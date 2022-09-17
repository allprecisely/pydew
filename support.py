from pathlib import Path

import pygame


def import_folder(path: Path):
    surface_list = []
    for image in path.iterdir():
        image_surf = pygame.image.load(image).convert_alpha()
        surface_list.append(image_surf)
    return surface_list


def import_folder_dict(path: Path):
    return {f.stem: pygame.image.load(f).convert_alpha() for f in path.iterdir()}
