from pathlib import Path

import pygame


def import_folder(path: Path):
    return [pygame.image.load(f).convert_alpha() for f in sorted(path.iterdir())]


def import_folder_dict(path: Path):
    return {f.stem: pygame.image.load(f).convert_alpha() for f in path.iterdir()}


def import_collections(path: Path):
    return {
        _path.stem: import_folder(_path) for _path in path.iterdir() if _path.is_dir()
    }
