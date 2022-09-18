from pathlib import Path
from random import choice

import pygame

from settings import LAYERS, SOIL_MAP, TILE_SIZE
from support import import_folder, import_folder_dict


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z


class SoilLayer:
    def __init__(self, all_sprites, tmx_data) -> None:
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        self.soil_surf = pygame.image.load(Path('assets', 'graphics', 'soil', 'o.png'))
        self.soil_surfs = import_folder_dict(Path('assets', 'graphics', 'soil'))
        self.water_surfs = import_folder(Path('assets', 'graphics', 'soil_water'))

        self.create_soil_grid(tmx_data)
        self.create_hit_rects()

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
