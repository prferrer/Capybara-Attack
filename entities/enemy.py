import math
import pygame

class Enemy:
    def __init__(self, x, y, enemy_type="orc", day=1):
        self.rect = pygame.Rect(x, y, 80, 80)
        self.x = float(x)
        self.y = float(y)
        self.enemy_type = enemy_type

        if enemy_type == "golem":
            self.hp = 70 + (day - 1) * 8
            self.attack = 4 + int((day - 1) * 0.5)
            self.speed = 1.0

        elif enemy_type == "yeti":
            self.hp = 35 + (day - 1) * 5
            self.attack = 8 + int((day - 1) * 0.7)
            self.speed = 2.2

        else:
            self.hp = 40 + (day - 1) * 6
            self.attack = 5 + int((day - 1) * 0.6)
            self.speed = 1.5

        self.max_hp = self.hp
        self.alive = True
        self.aggro_range = 150
        
        self.dead_sound = None
        
        if self.enemy_type == "orc":
            self.dead_sound = pygame.mixer.Sound("assets/audio/enemies/orc/orcdead.mp3") #boses orc
            
            self.dead_sound.set_volume(0.8)
        
        elif self.enemy_type == "golem":
            self.dead_sound = pygame.mixer.Sound("assets/audio/enemies/golem/golemdead.mp3") #nonchalant na bato

            self.dead_sound.set_volume(1.0)
        
        elif self.enemy_type == "yeti":
            self.dead_sound = pygame.mixer.Sound("assets/audio/enemies/yeti/yetidead.mp3") #oa na sigaw

            self.dead_sound.set_volume(0.9)

        if enemy_type == "golem":
            prefix = "golem"
        elif enemy_type == "yeti":
            prefix = "yeti"
        else:
            prefix = "orc"

        self.idle_image = pygame.image.load(
            f"assets/images/enemy/{prefix}_idle1.png"
        ).convert_alpha()

        self.attack_images = []
        self.right_attack_images = []
        self.left_attack_images = []
        self.right_run_images = []
        self.left_run_images = []

        for i in range(1, 6):
            if enemy_type == "orc":
                attack_image = pygame.image.load(
                    f"assets/images/enemy/orc_attack{i}.png"
                ).convert_alpha()

                self.attack_images.append(attack_image)

            else:
                right_attack = pygame.image.load(
                    f"assets/images/enemy/{prefix}_right_attack{i}.png"
                ).convert_alpha()

                left_attack = pygame.image.load(
                    f"assets/images/enemy/{prefix}_left_attack{i}.png"
                ).convert_alpha()

                self.right_attack_images.append(right_attack)
                self.left_attack_images.append(left_attack)

            right_run = pygame.image.load(
                f"assets/images/enemy/{prefix}_right_running{i}.png"
                if enemy_type != "orc"
                else f"assets/images/enemy/orc_right_run{i}.png"
            ).convert_alpha()

            left_run = pygame.image.load(
                f"assets/images/enemy/{prefix}_left_running{i}.png"
                if enemy_type != "orc"
                else f"assets/images/enemy/orc_left_run{i}.png"
            ).convert_alpha()

            self.right_run_images.append(right_run)
            self.left_run_images.append(left_run)

        self.idle_image = pygame.transform.scale(
            self.idle_image,
            (80, 80)
        )

        if self.attack_images:
            self.attack_images = [
                pygame.transform.scale(image, (80, 80))
                for image in self.attack_images
            ]

        self.right_attack_images = [
            pygame.transform.scale(image, (80, 80))
            for image in self.right_attack_images
        ]

        self.left_attack_images = [
            pygame.transform.scale(image, (80, 80))
            for image in self.left_attack_images
        ]

        self.right_run_images = [
            pygame.transform.scale(image, (80, 80))
            for image in self.right_run_images
        ]

        self.left_run_images = [
            pygame.transform.scale(image, (80, 80))
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

    def update(self, player):
        if not self.alive:
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.hypot(dx, dy)

        current_time = pygame.time.get_ticks()

        if distance > 90 and distance <= self.aggro_range:
            self.is_attacking = False
            self.is_moving = True

            if distance > 0:
                dx /= distance
                dy /= distance

            self.x += dx * self.speed
            self.y += dy * self.speed

            self.rect.x = round(self.x)
            self.rect.y = round(self.y)

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

        elif distance <= 90:
            self.is_moving = False
            self.is_attacking = True

            if dx > 0:
                self.facing_right = True
            elif dx < 0:
                self.facing_right = False

            if (
                current_time - self.last_attack_time
                >= self.attack_cooldown
            ):
                damage = max(
                    1,
                    self.attack - player.defense
                )

                if player.weapon_skill_invulnerable:
                    pass

                elif player.barrier_active:

                    self.take_damage(
                        damage
                    )

                    self.last_attack_time = current_time

                else:

                    player.hp -= damage
                    player.hit_sound.play()
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
                ) % 5

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

    def take_damage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            
            if self.dead_sound:
                self.dead_sound.play()

    def draw(self, screen):
        if not self.alive:
            return

        if self.is_attacking:
            if self.enemy_type == "orc":
                image = self.attack_images[self.current_frame]
            elif self.facing_right:
                image = self.right_attack_images[self.current_frame]
            else:
                image = self.left_attack_images[self.current_frame]

        elif self.is_moving:
            if self.facing_right:
                image = self.right_run_images[self.current_frame]
            else:
                image = self.left_run_images[self.current_frame]

        else:
            image = self.idle_image

        screen.blit(image, self.rect)

        health_width = 80
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