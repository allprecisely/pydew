import pygame

from settings import LAYERS

# from settings import *


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z = LAYERS['main']) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z


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


class Tree(Generic):
    def __init__(self, pos, surf, groups, name) -> None:
        super().__init__(pos, surf, groups)

        self.name = name
