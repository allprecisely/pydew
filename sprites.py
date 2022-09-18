from pathlib import Path
from random import choice, randint

import pygame

from settings import APPLE_POS, LAYERS
from timer import Timer


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75
        )


class Interaction(Generic):
    def __init__(self, pos, size, groups, name) -> None:
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name


class Water(Generic):
    def __init__(self, pos, frames, groups) -> None:
        self.frames = frames
        self.frame_index = 0

        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def update(self, dt, events):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]


class WildFlower(Generic):
    def __init__(self, pos, surf, groups, name) -> None:
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration=200) -> None:
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0, 0, 0))
        self.image = new_surf

    def update(self, dt, events):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups, name, player_add) -> None:
        super().__init__(pos, surf, groups)

        self.health = 5
        self.alive = 5
        self.stum_surf = pygame.image.load(
            Path('assets', 'graphics', 'stumps', f'{name.lower()}.png')
        ).convert_alpha()
        self.invul_timer = Timer(200)

        self.apple_surf = pygame.image.load(
            Path('assets', 'graphics', 'fruit', 'apple.png')
        ).convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

        # sounds
        self.axe_sound = pygame.mixer.Sound(Path('assets', 'audio', 'axe.mp3'))

    def damage(self):

        # play sound
        self.axe_sound.play()

        self.health -= 1
        if len(sprites := self.apple_sprites.sprites()) > 0:
            random_apple = choice(sprites)
            Particle(
                random_apple.rect.topleft,
                random_apple.image,
                self.groups()[0],
                LAYERS['fruit'],
            )
            random_apple.kill()
            self.player_add('apple')

    def check_death(self):
        if self.health <= 0:
            Particle(
                self.rect.topleft, self.image, self.groups()[0], LAYERS['fruit'], 300
            )
            self.image = self.stum_surf
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')

    def update(self, dt, events):
        if self.alive:
            self.check_death()

    def create_fruit(self):
        for x, y in self.apple_pos:
            if randint(0, 10) < 2:
                Generic(
                    (self.rect.left + x, self.rect.top + y),
                    self.apple_surf,
                    [self.apple_sprites, self.groups()[0]],
                    LAYERS['fruit'],
                )
