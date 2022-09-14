from pathlib import Path

import pygame

from settings import OVERLAY_POSITIONS


class Overlay:
    def __init__(self, player) -> None:
        self.display_surface = pygame.display.get_surface()
        self.player = player

        overlay_path = Path('assets', 'graphics', 'overlay')
        _load = lambda asset: pygame.image.load(overlay_path / f'{asset}.png').convert_alpha()
        self.tools_surf = {tool: _load(tool) for tool in player.tools}
        self.seeds_surf = {seed: _load(seed) for seed in player.seeds}

    def display(self):
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)
