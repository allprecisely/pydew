from pathlib import Path
from random import choice

import pygame

from settings import GROW_SPEED, LAYERS, PLANT_Y_OFFSET, SOIL_MAP, TILE_SIZE
from support import import_collections, import_folder, import_folder_dict


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


class Plant(pygame.sprite.Sprite):
    def __init__(self, groups, plant_type, soil, frames, check_watered):
        super().__init__(groups)
        self.plant_type = plant_type
        self.frames = frames
        self.soil = soil
        self.check_watered = check_watered

        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        self.image = self.frames[int(self.age)]
        self.rect = self.image.get_rect(
            midbottom=soil.rect.midbottom
            + pygame.math.Vector2(0, PLANT_Y_OFFSET[plant_type])
        )
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if int(self.age) > 0:
                self.z = LAYERS['main']
                if self.age >= self.max_age:
                    self.age = self.max_age
                    self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(
                midbottom=self.soil.rect.midbottom
                + pygame.math.Vector2(0, PLANT_Y_OFFSET[self.plant_type])
            )


class SoilLayer:
    def __init__(self, all_sprites, tmx_data) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        self.soil_surf = pygame.image.load(Path('assets', 'graphics', 'soil', 'o.png'))
        self.soil_surfs = import_folder_dict(Path('assets', 'graphics', 'soil'))
        self.water_surfs = import_folder(Path('assets', 'graphics', 'soil_water'))
        self.plant_surfs = import_collections(Path('assets', 'graphics', 'fruit'))

        self.create_soil_grid(tmx_data)
        self.create_hit_rects()

        # sounds
        self.hoe_sound = pygame.mixer.Sound(Path('assets', 'audio', 'hoe.wav'))
        self.hoe_sound.set_volume(0.1)
        self.watering = pygame.mixer.Sound(Path('assets', 'audio', 'water.mp3'))
        self.watering.set_volume(0.2)
        self.plant_sound = pygame.mixer.Sound(Path('assets', 'audio', 'plant.wav'))
        self.plant_sound.set_volume(0.2)

    def create_soil_grid(self, tmx_data):
        ground = pygame.image.load(Path('assets', 'graphics', 'world', 'ground.png'))
        h_tiles, v_tiles = (
            ground.get_width() // TILE_SIZE,
            ground.get_height() // TILE_SIZE,
        )

        self.grid = [[set() for _ in range(h_tiles)] for _ in range(v_tiles)]
        for x, y, _ in tmx_data.get_layer_by_name('Farmable').tiles():
            self.grid[y][x].add('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x, y = index_row * TILE_SIZE, index_col * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x, y = rect.x // TILE_SIZE, rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.hoe_sound.play()
                    self.grid[y][x].add('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:
                    tile_type = ''
                    for (x, y), letter in SOIL_MAP.items():
                        if 'X' in self.grid[index_row - y][index_col - x]:
                            tile_type += letter
                    SoilTile(
                        (index_col * TILE_SIZE, index_row * TILE_SIZE),
                        self.soil_surfs[tile_type or 'o'],
                        [self.all_sprites, self.soil_sprites],
                        LAYERS['soil'],
                    )

    def water(self, point):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(point):
                self.watering.play()
                x, y = soil_sprite.rect.x // TILE_SIZE, soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].add('W')
                SoilTile(
                    soil_sprite.rect.topleft,
                    choice(self.water_surfs),
                    [self.all_sprites, self.water_sprites],
                    LAYERS['soil water'],
                )

    def water_all(self):
        for soil_sprite in self.soil_sprites.sprites():
            x, y = soil_sprite.rect.x // TILE_SIZE, soil_sprite.rect.y // TILE_SIZE
            if not 'W' in self.grid[y][x]:
                self.grid[y][x].add('W')
                SoilTile(
                    soil_sprite.rect.topleft,
                    choice(self.water_surfs),
                    [self.all_sprites, self.water_sprites],
                    LAYERS['soil water'],
                )

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        for row in self.grid:
            for cell in row:
                cell.discard('W')

    def check_watered(self, pos):
        return 'W' in self.grid[pos[1] // TILE_SIZE][pos[0] // TILE_SIZE]

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x, y = soil_sprite.rect.x // TILE_SIZE, soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.plant_sound.play()
                    self.grid[y][x].add('P')
                    Plant(
                        [self.all_sprites, self.plant_sprites],
                        seed,
                        soil_sprite,
                        self.plant_surfs[seed],
                        self.check_watered,
                    )
