from pathlib import Path
import sys

import pygame

from level import Level
from settings import SCREEN_HEIGHT, SCREEN_WIDTH


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Pydew Valley')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            dt = self.clock.tick() / 1000
            self.level.run(dt, events)
            pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
