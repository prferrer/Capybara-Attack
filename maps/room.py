import pygame

from settings import (
    ROOM_WIDTH,
    ROOM_HEIGHT,
    ROOM_X,
    ROOM_Y
)


class Room:
    def __init__(self, map_number=1, map_type="normal"):
        self.map_number = map_number
        self.map_type = map_type
        self.walls = []

        if map_type == "cave":
            filename = f"assets/images/map/cave_map{map_number}.png"
        elif map_type == "snow":
            filename = f"assets/images/map/snow_map{map_number}.png"
        else:
            filename = f"assets/images/map/map{map_number}.png"

        self.map_image = pygame.image.load(
            filename
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