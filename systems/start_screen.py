import os

import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_TEXT,
    COLOR_BORDER,
)
from systems.settings_menu import menu as settings_menu

VIDEO_PATH = "assets/videos/capybara-loading.mp4"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BUTTONS_CENTER_X = 0.51
BUTTONS_CENTER_Y = 0.43

try:
    import cv2
except ImportError:
    cv2 = None

class LoopingVideo:
    def __init__(self, path):
        self.capture = None
        self.frame_surface = None
        self.frame_time = 1000 / 30
        self.next_frame_at = 0
        self.error = None
        self.hint = None

        self.rect = pygame.Rect(
            0,
            0,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        if not os.path.isabs(path):
            path = os.path.join(PROJECT_ROOT, path)

        if cv2 is None:
            self.error = (
                "OpenCV is not installed, so the video can't play. "
                "Run:  pip install opencv-python"
            )
            self.hint = "Video can't play: run  pip install opencv-python"

        elif not os.path.exists(path):
            self.error = f"Video file not found: {path}"
            self.hint = (
                "Video file not found - see console for the path "
                "it looked in"
            )

        else:
            capture = cv2.VideoCapture(path)

            if not capture.isOpened():
                self.error = (
                    f"OpenCV could not open the video: {path}"
                )
                self.hint = (
                    "OpenCV could not open the video - see console"
                )
                capture.release()
                capture = None

        if self.error:
            print(f"[start screen] {self.error}")
            return

        src_w = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        src_h = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if not src_w or not src_h:
            capture.release()
            return

        self.capture = capture

        video_h = round(
            SCREEN_WIDTH * src_h / src_w
        )

        self.size = (
            SCREEN_WIDTH,
            video_h
        )

        self.rect = pygame.Rect(
            0,
            (SCREEN_HEIGHT - video_h) // 2,
            SCREEN_WIDTH,
            video_h
        )

        fps = capture.get(cv2.CAP_PROP_FPS)

        if fps and fps > 1:
            self.frame_time = 1000 / fps

    @property
    def has_video(self):
        return self.capture is not None

    def update(self):
        if self.capture is None:
            return

        now = pygame.time.get_ticks()

        if (
            self.frame_surface is not None
            and now < self.next_frame_at
        ):
            return

        ok, frame = self.capture.read()

        if not ok:
            self.capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                0
            )

            ok, frame = self.capture.read()

            if not ok:
                return

        if (
            frame.shape[1],
            frame.shape[0]
        ) != self.size:
            frame = cv2.resize(
                frame,
                self.size
            )

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        self.frame_surface = pygame.image.frombuffer(
            frame.tobytes(),
            self.size,
            "RGB"
        )

        self.next_frame_at += self.frame_time

        if (
            now - self.next_frame_at
            > self.frame_time * 3
        ):
            self.next_frame_at = (
                now + self.frame_time
            )

    def draw(self, screen, hint_font):
        screen.fill((0, 0, 0))

        if self.frame_surface is not None:
            screen.blit(
                self.frame_surface,
                self.rect.topleft
            )
            return

        for y in range(SCREEN_HEIGHT):
            shade = 25 + int(
                40 * y / SCREEN_HEIGHT
            )

            pygame.draw.line(
                screen,
                (
                    shade,
                    shade + 15,
                    shade
                ),
                (0, y),
                (SCREEN_WIDTH, y)
            )

        if self.hint:
            draw_text_with_shadow(
                screen,
                hint_font,
                self.hint,
                (255, 200, 120),
                (
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT - 30
                )
            )

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None

def draw_text_with_shadow(
    screen,
    font,
    text,
    color,
    center
):
    shadow = font.render(
        text,
        True,
        (0, 0, 0)
    )

    label = font.render(
        text,
        True,
        color
    )

    label_rect = label.get_rect(
        center=center
    )

    screen.blit(
        shadow,
        label_rect.move(2, 2)
    )

    screen.blit(
        label,
        label_rect
    )

    return label_rect

WEAPON_OPTIONS = [
    {
        "id": "sword",
        "name": "SWORD",
        "image": "assets/images/player/idle1.png",
        "description": (
            "A balanced weapon with reliable offense, "
            "defense, and survivability."
        ),
        "stats": "HP 100   ATK 10   DEF 5",
        "benefit": (
            "Weapon Skill: Berserk\n"
            "Boosts all stats and grants lifesteal."
        ),
    },
    {
        "id": "katana",
        "name": "KATANA",
        "image": "assets/images/player/katana_idle1.png",
        "description": (
            "A fast, aggressive weapon built around "
            "high damage and mobility."
        ),
        "stats": "HP 70   ATK 25   DEF 2",
        "benefit": (
            "Weapon Skill: Dash\n"
            "Dash forward, damage enemies hit, and become untargetable."
        ),
    },
    {
        "id": "staff",
        "name": "STAFF",
        "image": "assets/images/player/staff_idle1.png",
        "description": (
            "A skill-focused weapon with weaker base "
            "stats but faster skill use."
        ),
        "stats": "HP 85   ATK 8   DEF 3",
        "benefit": (
            "Weapon Skill: Overcharge\n"
            "Boosts skill damage and greatly reduces skill cooldowns."
        ),
    },
    {
        "id": "shield",
        "name": "SHIELD",
        "image": "assets/images/player/shield_idle1.png",
        "description": (
            "A defensive weapon with massive durability "
            "at the cost of attack."
        ),
        "stats": "HP 200   ATK 4   DEF 20",
        "benefit": (
            "Weapon Skill: Barrier\n"
            "Surround yourself with a barrier that reflects damage."
        ),
    },
]

def draw_multiline_text(
    screen,
    font,
    text,
    color,
    center_x,
    start_y,
    line_gap=26
):
    lines = text.split("\n")

    for index, line in enumerate(lines):
        label = font.render(
            line,
            True,
            color
        )

        rect = label.get_rect(
            center=(
                center_x,
                start_y + index * line_gap
            )
        )

        screen.blit(
            label,
            rect
        )


def wrap_text(
    font,
    text,
    max_width
):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = (
            current_line + " " + word
        ).strip()

        if font.size(test_line)[0] <= max_width:
            current_line = test_line

        else:
            if current_line:
                lines.append(current_line)

            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def run_character_selection(
    screen,
    clock
):
    title_font = pygame.font.Font(
        None,
        58
    )

    weapon_font = pygame.font.Font(
        None,
        34
    )

    text_font = pygame.font.Font(
        None,
        24
    )

    small_font = pygame.font.Font(
        None,
        21
    )

    button_font = pygame.font.Font(
        None,
        34
    )

    skill_title_font = pygame.font.Font(
        None,
        24
    )

    skill_name_font = pygame.font.Font(
        None,
        23
    )

    images = {}

    for weapon in WEAPON_OPTIONS:
        image = pygame.image.load(
            weapon["image"]
        ).convert_alpha()

        images[weapon["id"]] = pygame.transform.scale(
            image,
            (128, 128)
        )

    selected_index = 0
    running = True

    while running:
        mouse_position = pygame.mouse.get_pos()

        # Weapon cards moved upward to create space below.
        card_width = 215
        card_height = 390
        gap = 10

        total_width = (
            card_width * len(WEAPON_OPTIONS)
            + gap * (len(WEAPON_OPTIONS) - 1)
        )

        start_x = (
            SCREEN_WIDTH - total_width
        ) // 2

        card_y = 75

        cards = []

        for index in range(
            len(WEAPON_OPTIONS)
        ):
            cards.append(
                pygame.Rect(
                    start_x + index * (
                        card_width + gap
                    ),
                    card_y,
                    card_width,
                    card_height
                )
            )

        # Dedicated weapon skill card.
        skill_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 380,
            475,
            760,
            65
        )

        confirm_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 125,
            555,
            250,
            55
        )

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:

                if event.key in (
                    pygame.K_a,
                    pygame.K_LEFT
                ):
                    selected_index = (
                        selected_index - 1
                    ) % len(WEAPON_OPTIONS)

                elif event.key in (
                    pygame.K_d,
                    pygame.K_RIGHT
                ):
                    selected_index = (
                        selected_index + 1
                    ) % len(WEAPON_OPTIONS)

                elif event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER,
                    pygame.K_SPACE
                ):
                    return WEAPON_OPTIONS[
                        selected_index
                    ]["id"]

                elif event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4
                ):
                    selected_index = (
                        event.key - pygame.K_1
                    )

                elif event.key == pygame.K_ESCAPE:
                    return None

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                for index, card in enumerate(cards):

                    if card.collidepoint(
                        mouse_position
                    ):
                        selected_index = index

                if skill_rect.collidepoint(
                    mouse_position
                ):
                    pass

                if confirm_rect.collidepoint(
                    mouse_position
                ):
                    return WEAPON_OPTIONS[
                        selected_index
                    ]["id"]

        screen.fill(
            (22, 27, 30)
        )

        # Title
        draw_text_with_shadow(
            screen,
            title_font,
            "CHOOSE YOUR WEAPON",
            COLOR_TEXT,
            (
                SCREEN_WIDTH // 2,
                55
            )
        )

        selected_weapon = WEAPON_OPTIONS[
            selected_index
        ]

        # -------------------------------------------------
        # WEAPON CARDS
        # -------------------------------------------------

        for index, (
            weapon,
            card
        ) in enumerate(
            zip(
                WEAPON_OPTIONS,
                cards
            )
        ):

            is_selected = (
                index == selected_index
            )

            is_hovered = card.collidepoint(
                mouse_position
            )

            if is_selected:
                card_color = (
                    75,
                    95,
                    70
                )

                border_color = (
                    255,
                    220,
                    120
                )

                border_width = 4

            elif is_hovered:
                card_color = (
                    55,
                    70,
                    58
                )

                border_color = (
                    180,
                    190,
                    140
                )

                border_width = 2

            else:
                card_color = (
                    42,
                    50,
                    52
                )

                border_color = (
                    100,
                    105,
                    100
                )

                border_width = 2

            pygame.draw.rect(
                screen,
                card_color,
                card,
                border_radius=10
            )

            pygame.draw.rect(
                screen,
                border_color,
                card,
                border_width,
                border_radius=10
            )

            # Weapon name
            name = weapon_font.render(
                weapon["name"],
                True,
                COLOR_TEXT
            )

            screen.blit(
                name,
                name.get_rect(
                    center=(
                        card.centerx,
                        card.y + 35
                    )
                )
            )

            # Character sprite
            image_rect = images[
                weapon["id"]
            ].get_rect(
                center=(
                    card.centerx,
                    card.y + 120
                )
            )

            screen.blit(
                images[weapon["id"]],
                image_rect
            )

            # Stats
            stats = text_font.render(
                weapon["stats"],
                True,
                (255, 225, 145)
            )

            screen.blit(
                stats,
                stats.get_rect(
                    center=(
                        card.centerx,
                        card.y + 195
                    )
                )
            )

            # Description
            description_lines = wrap_text(
                small_font,
                weapon["description"],
                card.width - 25
            )

            description_y = card.y + 235

            for line in description_lines[:4]:
                label = small_font.render(
                    line,
                    True,
                    COLOR_TEXT
                )

                screen.blit(
                    label,
                    label.get_rect(
                        center=(
                            card.centerx,
                            description_y
                        )
                    )
                )

                description_y += 22

        # -------------------------------------------------
        # WEAPON SKILL CARD
        # -------------------------------------------------

        skill_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 380,
            475,
            760,
            78
        )

        pygame.draw.rect(
            screen,
            (38, 48, 40),
            skill_rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (255, 220, 120),
            skill_rect,
            3,
            border_radius=12
        )

        # Skill title
        skill_title = skill_title_font.render(
            "WEAPON SKILL",
            True,
            (255, 220, 120)
        )

        screen.blit(
            skill_title,
            skill_title.get_rect(
                center=(
                    skill_rect.centerx,
                    skill_rect.y + 18
                )
            )
        )

        # Separate skill name and description
        benefit_lines = (
            selected_weapon["benefit"]
            .split("\n")
        )

        skill_name = benefit_lines[0]

        skill_description = ""

        if len(benefit_lines) > 1:
            skill_description = " ".join(
                benefit_lines[1:]
            )

        # Skill name
        skill_name_label = skill_name_font.render(
            skill_name,
            True,
            COLOR_TEXT
        )

        screen.blit(
            skill_name_label,
            skill_name_label.get_rect(
                center=(
                    skill_rect.centerx,
                    skill_rect.y + 42
                )
            )
        )

        # Skill description
        description_lines = wrap_text(
            small_font,
            skill_description,
            680
        )

        for index, line in enumerate(
            description_lines[:2]
        ):
            description_label = small_font.render(
                line,
                True,
                (215, 215, 185)
            )

            screen.blit(
                description_label,
                description_label.get_rect(
                    center=(
                        skill_rect.centerx,
                        skill_rect.y
                        + 62
                        + index * 19
                    )
                )
            )
        # -------------------------------------------------
        # CONFIRM BUTTON
        # -------------------------------------------------

        confirm_color = (
            (110, 150, 90)
            if confirm_rect.collidepoint(
                mouse_position
            )
            else (80, 115, 65)
        )

        pygame.draw.rect(
            screen,
            confirm_color,
            confirm_rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            COLOR_BORDER,
            confirm_rect,
            3,
            border_radius=10
        )

        confirm_text = button_font.render(
            f"CHOOSE {selected_weapon['name']}",
            True,
            COLOR_TEXT
        )

        screen.blit(
            confirm_text,
            confirm_text.get_rect(
                center=confirm_rect.center
            )
        )

        # Controls hint
        hint = small_font.render(
            "1-4 / A-D / Arrow Keys to select  •  "
            "Enter or Click to confirm",
            True,
            (170, 175, 170)
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    628
                )
            )
        )

        pygame.display.flip()
        clock.tick(FPS)

    return None


def run_start_screen(screen, clock):
    """
    Shows the looping video with Start / Settings buttons.
    Returns True when the player presses Start, False if they quit.
    """

    title_font = pygame.font.Font(
        None,
        96
    )

    button_font = pygame.font.Font(
        None,
        52
    )

    text_font = pygame.font.Font(
        None,
        34
    )

    hint_font = pygame.font.Font(
        None,
        24
    )

    video = LoopingVideo(
        VIDEO_PATH
    )

    center_x = int(
        SCREEN_WIDTH * BUTTONS_CENTER_X
    )

    center_y = (
        video.rect.top
        + int(
            video.rect.height
            * BUTTONS_CENTER_Y
        )
    )

    start_rect = pygame.Rect(
        0,
        0,
        200,
        60
    )

    start_rect.center = (
        center_x - 95,
        center_y
    )

    settings_center = (
        center_x + 145,
        center_y
    )

    settings_rect = pygame.Rect(
        0,
        0,
        160,
        50
    )

    settings_rect.center = (
        settings_center
    )

    result = False
    running = True

    while running:
        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                result = False
                running = False

            elif event.type == pygame.KEYDOWN:

                if settings_menu.is_open:
                    settings_menu.handle_event(event)

                elif event.key in (
                    pygame.K_RETURN,
                    pygame.K_KP_ENTER
                ):
                    result = True
                    running = False

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if settings_menu.is_open:
                    settings_menu.handle_event(event)

                elif start_rect.collidepoint(
                    mouse_position
                ):
                    result = True
                    running = False

                elif settings_rect.collidepoint(
                    mouse_position
                ):
                    settings_menu.open()

            elif settings_menu.is_open:
                settings_menu.handle_event(event)

        video.update()

        video.draw(
            screen,
            hint_font
        )


        hovering_start = (
            start_rect.collidepoint(
                mouse_position
            )
        )

        fill = (
            (110, 150, 90)
            if hovering_start
            else (80, 115, 65)
        )

        pygame.draw.rect(
            screen,
            fill,
            start_rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            COLOR_BORDER,
            start_rect,
            3,
            border_radius=12
        )

        draw_text_with_shadow(
            screen,
            button_font,
            "START",
            COLOR_TEXT,
            start_rect.center
        )

        hovering_settings = (
            settings_rect.collidepoint(
                mouse_position
            )
        )

        color = (
            (255, 235, 150)
            if hovering_settings
            else COLOR_TEXT
        )

        label_rect = draw_text_with_shadow(
            screen,
            text_font,
            "Settings",
            color,
            settings_center
        )

        if hovering_settings:

            pygame.draw.line(
                screen,
                color,
                (
                    label_rect.left,
                    label_rect.bottom + 2
                ),
                (
                    label_rect.right,
                    label_rect.bottom + 2
                ),
                2
            )

        settings_menu.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    video.close()

    return result
