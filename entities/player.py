import pygame

from settings import (
    PLAYER_SIZE,
    PLAYER_SPEED,
    ROOM_X,
    ROOM_Y,
    ROOM_WIDTH,
    ROOM_HEIGHT,
    TILE_SIZE
)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x,
            y,
            PLAYER_SIZE,
            PLAYER_SIZE
        )

        self.speed = PLAYER_SPEED
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.gold = 0
        self.inventory = []

        self.selected_skill = None
        self.skill_damage = 0
        self.skill_cooldown = 3000
        self.last_skill_use = -3000

        self.idle_image = pygame.image.load(
            "assets/images/idle1.png"
        ).convert_alpha()

        self.run_images = []

        for i in range(1, 6):
            image = pygame.image.load(
                f"assets/images/run{i}.png"
            ).convert_alpha()

            self.run_images.append(image)

        self.attack_right_images = []
        self.attack_left_images = []

        for i in range(1, 6):
            right_image = pygame.image.load(
                f"assets/images/attack_right{i}.png"
            ).convert_alpha()

            left_image = pygame.image.load(
                f"assets/images/attack_left{i}.png"
            ).convert_alpha()

            self.attack_right_images.append(right_image)
            self.attack_left_images.append(left_image)

        self.idle_image = pygame.transform.scale(
            self.idle_image,
            (PLAYER_SIZE, PLAYER_SIZE)
        )

        self.run_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.run_images
        ]

        self.attack_right_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.attack_right_images
        ]

        self.attack_left_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.attack_left_images
        ]

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False

    def update(self, walls):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing_right = False

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing_right = True

        self.is_moving = dx != 0 or dy != 0

        self.rect.x += dx
        self.rect.y += dy

        left_limit = ROOM_X
        right_limit = ROOM_X + ROOM_WIDTH
        top_limit = ROOM_Y
        bottom_limit = ROOM_Y + ROOM_HEIGHT

        self.rect.left = max(self.rect.left, left_limit)
        self.rect.right = min(self.rect.right, right_limit)

        self.rect.top = max(self.rect.top, top_limit)
        self.rect.bottom = min(self.rect.bottom, bottom_limit)

        if self.is_attacking:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1

                if self.current_frame >= 5:
                    self.current_frame = 0
                    self.is_attacking = False

        elif self.is_moving:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (
                    self.current_frame + 1
                ) % 5

        else:
            self.current_frame = 0
            self.animation_timer = 0

    def attack_enemy(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            self.animation_timer = 0

    def draw(self, screen):
        if self.is_attacking:
            if self.facing_right:
                image = self.attack_right_images[
                    self.current_frame
                ]
            else:
                image = self.attack_left_images[
                    self.current_frame
                ]

        elif self.is_moving:
            image = self.run_images[
                self.current_frame
            ]

            if not self.facing_right:
                image = pygame.transform.flip(
                    image,
                    True,
                    False
                )

        else:
            image = self.idle_image

            if not self.facing_right:
                image = pygame.transform.flip(
                    image,
                    True,
                    False
                )

        screen.blit(image, self.rect)