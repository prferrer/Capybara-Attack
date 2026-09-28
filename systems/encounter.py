import random
import pygame


class Encounter:
    def __init__(self, encounter_type, x, y):
        self.type = encounter_type
        self.rect = pygame.Rect(x, y, 80, 80)
        self.active = True
        self.opened = False

        frame_counts = {
            "gold_chest": 4,
            "mystery_chest": 6,
            "healing_fountain": 5,
            "cursed_fountain": 5,
            "capy_statue": 6,
            "training_buddy": 3
        }

        self.images = []

        for i in range(1, frame_counts[encounter_type] + 1):
            image = pygame.image.load(
                f"assets/images/gameplay/{encounter_type}{i}.png"
            ).convert_alpha()

            image = pygame.transform.scale(
                image,
                (80, 80)
            )

            self.images.append(image)

        self.frame = 0
        self.timer = 0
        self.animation_speed = 8

    def update(self):
        if not self.active:
            return

        self.timer += 1

        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame = (
                self.frame + 1
            ) % len(self.images)

    def interact(self, player):
        if not self.active:
            return

        if self.type == "gold_chest":
            player.gold += random.randint(15, 30)
            self.active = False

        elif self.type == "mystery_chest":
            reward = random.choice([
                "gold",
                "heal",
                "attack"
            ])

            if reward == "gold":
                player.gold += random.randint(25, 50)

            elif reward == "heal":
                player.hp = min(
                    player.max_hp,
                    player.hp + 30
                )

            else:
                player.attack += 3

            self.active = False

        elif self.type == "healing_fountain":
            player.hp = min(
                player.max_hp,
                player.hp + int(player.max_hp * 0.35)
            )
            self.active = False

        elif self.type == "cursed_fountain":
            player.hp -= int(player.max_hp * 0.20)
            player.hp = max(player.hp, 1)
            player.gold += 40
            self.active = False

        elif self.type == "capy_statue":
            player.max_hp += 20
            player.hp += 20
            self.active = False

        elif self.type == "training_buddy":
            player.attack += 5
            self.active = False

    def draw(self, screen):
        if not self.active:
            return

        image = self.images[self.frame]

        screen.blit(
            image,
            self.rect
        )