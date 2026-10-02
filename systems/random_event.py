import random
import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT
from systems.item import ITEM_DATA, give_item


SKILLS = [
    ("Fire", 35),
    ("Ice", 25),
    ("Lightning", 45)
]

EQUIPMENT = list(ITEM_DATA.keys())


RANDOM_EVENTS = [
    {
        "title": "Warrior's Heart",
        "description": "+20 ATK",
        "rarity": "COMMON",
        "effect": {"type": "attack", "value": 20}
    },
    {
        "title": "Iron Will",
        "description": "+15 DEF",
        "rarity": "COMMON",
        "effect": {"type": "defense", "value": 15}
    },
    {
        "title": "Vitality",
        "description": "+40 Max HP",
        "rarity": "COMMON",
        "effect": {"type": "max_hp", "value": 40}
    },
    {
        "title": "Gold Rush",
        "description": "+500 Gold",
        "rarity": "COMMON",
        "effect": {"type": "gold", "value": 500}
    },
    {
        "title": "Second Wind",
        "description": "Restore 50% HP",
        "rarity": "UNCOMMON",
        "effect": {"type": "heal_percent", "value": 0.50}
    },
    {
        "title": "Quick Hands",
        "description": "-500ms Skill Cooldown",
        "rarity": "UNCOMMON",
        "effect": {"type": "cooldown", "value": -500}
    },
    {
        "title": "Arcane Gift",
        "description": "+25 Skill Damage",
        "rarity": "UNCOMMON",
        "effect": {"type": "skill_damage", "value": 25}
    },
    {
        "title": "Treasure Hunter",
        "description": "Gain a random equipment",
        "rarity": "RARE",
        "effect": {"type": "random_equipment"}
    },
    {
        "title": "Iron Claw",
        "description": "Gain Iron Claw",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "iron_claw"
        }
    },
    {
        "title": "Iron Armor",
        "description": "Gain Iron Armor",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "iron_armor"
        }
    },
    {
        "title": "Heart Medallion",
        "description": "Gain Heart Medallion",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "heart_medallion"
        }
    },
    {
        "title": "Lucky Coin",
        "description": "Gain Lucky Coin",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "lucky_coin"
        }
    },
    {
        "title": "Stopwatch",
        "description": "Gain Stopwatch",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "stopwatch"
        }
    },
    {
        "title": "Spellbook",
        "description": "Gain Spellbook",
        "rarity": "RARE",
        "effect": {
            "type": "equipment",
            "item": "spellbook"
        }
    },
    {
        "title": "Ancient Training",
        "description": "+10 ATK and +10 DEF",
        "rarity": "RARE",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 10),
                ("defense", 10)
            ]
        }
    },
    {
        "title": "Blessing",
        "description": "+25 ATK and +25 Max HP",
        "rarity": "RARE",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 25),
                ("max_hp", 25)
            ]
        }
    },
    {
        "title": "Blood Pact",
        "description": "+50 ATK, lose 20% Max HP",
        "rarity": "LEGENDARY",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 50),
                ("max_hp_percent", -0.20)
            ]
        }
    },
    {
        "title": "Glass Cannon",
        "description": "+70 ATK, lose 35% Max HP",
        "rarity": "LEGENDARY",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 70),
                ("max_hp_percent", -0.35)
            ]
        }
    },
    {
        "title": "Desperate Strength",
        "description": "Lose 20% current HP, +45 ATK",
        "rarity": "LEGENDARY",
        "effect": {
            "type": "multi",
            "effects": [
                ("current_hp_percent", -0.20),
                ("attack", 45)
            ]
        }
    },
    {
        "title": "Heavy Armor",
        "description": "+35 DEF, +750ms Skill Cooldown",
        "rarity": "UNCOMMON",
        "effect": {
            "type": "multi",
            "effects": [
                ("defense", 35),
                ("cooldown", 750)
            ]
        }
    },
    {
        "title": "Overcharge",
        "description": "+45 Skill Damage, +1000ms Cooldown",
        "rarity": "RARE",
        "effect": {
            "type": "multi",
            "effects": [
                ("skill_damage", 45),
                ("cooldown", 1000)
            ]
        }
    },
    {
        "title": "Time Debt",
        "description": "+1500ms Skill Cooldown",
        "rarity": "CURSED",
        "effect": {
            "type": "cooldown",
            "value": 1500
        }
    },
    {
        "title": "Weakening Curse",
        "description": "-20 ATK",
        "rarity": "CURSED",
        "effect": {
            "type": "attack",
            "value": -20
        }
    },
    {
        "title": "Cracked Armor",
        "description": "-15 DEF",
        "rarity": "CURSED",
        "effect": {
            "type": "defense",
            "value": -15
        }
    },
    {
        "title": "Vital Drain",
        "description": "Lose 25% current HP",
        "rarity": "CURSED",
        "effect": {
            "type": "current_hp_percent",
            "value": -0.25
        }
    },
    {
        "title": "Greedy Tax",
        "description": "Lose 25% of your Gold",
        "rarity": "CURSED",
        "effect": {
            "type": "gold_percent",
            "value": -0.25
        }
    },
    {
        "title": "Broken Clock",
        "description": "+750ms Skill Cooldown",
        "rarity": "CURSED",
        "effect": {
            "type": "cooldown",
            "value": 750
        }
    },
    {
        "title": "Lucky Gamble",
        "description": "+30 ATK, lose 200 Gold",
        "rarity": "UNCOMMON",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 30),
                ("gold", -200)
            ]
        }
    },
    {
        "title": "Heart Exchange",
        "description": "-30 Max HP, +40 ATK",
        "rarity": "RARE",
        "effect": {
            "type": "multi",
            "effects": [
                ("max_hp", -30),
                ("attack", 40)
            ]
        }
    },
    {
        "title": "Fortified Body",
        "description": "+25 Max HP, +10 DEF",
        "rarity": "UNCOMMON",
        "effect": {
            "type": "multi",
            "effects": [
                ("max_hp", 25),
                ("defense", 10)
            ]
        }
    },
    {
        "title": "Power Surge",
        "description": "+30 ATK, +20 Skill Damage",
        "rarity": "RARE",
        "effect": {
            "type": "multi",
            "effects": [
                ("attack", 30),
                ("skill_damage", 20)
            ]
        }
    },
    {
        "title": "Arcane Debt",
        "description": "+60 Skill Damage, +1500ms Cooldown",
        "rarity": "LEGENDARY",
        "effect": {
            "type": "multi",
            "effects": [
                ("skill_damage", 60),
                ("cooldown", 1500)
            ]
        }
    },
    {
        "title": "Empty Pockets",
        "description": "Lose 500 Gold",
        "rarity": "CURSED",
        "effect": {
            "type": "gold",
            "value": -500
        }
    },
    {
        "title": "Mysterious Relic",
        "description": "Gain a random equipment",
        "rarity": "RARE",
        "effect": {"type": "random_equipment"}
    },
    {
        "title": "Arcane Lesson",
        "description": "Gain a random skill",
        "rarity": "RARE",
        "effect": {"type": "random_skill"}
    },
    {
        "title": "Skill Reforging",
        "description": "Replace your current skill",
        "rarity": "LEGENDARY",
        "effect": {"type": "replace_skill"}
    },
    {
        "title": "Fire Mastery",
        "description": "Gain Fire as your skill",
        "rarity": "RARE",
        "effect": {
            "type": "skill",
            "skill": "Fire",
            "damage": 35
        }
    },
    {
        "title": "Ice Mastery",
        "description": "Gain Ice as your skill",
        "rarity": "RARE",
        "effect": {
            "type": "skill",
            "skill": "Ice",
            "damage": 25
        }
    },
    {
        "title": "Lightning Mastery",
        "description": "Gain Lightning as your skill",
        "rarity": "RARE",
        "effect": {
            "type": "skill",
            "skill": "Lightning",
            "damage": 45
        }
    }
]


def wrap_text(font, text, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()

        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


def build_random_event_choices(player):
    valid = []

    for event in RANDOM_EVENTS:
        effect_type = event["effect"]["type"]

        if effect_type in (
            "equipment",
            "random_equipment"
        ):
            if len(player.inventory) >= player.inventory_slots:
                continue

        if (
            effect_type == "replace_skill"
            and player.selected_skill is None
        ):
            continue

        if effect_type == "skill":
            if event["effect"]["skill"] in [
                skill[0]
                for skill in player.skills
            ]:
                continue

            if len(player.skills) >= 3:
                continue

        if effect_type == "random_skill":
            available = [
                skill
                for skill, damage in SKILLS
                if skill not in [
                    owned[0]
                    for owned in player.skills
                ]
            ]

            if len(player.skills) >= 3:
                continue

            if not available:
                continue

        valid.append(event)

    return random.sample(
        valid,
        min(3, len(valid))
    )


def apply_random_event(player, event):
    effect = event["effect"]
    effect_type = effect["type"]

    if effect_type == "multi":
        for stat, value in effect["effects"]:
            apply_effect(
                player,
                {
                    "type": stat,
                    "value": value
                }
            )

        return

    if effect_type == "equipment":
        give_item(
            player,
            effect["item"]
        )
        return

    if effect_type == "random_equipment":
        give_item(
            player,
            random.choice(EQUIPMENT)
        )
        return

    if effect_type in (
        "random_skill",
        "replace_skill"
    ):
        choices = [
            skill
            for skill, damage in SKILLS
            if skill != player.selected_skill
        ]

        if choices:
            skill = random.choice(choices)

            damage = next(
                value
                for name, value in SKILLS
                if name == skill
            )

            player.add_skill(
                skill,
                damage
            )

        return

    if effect_type == "skill":
        player.add_skill(
            effect["skill"],
            effect["damage"]
        )
        return

    apply_effect(
        player,
        effect
    )


def apply_effect(player, effect):
    effect_type = effect["type"]
    value = effect["value"]

    if effect_type == "attack":
        player.increase_attack(value)

    elif effect_type == "defense":
        player.increase_defense(value)

    elif effect_type == "max_hp":
        if value >= 0:
            player.increase_max_hp(value)
        else:
            player.max_hp = max(
                1,
                player.max_hp + value
            )

            player.hp = min(
                player.hp,
                player.max_hp
            )

    elif effect_type == "max_hp_percent":
        old_max = player.max_hp

        new_max = max(
            1,
            int(old_max * (1 + value))
        )

        player.max_hp = min(
            300,
            new_max
        )

        player.hp = min(
            player.hp,
            player.max_hp
        )

    elif effect_type == "current_hp_percent":
        player.hp = max(
            1,
            int(player.hp * (1 + value))
        )

    elif effect_type == "gold":
        player.gold = max(
            0,
            min(
                9999,
                player.gold + value
            )
        )

    elif effect_type == "gold_percent":
        player.gold = max(
            0,
            int(player.gold * (1 + value))
        )

    elif effect_type == "heal_percent":
        player.hp = min(
            player.max_hp,
            player.hp + int(
                player.max_hp * value
            )
        )

    elif effect_type == "cooldown":
        player.skill_cooldown = max(
            500,
            player.skill_cooldown + value
        )

    elif effect_type == "skill_damage":
        player.skill_damage = max(
            0,
            player.skill_damage + value
        )


def draw_random_event(screen, font, choices):
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (5, 8, 18, 225)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title_font = pygame.font.Font(
        None,
        48
    )

    small_font = pygame.font.Font(
        None,
        22
    )

    card_font = pygame.font.Font(
        None,
        30
    )

    effect_font = pygame.font.Font(
        None,
        24
    )

    title = title_font.render(
        "CHOOSE ONE",
        True,
        COLOR_TEXT
    )

    screen.blit(
        title,
        (
            SCREEN_WIDTH // 2
            - title.get_width() // 2,
            35
        )
    )

    cards = []

    card_width = 220
    card_height = 455
    gap = 20

    start_x = (
        SCREEN_WIDTH
        - (card_width * 3 + gap * 2)
    ) // 2

    y = 105

    for index, event in enumerate(choices):
        rect = pygame.Rect(
            start_x + index * (card_width + gap),
            y,
            card_width,
            card_height
        )

        pygame.draw.rect(
            screen,
            (24, 47, 90),
            rect,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            (70, 130, 210),
            rect,
            3,
            border_radius=14
        )

        header = pygame.Rect(
            rect.x + 12,
            rect.y + 12,
            rect.width - 24,
            35
        )

        pygame.draw.rect(
            screen,
            (39, 70, 125),
            header,
            border_radius=8
        )

        rarity = small_font.render(
            event["rarity"],
            True,
            (220, 235, 255)
        )

        screen.blit(
            rarity,
            (
                header.centerx
                - rarity.get_width() // 2,
                header.centery
                - rarity.get_height() // 2
            )
        )

        icon_center = (
            rect.centerx,
            rect.y + 115
        )

        pygame.draw.circle(
            screen,
            (48, 84, 145),
            icon_center,
            55
        )

        pygame.draw.circle(
            screen,
            (110, 170, 235),
            icon_center,
            55,
            3
        )

        icon = card_font.render(
            "?",
            True,
            COLOR_TEXT
        )

        screen.blit(
            icon,
            (
                icon_center[0]
                - icon.get_width() // 2,
                icon_center[1]
                - icon.get_height() // 2
            )
        )

        title_lines = wrap_text(
            card_font,
            event["title"],
            card_width - 30
        )

        title_y = rect.y + 190

        for line in title_lines:
            text = card_font.render(
                line,
                True,
                COLOR_TEXT
            )

            screen.blit(
                text,
                (
                    rect.centerx
                    - text.get_width() // 2,
                    title_y
                )
            )

            title_y += 32

        desc_lines = wrap_text(
            font,
            event["description"],
            card_width - 35
        )

        desc_y = rect.y + 265

        for line in desc_lines:
            text = font.render(
                line,
                True,
                (205, 220, 245)
            )

            screen.blit(
                text,
                (
                    rect.centerx
                    - text.get_width() // 2,
                    desc_y
                )
            )

            desc_y += 30

        effect_box = pygame.Rect(
            rect.x + 15,
            rect.bottom - 80,
            rect.width - 30,
            55
        )

        pygame.draw.rect(
            screen,
            (17, 34, 68),
            effect_box,
            border_radius=8
        )

        choose = effect_font.render(
            "CHOOSE",
            True,
            (255, 230, 130)
        )

        screen.blit(
            choose,
            (
                effect_box.centerx
                - choose.get_width() // 2,
                effect_box.centery
                - choose.get_height() // 2
            )
        )

        cards.append(rect)

    return cards