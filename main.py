import random
import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GAME_TITLE,
    COLOR_BACKGROUND,
    COLOR_TEXT,
    ROOM_X,
    ROOM_Y
)

from entities.player import Player
from entities.enemy import Enemy
from maps.room import Room
from systems.game_manager import GameManager
from systems.skill import SkillEffect
from systems.start_screen import run_start_screen
from systems.encounter import Encounter
from systems.item import (
    ItemPickup,
    HeartPickup,
    ITEM_DATA,
    give_item,
    remove_item,
    consume_item
)


def get_map_info(day):
    cycle_day = ((day - 1) % 15) + 1

    if cycle_day <= 5:
        return "normal", cycle_day

    if cycle_day <= 10:
        return "cave", cycle_day - 5

    return "snow", cycle_day - 10


def create_enemies(map_type, day):
    if map_type == "cave":
        enemy_type = "golem"
    elif map_type == "snow":
        enemy_type = "yeti"
    else:
        enemy_type = "orc"

    if day <= 5:
        enemy_count = 2
    elif day <= 10:
        enemy_count = 3
    elif day <= 15:
        enemy_count = 4
    elif day <= 20:
        enemy_count = 5
    elif day <= 30:
        enemy_count = 6
    elif day <= 40:
        enemy_count = 7
    else:
        enemy_count = 8

    positions = [
        (ROOM_X + 350, ROOM_Y + 200),
        (ROOM_X + 550, ROOM_Y + 350),
        (ROOM_X + 200, ROOM_Y + 400),
        (ROOM_X + 650, ROOM_Y + 150),
        (ROOM_X + 400, ROOM_Y + 450),
        (ROOM_X + 150, ROOM_Y + 150),
        (ROOM_X + 700, ROOM_Y + 400),
        (ROOM_X + 500, ROOM_Y + 100)
    ]

    return [
        Enemy(x, y, enemy_type, day)
        for x, y in positions[:enemy_count]
    ]


def create_encounter():
    encounter_type = random.choices(
        [
            "gold_chest",
            "mystery_chest",
            "healing_fountain",
            "cursed_fountain",
            "capy_statue",
            "training_buddy",
            "merchant"
        ],
        weights=[
            27,
            22,
            10,
            9,
            10,
            10,
            12
        ]
    )[0]

    x = ROOM_X + random.randint(100, 650)
    y = ROOM_Y + random.randint(100, 350)

    return Encounter(
        encounter_type,
        x,
        y
    )

START_DAY = 5


def new_game():
    game_manager = GameManager()
    game_manager.day = START_DAY

    map_type, map_number = get_map_info(
        game_manager.day
    )

    room = Room(
        map_number,
        map_type
    )

    player = Player(
        ROOM_X + 48,
        ROOM_Y + 48
    )

    encounter = create_encounter()

    if encounter.type in [
        "healing_fountain",
        "cursed_fountain",
        "capy_statue",
        "training_buddy",
        "merchant"
    ]:
        enemies = []
    else:
        enemies = create_enemies(
            map_type,
            game_manager.day
        )

    return (
        game_manager,
        map_type,
        map_number,
        room,
        player,
        enemies,
        encounter
    )


def get_restart_button_rect():
    button_rect = pygame.Rect(
        0,
        0,
        280,
        70
    )

    button_rect.center = (
        SCREEN_WIDTH // 2,
        400
    )

    return button_rect


def draw_game_over(
    screen,
    big_font,
    button_font,
    mouse_position
):
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = big_font.render(
        "GAME OVER",
        True,
        (255, 80, 80)
    )

    title_shadow = big_font.render(
        "GAME OVER",
        True,
        (0, 0, 0)
    )

    title_rect = title.get_rect(
        center=(
            SCREEN_WIDTH // 2,
            230
        )
    )

    screen.blit(
        title_shadow,
        title_rect.move(4, 4)
    )

    screen.blit(
        title,
        title_rect
    )

    button_rect = get_restart_button_rect()

    if button_rect.collidepoint(
        mouse_position
    ):
        button_color = (
            110,
            150,
            90
        )
    else:
        button_color = (
            80,
            115,
            65
        )

    pygame.draw.rect(
        screen,
        button_color,
        button_rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (220, 200, 120),
        button_rect,
        3,
        border_radius=12
    )

    label = button_font.render(
        "RESTART",
        True,
        COLOR_TEXT
    )

    screen.blit(
        label,
        label.get_rect(
            center=button_rect.center
        )
    )


def draw_hud(screen, font, player):
    hud_text = (
        f"HP: {player.hp}/{player.max_hp}   "
        f"ATK: {player.attack}   "
        f"DEF: {player.defense}   "
        f"Gold: {player.gold}"
    )

    text = font.render(
        hud_text,
        True,
        COLOR_TEXT
    )

    screen.blit(
        text,
        (10, 10)
    )


def draw_backpack(screen, font, player, backpack_menu_open):
    backpack_rect = pygame.Rect(
        10,
        45,
        50,
        50
    )

    backpack_image = pygame.image.load(
        "assets/images/gameplay/backpack.png"
    ).convert_alpha()

    backpack_image = pygame.transform.scale(
        backpack_image,
        (50, 50)
    )

    screen.blit(
        backpack_image,
        backpack_rect
    )

    slot_text = font.render(
        f"{len(player.inventory)}/{player.inventory_slots}",
        True,
        COLOR_TEXT
    )

    screen.blit(
        slot_text,
        (65, 60)
    )

    if not backpack_menu_open:
        return backpack_rect, []

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 180)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    window = pygame.Rect(
        SCREEN_WIDTH // 2 - 300,
        60,
        600,
        480
    )

    pygame.draw.rect(
        screen,
        (45, 55, 45),
        window,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        (220, 200, 120),
        window,
        3,
        border_radius=15
    )

    title = font.render(
        "BACKPACK",
        True,
        COLOR_TEXT
    )

    screen.blit(
        title,
        (
            window.centerx
            - title.get_width() // 2,
            window.y + 20
        )
    )

    buttons = []

    for index, item_type in enumerate(
        player.inventory
    ):

        item_data = ITEM_DATA[item_type]

        row = pygame.Rect(
            window.x + 25,
            window.y + 75 + index * 55,
            550,
            45
        )

        pygame.draw.rect(
            screen,
            (70, 85, 70),
            row,
            border_radius=6
        )

        item_name = item_data["name"]
        stat = item_data["stat"]
        value = item_data["value"]

        if stat == "attack_potion":
            effect = "+25 ATK"
        elif stat == "skill_potion":
            effect = "+25 SKILL DMG"
        elif stat == "health_potion":
            effect = "FULL HEAL"
        elif stat == "gold_multiplier":
            effect = f"+{int(value * 100)}% GOLD"
        elif stat == "cooldown":
            effect = f"-{value}ms COOLDOWN"
        else:
            effect = (
                f"+{value} "
                f"{stat.replace('_', ' ').upper()}"
            )

        item_text = font.render(
            f"{item_name} ({effect})",
            True,
            COLOR_TEXT
        )

        screen.blit(
            item_text,
            (
                row.x + 15,
                row.centery
                - item_text.get_height() // 2
            )
        )

        if item_data["consumable"]:

            consume_button = pygame.Rect(
                row.right - 190,
                row.y + 5,
                80,
                35
            )

            pygame.draw.rect(
                screen,
                (70, 110, 70),
                consume_button,
                border_radius=5
            )

            consume_text = font.render(
                "USE",
                True,
                COLOR_TEXT
            )

            screen.blit(
                consume_text,
                (
                    consume_button.centerx
                    - consume_text.get_width() // 2,
                    consume_button.centery
                    - consume_text.get_height() // 2
                )
            )

            buttons.append(
                (
                    consume_button,
                    "consume",
                    item_type
                )
            )

        drop_button = pygame.Rect(
            row.right - 100,
            row.y + 5,
            85,
            35
        )

        pygame.draw.rect(
            screen,
            (100, 55, 55),
            drop_button,
            border_radius=5
        )

        drop_text = font.render(
            "DROP",
            True,
            COLOR_TEXT
        )

        screen.blit(
            drop_text,
            (
                drop_button.centerx
                - drop_text.get_width() // 2,
                drop_button.centery
                - drop_text.get_height() // 2
            )
        )

        buttons.append(
            (
                drop_button,
                "drop",
                item_type
            )
        )

    close_button = pygame.Rect(
        window.centerx - 100,
        window.bottom - 50,
        200,
        35
    )

    pygame.draw.rect(
        screen,
        (90, 60, 60),
        close_button,
        border_radius=6
    )

    close_text = font.render(
        "CLOSE",
        True,
        COLOR_TEXT
    )

    screen.blit(
        close_text,
        (
            close_button.centerx
            - close_text.get_width() // 2,
            close_button.centery
            - close_text.get_height() // 2
        )
    )

    buttons.append(
        (
            close_button,
            "close",
            None
        )
    )

    return backpack_rect, buttons

def draw_interaction_indicator(
    screen,
    player,
    encounter,
    items
):
    indicator = pygame.image.load(
        "assets/images/gameplay/indicator.png"
    ).convert_alpha()

    indicator = pygame.transform.scale(
        indicator,
        (32, 32)
    )

    if (
        encounter
        and encounter.active
        and player.rect.colliderect(
            encounter.rect.inflate(35, 35)
        )
    ):
        rect = indicator.get_rect(
            midbottom=(
                encounter.rect.centerx,
                encounter.rect.top - 5
            )
        )

        screen.blit(
            indicator,
            rect
        )

    for item in items:
        if (
            item.active
            and player.rect.colliderect(
                item.rect.inflate(35, 35)
            )
        ):
            rect = indicator.get_rect(
                midbottom=(
                    item.rect.centerx,
                    item.rect.top - 5
                )
            )

            screen.blit(
                indicator,
                rect
            )


def draw_skill_button(
    screen,
    font,
    player
):
    if player.selected_skill is None:
        return None

    button_rect = pygame.Rect(
        SCREEN_WIDTH - 210,
        SCREEN_HEIGHT - 80,
        190,
        55
    )

    current_time = pygame.time.get_ticks()

    cooldown_left = (
        player.skill_cooldown
        - (
            current_time
            - player.last_skill_use
        )
    )

    if cooldown_left > 0:
        button_color = (
            80,
            80,
            80
        )

        seconds = cooldown_left / 1000

        text = font.render(
            f"{player.selected_skill} {seconds:.1f}s",
            True,
            COLOR_TEXT
        )

    else:
        button_color = (
            90,
            60,
            140
        )

        text = font.render(
            f"USE {player.selected_skill}",
            True,
            COLOR_TEXT
        )

    pygame.draw.rect(
        screen,
        button_color,
        button_rect
    )

    pygame.draw.rect(
        screen,
        (220, 200, 120),
        button_rect,
        2
    )

    screen.blit(
        text,
        (
            button_rect.centerx
            - text.get_width() // 2,
            button_rect.centery
            - text.get_height() // 2
        )
    )

    return button_rect


def draw_skill_menu(screen, font):
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 190)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = font.render(
        "CHOOSE YOUR SKILL",
        True,
        COLOR_TEXT
    )

    screen.blit(
        title,
        (
            SCREEN_WIDTH // 2
            - title.get_width() // 2,
            100
        )
    )

    skills = [
        ("Fire", 35),
        ("Ice", 25),
        ("Lightning", 45)
    ]

    buttons = []

    for index, (name, damage) in enumerate(skills):

        button_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 150,
            180 + index * 100,
            300,
            70
        )

        pygame.draw.rect(
            screen,
            (60, 80, 70),
            button_rect
        )

        pygame.draw.rect(
            screen,
            (220, 200, 120),
            button_rect,
            2
        )

        text = font.render(
            f"{name}  +{damage} DMG",
            True,
            COLOR_TEXT
        )

        screen.blit(
            text,
            (
                button_rect.centerx
                - text.get_width() // 2,
                button_rect.centery
                - text.get_height() // 2
            )
        )

        buttons.append(
            (
                button_rect,
                name,
                damage
            )
        )

    return buttons

def draw_merchant_menu(screen, font, player, encounter):
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 180)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    window = pygame.Rect(
        SCREEN_WIDTH // 2 - 300,
        80,
        600,
        440
    )

    pygame.draw.rect(
        screen,
        (45, 55, 45),
        window,
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        (220, 200, 120),
        window,
        3,
        border_radius=15
    )

    title = font.render(
        "MERCHANT",
        True,
        COLOR_TEXT
    )

    screen.blit(
        title,
        (
            window.centerx - title.get_width() // 2,
            window.y + 25
        )
    )

    gold_text = font.render(
        f"Gold: {player.gold}",
        True,
        (255, 220, 80)
    )

    screen.blit(
        gold_text,
        (
            window.x + 25,
            window.y + 75
        )
    )

    buttons = []

    for index, (item_type, price) in enumerate(
        encounter.shop_items
    ):
        button = pygame.Rect(
            window.x + 40,
            window.y + 120 + index * 75,
            520,
            60
        )

        pygame.draw.rect(
            screen,
            (70, 85, 70),
            button,
            border_radius=8
        )

        item_name = ITEM_DATA[item_type]["name"]

        text = font.render(
            f"{item_name} - {price} Gold",
            True,
            COLOR_TEXT
        )

        screen.blit(
            text,
            (
                button.x + 20,
                button.centery - text.get_height() // 2
            )
        )

        buttons.append(
            (button, item_type, price)
        )

    close_button = pygame.Rect(
        window.centerx - 100,
        window.bottom - 65,
        200,
        45
    )

    pygame.draw.rect(
        screen,
        (90, 60, 60),
        close_button,
        border_radius=8
    )

    close_text = font.render(
        "CLOSE",
        True,
        COLOR_TEXT
    )

    screen.blit(
        close_text,
        (
            close_button.centerx
            - close_text.get_width() // 2,
            close_button.centery
            - close_text.get_height() // 2
        )
    )

    return buttons, close_button

def main():
    pygame.init()

    pygame.mixer.init()

    pygame.mixer.music.load(
        "assets/audio/capyloadscreenmusic.mp3"
    )

    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )
    )

    pygame.display.set_caption(
        GAME_TITLE
    )

    clock = pygame.time.Clock()

    if not run_start_screen(
        screen,
        clock
    ):
        pygame.quit()
        return

    pygame.mixer.music.stop()
    
    pygame.mixer.music.load("assets/audio/capybgmusic.mp3") #Medieval Music Vibez
    pygame.mixer.music.play(-1)

    font = pygame.font.Font(
        None,
        28
    )

    big_font = pygame.font.Font(
        None,
        160
    )

    button_font = pygame.font.Font(
        None,
        52
    )

    (
        game_manager,
        map_type,
        map_number,
        room,
        player,
        enemies,
        encounter
    ) = new_game()

    items = []


    last_player_attack = 0
    player_attack_cooldown = 1000

    skill_menu_open = False
    skill_buttons = []
    skill_effect = None
    
    merchant_menu_open = False
    backpack_menu_open = False
    backpack_buttons = []
    

    blocked_message_until = 0

    running = True

    while running:

        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                
                if (
                    event.key == pygame.K_b
                    and game_manager.state != "GAME_OVER"
                ):
                    if not merchant_menu_open:
                        backpack_menu_open = not backpack_menu_open

                if (
                    event.key == pygame.K_e
                    and game_manager.state != "GAME_OVER"
                ):

                    for item in items:

                        if (
                            item.active
                            and player.rect.colliderect(
                                item.rect.inflate(
                                    35,
                                    35
                                )
                            )
                        ):
                            item.collect(
                                player
                            )

                    if (
                        encounter.active
                        and player.rect.colliderect(
                            encounter.rect
                        )
                    ):

                        if encounter.type == "merchant":
                            merchant_menu_open = True

                        elif (
                            encounter.type in [
                                "gold_chest",
                                "mystery_chest"
                            ]
                            and enemies
                        ):
                            pass

                        else:
                            encounter.interact(
                                player
                            )

                    if (
                        map_type == "normal"
                        and map_number == 5
                        and player.selected_skill is None
                    ):

                        campsite = pygame.Rect(
                            ROOM_X + 570,
                            ROOM_Y + 70,
                            190,
                            190
                        )

                        if player.rect.colliderect(
                            campsite
                        ):
                            skill_menu_open = True

                if (
                    game_manager.state == "GAME_OVER"
                    and event.key in (
                        pygame.K_RETURN,
                        pygame.K_r
                    )
                ):

                    (
                        game_manager,
                        map_type,
                        map_number,
                        room,
                        player,
                        enemies,
                        encounter
                    ) = new_game()

                    items = []

                    last_player_attack = 0
                    skill_menu_open = False
                    skill_effect = None

                elif (
                    event.key == pygame.K_SPACE
                    and game_manager.state != "GAME_OVER"
                    and enemies
                ):

                    blocked_message_until = (
                        pygame.time.get_ticks()
                        + 1800
                    )

                elif (
                    event.key == pygame.K_SPACE
                    and game_manager.state != "GAME_OVER"
                ):

                    if (
                        not skill_menu_open
                        and not merchant_menu_open
                        and not backpack_menu_open
                    ):

                        game_manager.next_day()

                        map_type, map_number = get_map_info(
                            game_manager.day
                        )

                        encounter = create_encounter()

                        items = []
                        merchant_menu_open = False
                        
                        
                        room = Room(
                            map_number,
                            map_type
                        )

                        player.rect.topleft = (
                            ROOM_X + 48,
                            ROOM_Y + 48
                        )

                        if encounter.type in [
                            "healing_fountain",
                            "cursed_fountain",
                            "capy_statue",
                            "training_buddy",
                            "merchant"
                        ]:
                            enemies = []

                        else:
                            enemies = create_enemies(
                                map_type,
                                game_manager.day
                            )

            if event.type == pygame.MOUSEBUTTONDOWN:

                if (
                    event.button == 1
                    and game_manager.state == "GAME_OVER"
                ):

                    if get_restart_button_rect().collidepoint(
                        mouse_position
                    ):

                        (
                            game_manager,
                            map_type,
                            map_number,
                            room,
                            player,
                            enemies,
                            encounter
                        ) = new_game()

                        items = []
                        merchant_menu_open = False
                        backpack_menu_open = False
                        last_player_attack = 0
                        skill_menu_open = False
                        skill_effect = None

                elif event.button == 1:
                    
                    backpack_icon_rect = pygame.Rect(
                        10,
                        45,
                        50,
                        50
                    )

                    if (
                        not backpack_menu_open
                        and not merchant_menu_open
                        and backpack_icon_rect.collidepoint(mouse_position)
                    ):
                        backpack_menu_open = True
                        continue
                    
                    if backpack_menu_open:

                        for (
                            button,
                            action,
                            item_type
                        ) in backpack_buttons:

                            if button.collidepoint(
                                mouse_position
                            ):

                                if action == "close":
                                    backpack_menu_open = False

                                elif action == "consume":
                                    consume_item(
                                        player,
                                        item_type
                                    )

                                elif action == "drop":
                                    if remove_item(
                                        player,
                                        item_type
                                    ):
                                        items.append(
                                            ItemPickup(
                                                item_type,
                                                player.rect.centerx,
                                                player.rect.centery
                                            )
                                        )

                                break

                        continue
                    
                    if merchant_menu_open:

                        merchant_buttons, close_button = draw_merchant_menu(
                            screen,
                            font,
                            player,
                            encounter
                        )

                        if close_button.collidepoint(
                            mouse_position
                        ):
                            merchant_menu_open = False

                        else:
                            for button, item_type, price in merchant_buttons:

                                if button.collidepoint(
                                    mouse_position
                                ):

                                    if (
                                        player.gold >= price
                                        and len(player.inventory)
                                        < player.inventory_slots
                                    ):

                                        if give_item(
                                            player,
                                            item_type
                                        ):
                                            player.gold -= price

                        continue

                    if skill_menu_open:

                        skill_buttons = draw_skill_menu(
                            screen,
                            font
                        )

                        for (
                            button,
                            name,
                            damage
                        ) in skill_buttons:

                            if button.collidepoint(
                                mouse_position
                            ):

                                player.selected_skill = name
                                player.skill_damage += damage
                                skill_menu_open = False

        if game_manager.state == "EXPLORING":

            if (
                not skill_menu_open
                and not merchant_menu_open
                and not backpack_menu_open
            ):
                player.update([])

        current_time = pygame.time.get_ticks()

        if (
            not skill_menu_open
            and not merchant_menu_open
            and not backpack_menu_open
            and game_manager.state != "GAME_OVER"
        ):

            for enemy in enemies:
                enemy.update(player)

            if player.hp <= 0:
                player.hp = 0
                game_manager.state = "GAME_OVER"

            for enemy in enemies:

                if not enemy.alive:
                    continue

                distance = pygame.math.Vector2(
                    player.rect.center
                ).distance_to(
                    enemy.rect.center
                )

                if (
                    distance <= 100
                    and current_time
                    - last_player_attack
                    >= player_attack_cooldown
                ):

                    player.attack_enemy()

                    enemy.take_damage(
                        player.attack
                    )

                    last_player_attack = current_time

                    if not enemy.alive:
                        player.add_gold(
                            int(
                                10
                                * player.gold_multiplier
                            )
                        )

                        items.append(
                            HeartPickup(
                                enemy.rect.centerx,
                                enemy.rect.centery
                            )
                        )

        enemies = [
            enemy
            for enemy in enemies
            if enemy.alive
        ]
        
        items = [
            item
            for item in items
            if item.active
        ]

        if skill_effect:

            skill_effect.update()

            if skill_effect.finished:
                skill_effect = None

        screen.fill(
            COLOR_BACKGROUND
        )

        room.draw(
            screen
        )

        for enemy in enemies:
            enemy.draw(
                screen
            )

        encounter.update()

        encounter.complete_reward(
            player,
            items
        )
        encounter.draw(
            screen
        )

        for item in items:

            if isinstance(
                item,
                HeartPickup
            ):
                item.update()

                if (
                    item.active
                    and player.rect.colliderect(
                        item.rect
                    )
                ):
                    item.collect(
                        player
                    )

            item.draw(
                screen
            )

        player.draw(
            screen
        )

        draw_interaction_indicator(
            screen,
            player,
            encounter,
            items
        )

        if skill_effect:
            skill_effect.draw(
                screen
            )

        draw_hud(
            screen,
            font,
            player
        )

        backpack_icon_rect, backpack_buttons = draw_backpack(
            screen,
            font,
            player,
            backpack_menu_open
        )

        skill_button = draw_skill_button(
            screen,
            font,
            player
        )

        if (
            skill_button
            and not skill_menu_open
            and game_manager.state != "GAME_OVER"
            and pygame.mouse.get_pressed()[0]
            and skill_button.collidepoint(
                mouse_position
            )
        ):

            if (
                current_time
                - player.last_skill_use
                >= player.skill_cooldown
            ):

                skill_enemies = []

                for enemy in enemies:

                    if not enemy.alive:
                        continue

                    dx = (
                        enemy.rect.centerx
                        - player.rect.centerx
                    )

                    dy = abs(
                        enemy.rect.centery
                        - player.rect.centery
                    )

                    if player.facing_right:
                        in_front = dx > 0
                    else:
                        in_front = dx < 0

                    distance = pygame.math.Vector2(
                        player.rect.center
                    ).distance_to(
                        enemy.rect.center
                    )

                    if (
                        in_front
                        and distance <= 180
                        and dy <= 100
                    ):
                        skill_enemies.append(
                            enemy
                        )

                if skill_enemies:

                    skill_effect = SkillEffect(
                        player.selected_skill,
                        (
                            player.rect.centerx
                            + (
                                70
                                if player.facing_right
                                else -70
                            ),
                            player.rect.centery
                        ),
                        player.facing_right
                    )

                    for enemy in skill_enemies:

                        enemy.take_damage(
                            player.skill_damage
                        )

                        if not enemy.alive:

                            player.add_gold(
                                int(
                                    20
                                    * player.gold_multiplier
                                )
                            )

                            items.append(
                                HeartPickup(
                                    enemy.rect.centerx,
                                    enemy.rect.centery
                                )
                            )

                    player.last_skill_use = (
                        current_time
                    )
        if skill_menu_open:

            skill_buttons = draw_skill_menu(
                screen,
                font
            )

        if merchant_menu_open:

            draw_merchant_menu(
                screen,
                font,
                player,
                encounter
            )

        if (
            map_type == "normal"
            and map_number == 5
            and not skill_menu_open
            and player.selected_skill is None
        ):

            campsite = pygame.Rect(
                ROOM_X + 570,
                ROOM_Y + 70,
                190,
                190
            )

            if player.rect.colliderect(
                campsite
            ):

                prompt = font.render(
                    "Press E to choose a skill",
                    True,
                    COLOR_TEXT
                )

                screen.blit(
                    prompt,
                    (
                        SCREEN_WIDTH // 2
                        - prompt.get_width() // 2,
                        SCREEN_HEIGHT - 35
                    )
                )

        if (
            game_manager.state != "GAME_OVER"
            and not skill_menu_open
        ):

            if current_time < blocked_message_until:

                next_day_text = font.render(
                    "Defeat all enemies first!",
                    True,
                    (255, 100, 100)
                )

            elif not enemies:

                next_day_text = font.render(
                    "Area cleared! Press SPACE to continue",
                    True,
                    (255, 235, 150)
                )

            else:
                next_day_text = None

            if next_day_text:

                screen.blit(
                    next_day_text,
                    (
                        SCREEN_WIDTH // 2
                        - next_day_text.get_width() // 2,
                        SCREEN_HEIGHT - 62
                    )
                )

        if game_manager.state == "GAME_OVER":

            draw_game_over(
                screen,
                big_font,
                button_font,
                mouse_position
            )

        pygame.display.flip()

        clock.tick(
            FPS
        )

    pygame.quit()


if __name__ == "__main__":
    main()