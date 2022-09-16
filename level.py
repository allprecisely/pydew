from pathlib import Path
from typing import Sequence, Union

import pygame
from pygame.sprite import Group, Sprite
from pytmx.util_pygame import load_pygame

from overlay import Overlay
from player import Player
from sprites import Generic
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.all_sprites = CameraGroup()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame(Path('assets', 'data', 'map.tmx'))

        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    self.all_sprites,
                    LAYERS['house bottom']
                )

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surf,
                    self.all_sprites,
                    LAYERS['house bottom']
                )

        Generic(
            pos=(0, 0),
            surf=pygame.image.load(Path('assets', 'graphics', 'world', 'ground.png')).convert_alpha(),
            groups = self.all_sprites,
            z = LAYERS['ground'],
        )
        self.player = Player(pos=(640, 360), group=self.all_sprites)

    def run(self, dt, events):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt, events)

        self.overlay.display()


class CameraGroup(Group):
    def __init__(self, *sprites: Union[Sprite, Sequence[Sprite]]) -> None:
        super().__init__(*sprites)
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)
