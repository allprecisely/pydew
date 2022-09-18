from pathlib import Path
import random
from typing import Sequence, Union

import pygame
from pygame.sprite import Group, Sprite
from pytmx.util_pygame import load_pygame

from overlay import Overlay
from player import Player
from settings import LAYERS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE, TMX_LAYERS
from sky import Rain
from soil import SoilLayer
from sprites import Generic, Interaction, Tree, Water
from support import import_folder
from transition import Transition


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        tmx_data = load_pygame(Path('assets', 'data', 'map.tmx'))
        ground_surf = pygame.image.load(
            Path('assets', 'graphics', 'world', 'ground.png')
        ).convert_alpha()
        self.soil_layer = SoilLayer(self.all_sprites, tmx_data)
        self.setup(tmx_data, ground_surf)
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)
        self.rain = Rain(self.all_sprites, ground_surf)
        self.raining = random.randint(0, 5) == 0
        self.soil_layer.raining = self.raining

    def setup(self, tmx_data, ground_surf):
        Generic((0, 0), ground_surf, self.all_sprites, LAYERS['ground'])

        for tmx, layers in TMX_LAYERS.items():
            for layer in layers:
                for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                    Generic(
                        (x * TILE_SIZE, y * TILE_SIZE),
                        surf,
                        self.all_sprites,
                        LAYERS[tmx],
                    )

        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                surf,
                [self.all_sprites, self.collision_sprites],
            )

        for obj in tmx_data.get_layer_by_name('Decoration'):
            Generic(
                (obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites]
            )

        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                (obj.x, obj.y),
                obj.image,
                [self.all_sprites, self.collision_sprites, self.tree_sprites],
                obj.name,
                player_add=self.player_add,
            )

        water_frames = import_folder(Path('assets', 'graphics', 'water'))
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water(
                (x * TILE_SIZE, y * TILE_SIZE),
                water_frames,
                self.all_sprites,
            )

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),
                self.collision_sprites,
            )

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.tree_sprites,
                    self.interaction_sprites,
                    self.soil_layer,
                )
            elif obj.name == 'Bed':
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    obj.name,
                )

    def player_add(self, item):
        self.player.item_inventory[item] += 1

    def reset(self):
        self.raining = random.randint(0, 5) == 0
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        else:
            self.soil_layer.remove_water()

        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def run(self, dt, events):
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt, events)

        self.overlay.display()

        if self.raining:
            self.rain.update()

        if self.player.sleep:
            self.transition.play(dt)


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
