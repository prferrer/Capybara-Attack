import pygame


ITEM_DATA = {
    "iron_claw": {
        "name": "Iron Claw",
        "stat": "attack",
        "value": 2
    },
    "iron_armor": {
        "name": "Iron Armor",
        "stat": "defense",
        "value": 2
    },
    "heart_medallion": {
        "name": "Heart Medallion",
        "stat": "max_hp",
        "value": 10
    },
    "lucky_coin": {
        "name": "Lucky Coin",
        "stat": "gold_multiplier",
        "value": 0.10
    },
    "stopwatch": {
        "name": "Stopwatch",
        "stat": "cooldown",
        "value": 250
    },
    "spellbook": {
        "name": "Spellbook",
        "stat": "skill_damage",
        "value": 5
    }
}


class ItemPickup:
    def __init__(self, item_type, x, y):
        self.type = item_type
        self.data = ITEM_DATA[item_type]

        image = pygame.image.load(
            f"assets/images/gameplay/{item_type}.png"
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

        player.inventory.append(self.type)

        stat = self.data["stat"]
        value = self.data["value"]

        if stat == "attack":
            player.attack += value

        elif stat == "defense":
            player.defense += value

        elif stat == "max_hp":
            player.max_hp += value
            player.hp += value

        elif stat == "gold_multiplier":
            player.gold_multiplier += value

        elif stat == "cooldown":
            player.skill_cooldown = max(
                500,
                player.skill_cooldown - value
            )

        elif stat == "skill_damage":
            player.skill_damage += value

        self.active = False
        return True

    def draw(self, screen):
        if self.active:
            screen.blit(
                self.image,
                self.rect
            )