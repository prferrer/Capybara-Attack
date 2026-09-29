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
from systems.item import ItemPickup


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


def create_item():
    item_type = random.choice([
        "iron_claw",
        "iron_armor",
        "heart_medallion",
        "lucky_coin",
        "stopwatch",
        "spellbook"
    ])

    x = ROOM_X + random.randint(100, 650)
    y = ROOM_Y + random.randint(100, 350)

    return ItemPickup(
        item_type,
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


def draw_backpack(screen, font, player):
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
        (
            65,
            60
        )
    )


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

    if random.random() < 0.25:
        items.append(
            create_item()
        )

    last_player_attack = 0
    player_attack_cooldown = 1000

    skill_menu_open = False
    skill_buttons = []
    skill_effect = None

    blocked_message_until = 0

    running = True

    while running:

        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

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

                        if (
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

                    if random.random() < 0.25:
                        items.append(
                            create_item()
                        )

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

                    if not skill_menu_open:

                        game_manager.next_day()

                        map_type, map_number = get_map_info(
                            game_manager.day
                        )

                        encounter = create_encounter()

                        items = []

                        if random.random() < 0.25:
                            items.append(
                                create_item()
                            )

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

                        if random.random() < 0.25:
                            items.append(
                                create_item()
                            )

                        last_player_attack = 0
                        skill_menu_open = False
                        skill_effect = None

                elif event.button == 1:

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
                                player.skill_damage = damage
                                skill_menu_open = False

        if game_manager.state == "EXPLORING":

            if not skill_menu_open:
                player.update([])

        current_time = pygame.time.get_ticks()

        if (
            not skill_menu_open
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
                        player.gold += int(
                            10 * player.gold_multiplier
                        )

        enemies = [
            enemy
            for enemy in enemies
            if enemy.alive
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
            player
        )

        encounter.draw(
            screen
        )

        for item in items:
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

        draw_backpack(
            screen,
            font,
            player
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

                nearest_enemy = None
                nearest_distance = float("inf")

                for enemy in enemies:

                    distance = pygame.math.Vector2(
                        player.rect.center
                    ).distance_to(
                        enemy.rect.center
                    )

                    if distance < nearest_distance:
                        nearest_enemy = enemy
                        nearest_distance = distance

                if (
                    nearest_enemy
                    and nearest_distance <= 180
                ):

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

                    nearest_enemy.take_damage(
                        player.skill_damage
                    )

                    player.last_skill_use = (
                        current_time
                    )

                    if not nearest_enemy.alive:
                        player.gold += int(
                            20 * player.gold_multiplier
                        )

        if skill_menu_open:

            skill_buttons = draw_skill_menu(
                screen,
                font
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