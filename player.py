from pathlib import Path

import pygame

from settings import LAYERS, PLAYER_TOOL_OFFSET
from support import import_folder
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        group,
        collision_sprites,
        tree_sprites,
        interaction_sprites,
        soil_layer,
    ):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        self.timers = {
            'tool_use': Timer(350, self.use_tool),
            'seed_use': Timer(350, self.use_seed),
        }

        self.tools = ['axe', 'water', 'hoe']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0,
        }

        self.hitbox = self.rect.copy().inflate(-126, -70)
        self.collision_sprites = collision_sprites

        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.soil_layer = soil_layer

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        elif self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        elif self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)

    def get_target_position(self):
        self.target_pos = (
            self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        )

    def use_seed(self):
        pass

    def import_assets(self):
        self.animations = {
            'up': [],
            'down': [],
            'left': [],
            'right': [],
            'up_idle': [],
            'down_idle': [],
            'left_idle': [],
            'right_idle': [],
            'up_axe': [],
            'down_axe': [],
            'left_axe': [],
            'right_axe': [],
            'up_water': [],
            'down_water': [],
            'left_water': [],
            'right_water': [],
            'up_hoe': [],
            'down_hoe': [],
            'left_hoe': [],
            'right_hoe': [],
        }

        for animation in self.animations:
            full_path = Path('assets', 'graphics', 'character', animation)
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self, events):
        keys = pygame.key.get_pressed()

        if not any(t.active for t in self.timers.values()) and not self.sleep:
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE]:
                self.timers['tool_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_LCTRL]:
                self.timers['seed_use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(
                    self, self.interaction_sprites, False
                )
                if collided_interaction_sprite:
                    if (
                        collided_sprite_name := collided_interaction_sprite[0].name
                    ) == 'Trader':
                        pass
                    elif collided_sprite_name == 'Bed':
                        self.status = 'left_idle'
                        self.sleep = True

            for event in events:
                if event.type == pygame.KEYUP and event.key == pygame.K_q:
                    self.tool_index = (self.tool_index + 1) % len(self.tools)
                    self.selected_tool = self.tools[self.tool_index]

                if event.type == pygame.KEYUP and event.key == pygame.K_e:
                    self.seed_index = (self.seed_index + 1) % len(self.seeds)
                    self.selected_seed = self.seeds[self.seed_index]

    def get_status(self):
        if self.timers['tool_use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
            return

        if not any(pygame.key.get_pressed()):
            self.status = self.status.split('_')[0] + '_idle'

    def collisions(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hitbox := getattr(sprite, 'hitbox'):
                if hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collisions('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collisions('vertical')

    def update(self, dt, events):
        self.get_target_position()
        self.input(events)
        self.get_status()
        for timer in self.timers.values():
            timer.update()

        self.move(dt)
        self.animate(dt)
