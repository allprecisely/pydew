from pathlib import Path

import pygame

from player import Player
from settings import PURCHASE_PRICES, SALE_PRICES, SCREEN_HEIGHT, SCREEN_WIDTH


class Menu:
    def __init__(self, player: Player, toggle_menu) -> None:
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surf = pygame.display.get_surface()
        self.font = pygame.font.Font(Path('assets', 'font', 'LycheeSoda.ttf'), 30)

        # options
        self.width = 400
        self.space = 10
        self.padding = 8

        # entries
        self.options = list(self.player.item_inventory) + list(
            self.player.seed_inventory
        )
        self.sell_border = len(self.player.item_inventory) - 1

        # movement
        self.index = 0

        self.setup()

    def setup(self):
        # create the text surfaces
        self.text_surfs = [
            self.font.render(item, False, 'Black') for item in self.options
        ]
        self.total_height = (
            sum(surf.get_height() for surf in self.text_surfs)
            + (self.padding * 2 + self.space) * len(self.text_surfs)
            - self.space
        )
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(
            SCREEN_WIDTH / 2 - self.width / 2,
            self.menu_top,
            self.width,
            self.total_height,
        )

        # but/sell surf
        self.buy_text = self.font.render('buy', False, 'Black')
        self.sell_text = self.font.render('sell', False, 'Black')

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surf, 'White', text_rect.inflate(10, 10), 0, 4)
        self.display_surf.blit(text_surf, text_rect)

    def input(self, events):
        for event in events:
            if event.type != pygame.KEYUP:
                continue
            if event.key == pygame.K_RETURN:
                self.toggle_menu()
            elif event.key == pygame.K_UP:
                self.index -= 1
                if self.index < 0:
                    self.index = len(self.options) - 1
            elif event.key == pygame.K_DOWN:
                self.index += 1
                if self.index >= len(self.options):
                    self.index = 0
            elif event.key == pygame.K_SPACE:
                current_item = self.options[self.index]
                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                    if self.player.money >= PURCHASE_PRICES[current_item]:
                        self.player.seed_inventory[current_item] += 1
                        self.player.money -= PURCHASE_PRICES[current_item]

    def show_entry(self, text_surf, amount, top, selected):
        # background
        bg_rect = pygame.Rect(
            self.main_rect.left,
            top,
            self.width,
            text_surf.get_height() + self.padding * 2,
        )
        pygame.draw.rect(self.display_surf, 'White', bg_rect, 0, 4)

        # text
        text_rect = text_surf.get_rect(
            midleft=(self.main_rect.left + self.space, bg_rect.centery)
        )
        self.display_surf.blit(text_surf, text_rect)

        # amount
        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(
            midright=(self.main_rect.right - self.space, bg_rect.centery)
        )
        self.display_surf.blit(amount_surf, amount_rect)

        # selected
        if selected:
            pygame.draw.rect(self.display_surf, 'black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                pos_rect = self.sell_text.get_rect(
                    midleft=(self.main_rect.left + 150, bg_rect.centery)
                )
                self.display_surf.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(
                    midleft=(self.main_rect.left + 150, bg_rect.centery)
                )
                self.display_surf.blit(self.buy_text, pos_rect)

    def update(self, events):
        self.input(events)
        self.display_money()

        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (
                text_surf.get_height() + (self.padding * 2) + self.space
            )
            amount_list = list(self.player.item_inventory.values()) + list(
                self.player.seed_inventory.values()
            )
            self.show_entry(
                text_surf, amount_list[text_index], top, self.index == text_index
            )
