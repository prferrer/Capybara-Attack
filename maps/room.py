
import pygame

from settings import (
    ROOM_WIDTH,
    ROOM_HEIGHT,
    ROOM_X,
    ROOM_Y
)


class Room:
    def __init__(self, map_number=1):
        self.map_number = map_number
        self.walls = []

        self.map_image = pygame.image.load(
            f"assets/images/map{map_number}.png"
        ).convert()

        self.map_image = pygame.transform.scale(
            self.map_image,
            (ROOM_WIDTH, ROOM_HEIGHT)
        )

    def draw(self, screen):
        screen.blit(
            self.map_image,
            (ROOM_X, ROOM_Y)
        )