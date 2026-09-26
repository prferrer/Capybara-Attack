import math
import pygame

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y,80,80)

        self.hp = 40
        self.max_hp = 40
        self.attack = 5
        self.alive = True

        self.idle_image = pygame.image.load(
            "assets/images/orc_idle1.png"
        ).convert_alpha()

        self.attack_images = []
        self.right_run_images = []
        self.left_run_images = []

        for i in range(1, 6):
            attack_image = pygame.image.load(
                f"assets/images/orc_attack{i}.png"
            ).convert_alpha()

            right_image = pygame.image.load(
                f"assets/images/orc_right_run{i}.png"
            ).convert_alpha()

            left_image = pygame.image.load(
                f"assets/images/orc_left_run{i}.png"
            ).convert_alpha()

            self.attack_images.append(attack_image)
            self.right_run_images.append(right_image)
            self.left_run_images.append(left_image)

        self.idle_image = pygame.transform.scale(
            self.idle_image,
            (80,80)
        )

        self.attack_images = [
            pygame.transform.scale(image, (80,80))
            for image in self.attack_images
        ]

        self.right_run_images = [
            pygame.transform.scale(image, (80,80))
            for image in self.right_run_images
        ]

        self.left_run_images = [
            pygame.transform.scale(image, (80,80))
            for image in self.left_run_images
        ]

        self.is_attacking = False
        self.is_moving = False
        self.facing_right = True

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.last_attack_time = 0
        self.attack_cooldown = 1000

        self.speed = 1.5

    def update(self, player):
        if not self.alive:
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.hypot(dx, dy)

        current_time = pygame.time.get_ticks()

        if distance > 90 and distance < 350:
            self.is_attacking = False
            self.is_moving = True

            if distance > 0:
                dx /= distance
                dy /= distance

            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

        elif distance <= 90:
            self.is_moving = False
            self.is_attacking = True

            if (
                current_time - self.last_attack_time
                >= self.attack_cooldown
            ):
                damage = max(
                    1,
                    self.attack - player.defense
                )

                player.hp -= damage
                self.last_attack_time = current_time

        else:
            self.is_moving = False
            self.is_attacking = False

        if self.is_attacking:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (
                    self.current_frame + 1
                ) % len(self.attack_images)

        elif self.is_moving:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (
                    self.current_frame + 1
                ) % len(self.right_run_images)

        else:
            self.current_frame = 0
            self.animation_timer = 0

    def take_damage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, screen):
        if not self.alive:
            return

        if self.is_attacking:
            image = self.attack_images[self.current_frame]

        elif self.is_moving:
            if self.facing_right:
                image = self.right_run_images[
                    self.current_frame
                ]
            else:
                image = self.left_run_images[
                    self.current_frame
                ]

        else:
            image = self.idle_image

        screen.blit(image, self.rect)

        health_width =80
        health_ratio = self.hp / self.max_hp

        pygame.draw.rect(
            screen,
            (100, 30, 30),
            (
                self.rect.x,
                self.rect.y - 8,
                health_width,
                5
            )
        )

        pygame.draw.rect(
            screen,
            (40, 200, 60),
            (
                self.rect.x,
                self.rect.y - 8,
                int(health_width * health_ratio),
                5
            )
        )