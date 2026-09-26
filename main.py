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

    screen.blit(text, (10, 10))


def draw_skill_button(screen, font, player):
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
        - (current_time - player.last_skill_use)
    )

    if cooldown_left > 0:
        button_color = (80, 80, 80)
        seconds = cooldown_left / 1000

        text = font.render(
            f"{player.selected_skill} {seconds:.1f}s",
            True,
            COLOR_TEXT
        )
    else:
        button_color = (90, 60, 140)

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

    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

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
            (button_rect, name, damage)
        )

    return buttons


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    pygame.display.set_caption(GAME_TITLE)

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    game_manager = GameManager()

    map_number = 5
    room = Room(map_number)

    player = Player(
        ROOM_X + 48,
        ROOM_Y + 48
    )

    enemies = [
        Enemy(
            ROOM_X + 350,
            ROOM_Y + 200
        ),
        Enemy(
            ROOM_X + 550,
            ROOM_Y + 350
        )
    ]

    last_player_attack = 0
    player_attack_cooldown = 1000

    skill_menu_open = False
    skill_buttons = []
    skill_effect = None

    running = True

    while running:

        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_e:

                    if (
                        map_number == 5
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

                if event.key == pygame.K_SPACE:

                    if not skill_menu_open:

                        game_manager.next_day()

                        map_number = (
                            (game_manager.day - 1) % 5
                        ) + 1

                        room = Room(map_number)

                        player.rect.topleft = (
                            ROOM_X + 48,
                            ROOM_Y + 48
                        )

                        enemies = [
                            Enemy(
                                ROOM_X + 350,
                                ROOM_Y + 200
                            ),
                            Enemy(
                                ROOM_X + 550,
                                ROOM_Y + 350
                            )
                        ]

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

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

        if not skill_menu_open:

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
                        player.gold += 10

        enemies = [
            enemy for enemy in enemies
            if enemy.alive
        ]
        
        if skill_effect:
            skill_effect.update()

            if skill_effect.finished:
                skill_effect = None

        screen.fill(
            COLOR_BACKGROUND
        )

        room.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if skill_effect:
            skill_effect.draw(screen)

        draw_hud(
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
                            + (70 if player.facing_right else -70),
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
                        player.gold += 20

        if skill_menu_open:

            skill_buttons = draw_skill_menu(
                screen,
                font
            )

        if (
            map_number == 5
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

        if game_manager.state == "GAME_OVER":

            game_over_text = font.render(
                "GAME OVER",
                True,
                (255, 80, 80)
            )

            screen.blit(
                game_over_text,
                (
                    SCREEN_WIDTH // 2 - 70,
                    20
                )
            )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()