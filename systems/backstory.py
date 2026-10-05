import os

import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_TEXT,
)
from systems.start_screen import (
    draw_text_with_shadow,
    wrap_text,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BACKSTORY_DIR = "assets/images/backstory"

# The 5 grid panels, in the position they sit on the original comic page
# (x, y, width, height), measured in the original page's own pixels -
# the page itself is GRID_PANEL_SIZE below. They build up in this order,
# each appearing in its own spot, like the comic page assembling itself.
GRID_PANEL_SIZE = (1532, 849)

GRID_PANELS = [
    ("panel_01.png", (0, 0, 735, 378)),
    ("panel_02.png", (763, 0, 380, 378)),
    ("panel_03.png", (1172, 0, 360, 378)),
    ("panel_04.png", (0, 419, 800, 430)),
    ("panel_05.png", (838, 419, 694, 430)),
]

# Shown full-screen by itself once the comic page has finished building.
FINAL_PANEL_FILE = "panel_06.png"

# Pause before the first grid panel appears, in milliseconds.
INTRO_PAUSE_MS = 500

# Time between one grid panel appearing and the next one starting.
GRID_PANEL_INTERVAL_MS = 1100

# How long a panel takes to fade in.
FADE_MS = 300

# Pause on the completed comic page before cutting to the final panel.
PAGE_HOLD_MS = 1000

# Pause on the final panel before the objective popup fades in.
OBJECTIVE_PAUSE_MS = 1000

# How long the objective popup takes to fade in.
OBJECTIVE_FADE_MS = 400

# "Press to continue" hint, shown once everything is fully visible.
HINT_TEXT = "Click or press any key to continue"

OBJECTIVE_TITLE_LINES = [
    "OBJECTIVE:",
    "RECLAIM YOUR HOME",
]

OBJECTIVE_BODY_LINES = [
    "The invaders have taken over Capy land.",
    (
        "Fight your way through the enemies, defeat them all, "
        "and take back the home that was stolen from you."
    ),
    "Good luck, Capy.",
]

OBJECTIVE_BOX_SIZE = (680, 300)


def _fit_rect(size, target_width, target_height):
    width, height = size

    scale = min(target_width / width, target_height / height)

    return round(width * scale), round(height * scale), scale


def _load_image(file_name):
    path = os.path.join(PROJECT_ROOT, BACKSTORY_DIR, file_name)

    if not os.path.exists(path):
        return None, path

    try:
        return pygame.image.load(path).convert(), path
    except pygame.error as error:
        return None, f"{path} ({error})"


def _build_grid(missing):
    """
    Loads the 5 grid panels and scales/positions each one as it would sit
    on the full comic page once that page is scaled to fit the screen.
    Returns a list of (scaled_surface, rect_on_screen), in build order.
    """
    page_width, page_height, scale = _fit_rect(
        GRID_PANEL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
    )

    page_left = (SCREEN_WIDTH - page_width) // 2
    page_top = (SCREEN_HEIGHT - page_height) // 2

    panels = []

    for file_name, (x, y, width, height) in GRID_PANELS:
        image, path_or_error = _load_image(file_name)

        if image is None:
            missing.append(path_or_error)
            continue

        size = (round(width * scale), round(height * scale))
        scaled = pygame.transform.smoothscale(image, size)

        rect = scaled.get_rect(
            topleft=(
                page_left + round(x * scale),
                page_top + round(y * scale)
            )
        )

        panels.append((scaled, rect))

    return panels


def _build_final_panel(missing):
    image, path_or_error = _load_image(FINAL_PANEL_FILE)

    if image is None:
        missing.append(path_or_error)
        return None

    width, height, _ = _fit_rect(
        image.get_size(), SCREEN_WIDTH, SCREEN_HEIGHT
    )

    scaled = pygame.transform.smoothscale(image, (width, height))

    rect = scaled.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    )

    return scaled, rect


def _draw_faded(screen, surface, rect, alpha):
    if alpha >= 255:
        screen.blit(surface, rect)
        return

    faded = surface.copy()
    faded.set_alpha(alpha)
    screen.blit(faded, rect)


def _render_objective_popup():
    """
    Draws the dim overlay, popup box and objective text onto one
    transparent surface, so the whole thing can fade in as a unit with
    a single set_alpha() call instead of fading each piece separately.
    """
    title_font = pygame.font.Font(None, 34)
    title_font.set_bold(True)

    body_font = pygame.font.Font(None, 24)

    surface = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
    )
    surface.fill((0, 0, 0, 160))

    box_width, box_height = OBJECTIVE_BOX_SIZE
    box_rect = pygame.Rect(0, 0, box_width, box_height)
    box_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    pygame.draw.rect(
        surface, (28, 36, 26, 235), box_rect, border_radius=16
    )
    pygame.draw.rect(
        surface, (205, 180, 110, 255), box_rect, 3, border_radius=16
    )

    text_padding = 32
    max_text_width = box_width - text_padding * 2

    y = box_rect.top + 34

    for line in OBJECTIVE_TITLE_LINES:
        rect = draw_text_with_shadow(
            surface, title_font, line, (255, 235, 180),
            (box_rect.centerx, y)
        )
        y = rect.bottom + 10

    y += 12

    for paragraph in OBJECTIVE_BODY_LINES:
        for line in wrap_text(body_font, paragraph, max_text_width):
            rect = draw_text_with_shadow(
                surface, body_font, line, COLOR_TEXT,
                (box_rect.centerx, y)
            )
            y = rect.bottom + 6

        y += 10

    return surface


def _show_missing_message(screen, clock, missing):
    print("[backstory] could not load any panel files:")

    for path in missing:
        print(f"[backstory]   {path}")

    expected = os.path.join(PROJECT_ROOT, BACKSTORY_DIR)

    title_font = pygame.font.Font(None, 42)
    body_font = pygame.font.Font(None, 26)

    lines = [
        "Backstory images not found.",
        "Expected folder:",
        expected,
        "",
        "Check the console for the exact missing files.",
        "",
        "Click or press any key to continue anyway",
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type in (
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN
            ):
                return True

        screen.fill((20, 20, 20))

        for index, line in enumerate(lines):
            font = title_font if index == 0 else body_font
            color = (255, 180, 120) if index == 0 else COLOR_TEXT

            label = font.render(line, True, color)
            rect = label.get_rect(
                center=(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 90 + index * 36
                )
            )
            screen.blit(label, rect)

        pygame.display.flip()
        clock.tick(FPS)


def run_backstory(screen, clock):
    """
    Builds the 5-panel comic page one panel at a time, in place, then
    cuts to the final full-screen panel. Only meant to be called once,
    right after Start is pressed - never on restart/death.

    Returns True normally, False if the player closed the window
    (so main() can quit cleanly instead of continuing into the game).
    """
    missing = []

    grid_panels = _build_grid(missing)
    final_panel = _build_final_panel(missing)

    if not grid_panels and not final_panel:
        return _show_missing_message(screen, clock, missing)

    if missing:
        print("[backstory] some panel files could not be loaded:")

        for path in missing:
            print(f"[backstory]   {path}")

    panel_count = len(grid_panels)

    # When each grid panel starts fading in.
    panel_start_times = [
        INTRO_PAUSE_MS + i * GRID_PANEL_INTERVAL_MS
        for i in range(panel_count)
    ]

    grid_done_time = (
        (panel_start_times[-1] + GRID_PANEL_INTERVAL_MS)
        if panel_count else INTRO_PAUSE_MS
    )

    final_start_time = grid_done_time + PAGE_HOLD_MS
    final_done_time = final_start_time + FADE_MS

    objective_start_time = final_done_time + OBJECTIVE_PAUSE_MS
    objective_done_time = objective_start_time + OBJECTIVE_FADE_MS

    objective_popup = _render_objective_popup()

    hint_font = pygame.font.Font(None, 26)

    start_time = pygame.time.get_ticks()
    skipped_to_end = False
    reached_end = False

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type in (
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN
            ):
                if reached_end:
                    return True

                skipped_to_end = True

        if skipped_to_end:
            elapsed = objective_done_time
            reached_end = True
        elif elapsed >= objective_done_time:
            reached_end = True

        screen.fill((0, 0, 0))

        if elapsed < final_start_time:
            # still building (or holding on) the comic page
            for index, (surface, rect) in enumerate(grid_panels):
                panel_elapsed = elapsed - panel_start_times[index]

                if panel_elapsed < 0:
                    continue

                alpha = min(255, int(255 * panel_elapsed / FADE_MS))
                _draw_faded(screen, surface, rect, alpha)
        elif final_panel is not None:
            panel_elapsed = elapsed - final_start_time
            alpha = min(255, int(255 * panel_elapsed / FADE_MS))

            _draw_faded(screen, final_panel[0], final_panel[1], alpha)

        if elapsed >= objective_start_time:
            popup_elapsed = elapsed - objective_start_time
            popup_alpha = min(
                255, int(255 * popup_elapsed / OBJECTIVE_FADE_MS)
            )

            faded_popup = objective_popup.copy()
            faded_popup.set_alpha(popup_alpha)
            screen.blit(faded_popup, (0, 0))

        if reached_end:
            hint = hint_font.render(HINT_TEXT, True, COLOR_TEXT)
            hint_rect = hint.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28)
            )
            screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(FPS)