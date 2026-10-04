import pygame


ITEM_DATA = {
    "iron_claw": {
        "name": "Iron Claw",
        "stat": "attack",
        "value": 2,
        "consumable": False
    },
    "iron_armor": {
        "name": "Iron Armor",
        "stat": "defense",
        "value": 2,
        "consumable": False
    },
    "heart_medallion": {
        "name": "Heart Medallion",
        "stat": "max_hp",
        "value": 10,
        "consumable": False
    },
    "lucky_coin": {
        "name": "Lucky Coin",
        "stat": "gold_multiplier",
        "value": 0.10,
        "consumable": False
    },
    "stopwatch": {
        "name": "Stopwatch",
        "stat": "cooldown",
        "value": 250,
        "consumable": False
    },
    "spellbook": {
        "name": "Spellbook",
        "stat": "skill_damage",
        "value": 5,
        "consumable": False
    },
    "attack_potion": {
        "name": "Attack Potion",
        "stat": "attack_potion",
        "value": 25,
        "consumable": True
    },
    "skill_potion": {
        "name": "Skill Potion",
        "stat": "skill_potion",
        "value": 25,
        "consumable": True
    },
    "health_potion": {
        "name": "Health Potion",
        "stat": "health_potion",
        "value": 100,
        "consumable": True
    }
}


def give_item(player, item_type):
    if len(player.inventory) >= player.inventory_slots:
        return False

    player.inventory.append(item_type)

    data = ITEM_DATA[item_type]
    stat = data["stat"]
    value = data["value"]

    if data["consumable"]:
        return True

    if stat == "attack":
        player.increase_attack(value)

    elif stat == "defense":
        player.increase_defense(value)

    elif stat == "max_hp":
        player.increase_max_hp(value)

    elif stat == "gold_multiplier":
        player.gold_multiplier += value

    elif stat == "cooldown":
        player.skill_cooldown_reduction += value

    elif stat == "skill_damage":
        player.skill_damage += value

    return True


def consume_item(player, item_type):
    if item_type not in player.inventory:
        return False

    data = ITEM_DATA[item_type]

    if not data["consumable"]:
        return False

    player.inventory.remove(item_type)

    stat = data["stat"]
    value = data["value"]
    
    drink_sound = pygame.mixer.Sound("assets/audio/potion/drinkpotion.mp3")
    drink_sound.set_volume(0.6)
    drink_sound.play()

    if stat == "attack_potion":
        player.increase_attack(value)

    elif stat == "skill_potion":
        player.skill_damage += value

    elif stat == "health_potion":
        player.hp = player.max_hp

    return True


def remove_item(player, item_type):
    if item_type not in player.inventory:
        return False

    player.inventory.remove(item_type)

    drop_sound = pygame.mixer.Sound("assets/audio/droppick/dropitem.mp3")
    drop_sound.set_volume(0.8)
    drop_sound.play()
    
    data = ITEM_DATA[item_type]
    stat = data["stat"]
    value = data["value"]

    if data["consumable"]:
        return True

    if stat == "attack":
        player.attack = max(
            0,
            player.attack - value
        )

    elif stat == "defense":
        player.defense = max(
            0,
            player.defense - value
        )

    elif stat == "max_hp":
        player.max_hp = max(
            1,
            player.max_hp - value
        )

        player.hp = min(
            player.hp,
            player.max_hp
        )

    elif stat == "gold_multiplier":
        player.gold_multiplier = max(
            1.0,
            player.gold_multiplier - value
        )

    elif stat == "cooldown":
        player.skill_cooldown_reduction -= value

    elif stat == "skill_damage":
        player.skill_damage = max(
            0,
            player.skill_damage - value
        )

    return True


class ItemPickup:
    def __init__(self, item_type, x, y):
        self.type = item_type
        self.data = ITEM_DATA[item_type]

        if item_type in [
            "attack_potion",
            "health_potion",
            "skill_potion"
        ]:
            image_path = (
                f"assets/images/player/{item_type}.png"
            )
        else:
            image_path = (
                f"assets/images/gameplay/{item_type}.png"
            )

        image = pygame.image.load(
            image_path
        ).convert_alpha()

        image = pygame.transform.scale(
            image,
            (45, 45)
        )

        self.image = image
        self.rect = image.get_rect(
            center=(x, y)
        )

        self.active = True

    def collect(self, player):
        if not self.active:
            return False

        if len(player.inventory) >= player.inventory_slots:
            return False

        if give_item(player, self.type):
            self.active = False
            
            pickup_sound = pygame.mixer.Sound("assets/audio/droppick/pickupitem.MP3")
            pickup_sound.set_volume(0.6)
            pickup_sound.play()
            
            return True

        return False

    def draw(self, screen):
        if self.active:
            screen.blit(
                self.image,
                self.rect
            )


class HeartPickup:
    def __init__(self, x, y):
        self.type = "heart"
        self.active = True

        self.images = []

        for i in range(1, 4):
            image = pygame.image.load(
                f"assets/images/player/heart{i}.png"
            ).convert_alpha()

            image = pygame.transform.scale(
                image,
                (45, 45)
            )

            self.images.append(image)

        self.frame = 0
        self.timer = 0
        self.animation_speed = 10

        self.image = self.images[0]

        self.rect = self.image.get_rect(
            center=(x, y)
        )

    def update(self):
        if not self.active:
            return

        self.timer += 1

        if self.timer >= self.animation_speed:
            self.timer = 0

            self.frame = (
                self.frame + 1
            ) % len(self.images)

            self.image = self.images[self.frame]

    def collect(self, player):
        if not self.active:
            return False

        if player.hp >= player.max_hp:
            return False

        heal_amount = max(
            1,
            int(player.max_hp * 0.25)
        )

        player.hp = min(
            player.max_hp,
            player.hp + heal_amount
        )

        self.active = False

        return True

    def draw(self, screen):
        if self.active:
            screen.blit(
                self.image,
                self.rect
            )
            
    