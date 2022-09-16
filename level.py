from pathlib import Path
from typing import Sequence, Union

import pygame
from pygame.sprite import Group, Sprite
from pytmx.util_pygame import load_pygame

from overlay import Overlay
from player import Player
from sprites import Generic, Tree, Water
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, TMX_LAYERS
from support import import_folder


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.all_sprites = CameraGroup()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame(Path('assets', 'data', 'map.tmx'))

        Generic(
            pos=(0, 0),
            surf=pygame.image.load(
                Path('assets', 'graphics', 'world', 'ground.png')
            ).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground'],
        )

        for tmx, layers in TMX_LAYERS.items():
            for layer in layers:
                for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                    Generic(
                        (x * TILE_SIZE, y * TILE_SIZE),
                        surf,
                        self.all_sprites,
                        LAYERS[tmx],
                    )

        for obj in tmx_data.get_layer_by_name('Decoration'):
            Generic((obj.x, obj.y), obj.image, self.all_sprites)

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, self.all_sprites, obj.name)

        water_frames = import_folder(Path('assets', 'graphics', 'water'))
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water(
                (x * TILE_SIZE, y * TILE_SIZE),
                water_frames,
                self.all_sprites,
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

        for sprite in sorted(
            self.sprites(), key=lambda sprite: (sprite.z, sprite.rect.centery)
        ):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.display_surface.blit(sprite.image, offset_rect)
