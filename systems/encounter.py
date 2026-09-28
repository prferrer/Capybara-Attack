import random
import pygame


class Encounter:
    def __init__(self, encounter_type, x, y):
        self.type = encounter_type
        self.active = True
        self.interacting = False
        self.finished = False

        frame_counts = {
            "gold_chest": 4,
            "mystery_chest": 6,
            "healing_fountain": 5,
            "cursed_fountain": 5,
            "capy_statue": 5,
            "training_buddy": 3,
            "merchant": 3
        }

        sizes = {
            "gold_chest": (55, 55),
            "mystery_chest": (55, 55),
            "healing_fountain": (80, 80),
            "cursed_fountain": (80, 80),
            "capy_statue": (65, 65),
            "training_buddy": (60, 60),
            "merchant": (80, 80)
        }

        self.images = []

        for i in range(1, frame_counts[encounter_type] + 1):
            image = pygame.image.load(
                f"assets/images/gameplay/{encounter_type}{i}.png"
            ).convert_alpha()

            image = pygame.transform.scale(
                image,
                sizes[encounter_type]
            )

            self.images.append(image)

        self.frame = 0
        self.timer = 0
        self.animation_speed = 18

        self.image = self.images[0]

        if encounter_type == "merchant":
            self.frame = random.randint(0, 2)
            self.image = self.images[self.frame]

        self.rect = self.image.get_rect(
            center=(x + 40, y + 40)
        )

    def update(self):
        if not self.active:
            return

        if not self.interacting:
            return

        self.timer += 1

        if self.timer >= self.animation_speed:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.frame = len(self.images) - 1
                self.interacting = False
                self.finished = True

            self.image = self.images[self.frame]

    def interact(self, player):
        if not self.active or self.interacting:
            return

        if self.type in [
            "gold_chest",
            "mystery_chest",
            "capy_statue"
        ]:
            self.interacting = True
            self.frame = 1
            self.timer = 0
            self.image = self.images[self.frame]
            return

        if self.type == "healing_fountain":
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

        elif self.type == "training_buddy":
            player.attack += 5
            self.active = False

        elif self.type == "merchant":
            pass

    def complete_reward(self, player):
        if not self.finished:
            return

        if self.type == "gold_chest":
            player.gold += random.randint(15, 30)

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

        elif self.type == "capy_statue":
            player.max_hp += 20
            player.hp += 20

        self.active = False

    def draw(self, screen):
        if not self.active:
            return

        screen.blit(
            self.image,
            self.rect
        )