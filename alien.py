import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen

        # load alien image
        # load and resize alien image
        self.image = pygame.image.load("images/alien.bmp")
        self.image = pygame.transform.scale(self.image, (50, 50))  # resize to 50x50
        self.rect = self.image.get_rect()

        # start near top left
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        self.x = float(self.rect.x)
