import random
import pygame

from systems.item import ITEM_DATA, ItemPickup

class Encounter:
    def __init__(self, encounter_type, x, y):
        self.type = encounter_type
        self.active = True
        self.interacting = False
        self.finished = False
        
        self.gold_chest_sound = None
        self.mystery_chest_sound = None
        
        if encounter_type == "gold_chest":
            self.gold_chest_sound = pygame.mixer.Sound("assets/audio/misc/chest/goldchest.mp3")#gold_chest sound
            self.gold_chest_sound.set_volume(0.6)
            
        elif encounter_type == "mystery_chest":
            self.mystery_chest_sound = pygame.mixer.Sound("assets/audio/misc/chest/mysterychest.mp3")#mystery_chest sound
            self.mystery_chest_sound.set_volume(0.6)
        
        self.healing_fountain_sound = None
        self.cursed_fountain_sound = None
        
        if encounter_type == "healing_fountain":
            self.healing_fountain_sound = pygame.mixer.Sound("assets/audio/misc/fountain/healing_fountain.mp3")
            self.healing_fountain_sound.set_volume(0.6)
            
        elif encounter_type == "cursed_fountain":
            self.cursed_fountain_sound = pygame.mixer.Sound("assets/audio/misc/fountain/cursed_fountain.mp3")
            self.cursed_fountain_sound.set_volume(0.6)
        
        self.capy_statue_sound = None
        self.training_buddy_sound = None
        
        if encounter_type == "capy_statue":
            self.capy_statue_sound = pygame.mixer.Sound("assets/audio/misc/statue/capystatue.mp3")
            self.capy_statue_sound.set_volume(0.6)
            
        elif encounter_type == "training_buddy":
            self.training_buddy_sound = pygame.mixer.Sound("assets/audio/misc/trainingbuddy/training_buddy.mp3")
            self.training_buddy_sound.set_volume(0.6)
        
        self.shop_items = [
            ("iron_claw", 50),
            ("iron_armor", 50),
            ("spellbook", 80)
        ]

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
            
            if self.type == "gold_chest" and self.gold_chest_sound:
                self.gold_chest_sound.play()
            elif self.type == "mystery_chest" and self.mystery_chest_sound:
                self.mystery_chest_sound.play()
            elif self.type == "capy_statue" and self.capy_statue_sound:
                self.capy_statue_sound.play()
                
            return

        if self.type == "healing_fountain":
            if self.healing_fountain_sound:
                self.healing_fountain_sound.play()
                
            player.hp = min(
                player.max_hp,
                player.hp + int(player.max_hp * 0.35)
            )
            self.active = False

        elif self.type == "cursed_fountain":
            if self.cursed_fountain_sound:
                self.cursed_fountain_sound.play()
                
            player.hp -= int(player.max_hp * 0.20)
            player.hp = max(player.hp, 1)
            player.add_gold(40)
            self.active = False

        elif self.type == "training_buddy":
            if self.training_buddy_sound:
                self.training_buddy_sound.play()
                
            player.increase_attack(5)
            self.active = False

        elif self.type == "merchant":
            pass

    def complete_reward(self, player, items):
        if not self.finished:
            return

        if self.type == "gold_chest":
            player.add_gold(
                random.randint(15, 30)
            )

        elif self.type == "mystery_chest":
            reward = random.choice([
                "gold",
                "heal",
                "attack",
                "item",
                "potion"
            ])

            if reward == "gold":
                player.add_gold(
                    random.randint(25, 50)
                )

            elif reward == "heal":
                player.hp = min(
                    player.max_hp,
                    player.hp + 30
                )

            elif reward == "attack":
                player.increase_attack(3)

            elif reward == "item":
                item_type = random.choice([
                    "iron_claw",
                    "iron_armor",
                    "heart_medallion",
                    "lucky_coin",
                    "stopwatch",
                    "spellbook"
                ])

                items.append(
                    ItemPickup(
                        item_type,
                        self.rect.centerx,
                        self.rect.centery
                    )
                )

            elif reward == "potion":
                potion_type = random.choice([
                    "attack_potion",
                    "health_potion",
                    "skill_potion"
                ])

                items.append(
                    ItemPickup(
                        potion_type,
                        self.rect.centerx,
                        self.rect.centery
                    )
                )

        elif self.type == "capy_statue":
            player.increase_max_hp(20)

        self.active = False
        self.finished = False
            
    def draw(self, screen):
        if not self.active:
            return

        screen.blit(
            self.image,
            self.rect
        )