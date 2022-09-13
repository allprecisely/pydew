from pathlib import Path

import pygame

def import_folder(path: Path):
    surface_list = []
    for image in path.iterdir():
        image_surf = pygame.image.load(image).convert_alpha()
        surface_list.append(image_surf)
    return surface_list