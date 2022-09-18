from pathlib import Path
from random import choice, randint

import pygame

from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH
from sprites import Generic
from support import import_folder


class Sky:
    def __init__(self) -> None:
        self.display_surf = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_color = [255, 255, 255]
        self.end_color = [38, 101, 189 ]
    
    def display(self, dt):
        for index, color in enumerate(self.end_color):
            if self.start_color[index] > color:
                self.start_color[index] -= 2 * dt
        self.full_surf.fill(self.start_color)
        self.display_surf.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


class Drop(Generic):
    def __init__(self, pos, surf, groups, z, moving) -> None:
        super().__init__(pos, surf, groups, z)

        self.lifetime = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt, events):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:
    def __init__(self, all_sprites, ground_surf) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder(Path('assets', 'graphics', 'rain', 'drops'))
        self.rain_floor = import_folder(Path('assets', 'graphics', 'rain', 'floor'))
        self.floor_w, self.floor_h = ground_surf.get_size()

    def create_floor(self):
        Drop(
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            choice(self.rain_floor),
            self.all_sprites,
            LAYERS['rain floor'],
            False,
        )

    def create_drops(self):
        Drop(
            (randint(0, self.floor_w), randint(0, self.floor_h)),
            choice(self.rain_drops),
            self.all_sprites,
            LAYERS['rain drops'],
            True,
        )

    def update(self):
        self.create_floor()
        self.create_drops()
