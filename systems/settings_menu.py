import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_TEXT,
    COLOR_BORDER
)

_levels = {
    "master": 1.0,
    "music": 1.0,
    "sfx": 1.0
}

_muted = [False]

def get_level(name):
    return _levels[name]

def set_level(name, value):
    _levels[name] = max(0.0, min(1.0, value))
    _apply_music_volume()

def is_muted():
    return _muted[0]

def set_muted(value):
    _muted[0] = bool(value)
    _apply_music_volume()

def _effective(channel):
    if _muted[0]:
        return 0.0

    return _levels["master"] * _levels[channel]

_previous_sound_factory = pygame.mixer.Sound

class _VolumeSound:
    def __init__(self, inner):
        self._inner = inner
        self._base_volume = 1.0

    def play(self, *args, **kwargs):
        self._inner.set_volume(
            self._base_volume * _effective("sfx")
        )

        return self._inner.play(*args, **kwargs)

    def set_volume(self, value):
        self._base_volume = value

    def get_volume(self):
        return self._base_volume

    def __getattr__(self, name):
        return getattr(self._inner, name)

def _sound_factory(*args, **kwargs):
    return _VolumeSound(
        _previous_sound_factory(*args, **kwargs)
    )

pygame.mixer.Sound = _sound_factory

_previous_music_set_volume = pygame.mixer.music.set_volume
_music_base_volume = [1.0]

def _apply_music_volume():
    try:
        _previous_music_set_volume(
            _music_base_volume[0] * _effective("music")
        )
    except pygame.error:
        pass

def _music_set_volume(value):
    _music_base_volume[0] = value
    _apply_music_volume()

pygame.mixer.music.set_volume = _music_set_volume

_real_get_ticks = pygame.time.get_ticks
_paused_total = [0]
_pause_started = [None]

def _game_get_ticks():
    if _pause_started[0] is not None:
        return _pause_started[0] - _paused_total[0]

    return _real_get_ticks() - _paused_total[0]

pygame.time.get_ticks = _game_get_ticks

PANEL_COLOR = (45, 55, 45)
BUTTON_COLOR = (80, 115, 65)
BUTTON_HOVER_COLOR = (110, 150, 90)
GOLD = (255, 235, 150)
TRACK_COLOR = (25, 30, 25)
FILL_COLOR = (110, 150, 90)

SLIDERS = [
    ("master", "Master Volume"),
    ("music", "Music"),
    ("sfx", "Sound Effects")
]

CONTROLS = [
    ("W A S D / Arrows", "Move your capybara."),
    ("Near an enemy", "You attack automatically."),
    ("Q  /  Weapon button", "Use your weapon skill (bottom-left)."),
    ("1 2 3  /  Skill buttons", "Cast the skills you have learned (bottom-right)."),
    ("E", "Interact: pick up items, open chests, use fountains, statues and "
          "training buddies, trade with the merchant."),
    ("SPACE", "Go to the next day (after every enemy is defeated)."),
    ("B  /  Bag icon", "Open your backpack to use or drop items."),
    ("Gear icon", "Open Settings (above the bag)."),
    ("ESC", "Close Settings or this guide."),
    ("Mouse click", "Choose skills and event cards, buy from the merchant, "
                    "press buttons."),
]

TIPS = [
    ("Survive", "Keep your HP above 0 and defeat enemies before they kill you!"),
    ("Earn Gold", "Defeat enemies to collect gold and become stronger."),
    ("Power Up", "Use your gold wisely to improve your abilities."),
    ("Game Over", "If your HP reaches 0, it's game over. Press R to restart."),
]

GUIDE = [
    ("Days & maps", "Each day you fight the enemies in a room, then press SPACE. "
                    "The map changes every 5 days (grassland, cave, snow) with "
                    "new enemies, and more of them as the days go by."),
    ("Gold & hearts", "Defeated enemies give gold and drop hearts. Walk over a "
                      "heart to heal."),
    ("Weapon skill (Q)", "Sword: Berserk (stronger + lifesteal). Katana: Dash. "
                         "Staff: Overcharge (faster, stronger skills). "
                         "Shield: Barrier (reflects damage)."),
    ("Skills", "Learn up to 3 of Fire, Ice and Lightning at the campsite. "
               "Cast them with 1 2 3 or the buttons; each has a cooldown."),
    ("Chests", "Defeat the enemies first, then press E next to a chest."),
    ("Fountains & more", "Healing fountain restores HP. Cursed fountain costs "
                         "HP but gives gold. Capy statue raises max HP. "
                         "Training buddy raises attack."),
    ("Merchant", "Press E to shop. Click an item to buy it with gold, then "
                 "CLOSE. Your backpack has limited slots."),
    ("Items & potions", "Pick them up with E, then use or drop them from the "
                        "backpack (B)."),
    ("Random events", "Sometimes a new day starts with 3 event cards. Click "
                      "one to choose. The game waits while you pick."),
]

PAGES = [
    (("CONTROLS", CONTROLS), ("TIPS", TIPS)),
    (("HOW THE GAME WORKS", GUIDE),)
]

def _wrap(font, text, max_width):
    lines = []
    line = ""

    for word in text.split():
        trial = word if not line else f"{line} {word}"

        if font.size(trial)[0] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines

class SettingsMenu:

    def __init__(self):
        self.is_open = False
        self.pausing = False
        self.view = "main"
        self.dragging = None
        self._fonts = None

        panel_w, panel_h = 560, 440
        self.panel = pygame.Rect(
            (SCREEN_WIDTH - panel_w) // 2,
            (SCREEN_HEIGHT - panel_h) // 2,
            panel_w,
            panel_h
        )

        self.tracks = {}

        for index, (key, _label) in enumerate(SLIDERS):
            self.tracks[key] = pygame.Rect(
                self.panel.left + 230,
                self.panel.top + 120 + index * 55,
                self.panel.width - 230 - 50,
                10
            )

        self.mute_rect = pygame.Rect(
            self.panel.left + 40,
            self.panel.top + 120 + len(SLIDERS) * 55 + 5,
            28,
            28
        )

        self.tutorial_button = pygame.Rect(0, 0, 220, 50)
        self.tutorial_button.midbottom = (
            self.panel.centerx - 125,
            self.panel.bottom - 30
        )

        self.close_button = pygame.Rect(0, 0, 220, 50)
        self.close_button.midbottom = (
            self.panel.centerx + 125,
            self.panel.bottom - 30
        )

        self.tutorial_back_button = pygame.Rect(0, 0, 160, 46)
        self.tutorial_prev_button = pygame.Rect(0, 0, 160, 46)
        self.tutorial_next_button = pygame.Rect(0, 0, 160, 46)
        self.tutorial_page = 0

    def open(self, pause_game=False):
        """pause_game=True (used in the game) also freezes the game clock."""
        self.is_open = True
        self.view = "main"
        self.dragging = None
        self.pausing = pause_game

        if pause_game and _pause_started[0] is None:
            _pause_started[0] = _real_get_ticks()

    def close(self):
        self.is_open = False
        self.view = "main"
        self.dragging = None
        self.pausing = False

        if _pause_started[0] is not None:
            _paused_total[0] += _real_get_ticks() - _pause_started[0]
            _pause_started[0] = None

    def _set_from_x(self, key, x):
        track = self.tracks[key]
        set_level(key, (x - track.left) / track.width)

    def handle_event(self, event):

        if not self.is_open:
            return False

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            if self.view == "tutorial":
                self.view = "main"
            else:
                self.close()

            return True

        left_click = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        )

        if self.view == "tutorial":
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_RIGHT
            ):
                self.tutorial_page = min(
                    self.tutorial_page + 1, len(PAGES) - 1
                )

            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_LEFT
            ):
                self.tutorial_page = max(self.tutorial_page - 1, 0)

            elif left_click:
                if self.tutorial_back_button.collidepoint(event.pos):
                    self.view = "main"

                elif (
                    self.tutorial_page < len(PAGES) - 1
                    and self.tutorial_next_button.collidepoint(event.pos)
                ):
                    self.tutorial_page += 1

                elif (
                    self.tutorial_page > 0
                    and self.tutorial_prev_button.collidepoint(event.pos)
                ):
                    self.tutorial_page -= 1

            return True

        if left_click:

            for key, track in self.tracks.items():
                if track.inflate(24, 30).collidepoint(event.pos):
                    self.dragging = key
                    self._set_from_x(key, event.pos[0])
                    return True

            if self.mute_rect.inflate(260, 10).collidepoint(event.pos):
                set_muted(not is_muted())

            elif self.tutorial_button.collidepoint(event.pos):
                self.view = "tutorial"
                self.tutorial_page = 0

            elif self.close_button.collidepoint(event.pos):
                self.close()

        elif (
            event.type == pygame.MOUSEMOTION
            and self.dragging
        ):
            self._set_from_x(self.dragging, event.pos[0])

        elif (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
        ):
            self.dragging = None

        return True

    def _get_fonts(self):
        if self._fonts is None:
            self._fonts = {
                "title": pygame.font.Font(None, 56),
                "pause": pygame.font.Font(None, 26),
                "label": pygame.font.Font(None, 32),
                "button": pygame.font.Font(None, 32),
                "head": pygame.font.Font(None, 30),
                "key": pygame.font.Font(None, 24),
                "text": pygame.font.Font(None, 24)
            }

        return self._fonts

    def _draw_button(self, screen, rect, text, mouse):
        fonts = self._get_fonts()

        pygame.draw.rect(
            screen,
            BUTTON_HOVER_COLOR
            if rect.collidepoint(mouse)
            else BUTTON_COLOR,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            COLOR_BORDER,
            rect,
            3,
            border_radius=12
        )

        label = fonts["button"].render(text, True, COLOR_TEXT)
        screen.blit(label, label.get_rect(center=rect.center))

    def _draw_overlay_and_panel(self, screen, panel):
        overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=15)
        pygame.draw.rect(screen, COLOR_BORDER, panel, 4, border_radius=15)

    def draw(self, screen):
        if not self.is_open:
            return

        if self.view == "tutorial":
            self._draw_tutorial(screen)
        else:
            self._draw_main(screen)

    def _draw_main(self, screen):
        fonts = self._get_fonts()
        mouse = pygame.mouse.get_pos()

        self._draw_overlay_and_panel(screen, self.panel)

        title = fonts["title"].render("SETTINGS", True, GOLD)
        screen.blit(
            title,
            title.get_rect(
                midtop=(self.panel.centerx, self.panel.top + 25)
            )
        )

        if self.pausing:
            paused = fonts["pause"].render(
                "GAME PAUSED  -  press ESC or click Close to resume",
                True,
                (255, 150, 130)
            )
            screen.blit(
                paused,
                paused.get_rect(
                    midtop=(self.panel.centerx, self.panel.top + 78)
                )
            )

        dimmed = is_muted()

        for key, label_text in SLIDERS:
            track = self.tracks[key]
            level = get_level(key)

            label = fonts["label"].render(
                label_text,
                True,
                (150, 150, 150) if dimmed else COLOR_TEXT
            )
            screen.blit(
                label,
                label.get_rect(
                    midleft=(self.panel.left + 40, track.centery)
                )
            )

            pygame.draw.rect(screen, TRACK_COLOR, track, border_radius=5)

            fill = pygame.Rect(
                track.left,
                track.top,
                int(track.width * level),
                track.height
            )
            pygame.draw.rect(
                screen,
                (95, 95, 95) if dimmed else FILL_COLOR,
                fill,
                border_radius=5
            )

            pygame.draw.rect(
                screen, COLOR_BORDER, track, 2, border_radius=5
            )

            pygame.draw.circle(
                screen,
                (150, 150, 150) if dimmed else GOLD,
                (track.left + int(track.width * level), track.centery),
                11
            )
            pygame.draw.circle(
                screen,
                (40, 40, 40),
                (track.left + int(track.width * level), track.centery),
                11,
                2
            )

        pygame.draw.rect(screen, TRACK_COLOR, self.mute_rect, border_radius=6)
        pygame.draw.rect(
            screen, COLOR_BORDER, self.mute_rect, 2, border_radius=6
        )

        if is_muted():
            pygame.draw.line(
                screen, GOLD,
                (self.mute_rect.left + 6, self.mute_rect.centery),
                (self.mute_rect.centerx - 2, self.mute_rect.bottom - 7),
                4
            )
            pygame.draw.line(
                screen, GOLD,
                (self.mute_rect.centerx - 2, self.mute_rect.bottom - 7),
                (self.mute_rect.right - 6, self.mute_rect.top + 7),
                4
            )

        mute_label = fonts["label"].render(
            "Mute all sound", True, COLOR_TEXT
        )
        screen.blit(
            mute_label,
            mute_label.get_rect(
                midleft=(self.mute_rect.right + 14, self.mute_rect.centery)
            )
        )

        self._draw_button(screen, self.tutorial_button, "How to Play", mouse)
        self._draw_button(screen, self.close_button, "Close", mouse)

    def _draw_tutorial(self, screen):
        fonts = self._get_fonts()
        mouse = pygame.mouse.get_pos()

        panel = pygame.Rect(0, 0, 880, SCREEN_HEIGHT - 20)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self._draw_overlay_and_panel(screen, panel)

        title = fonts["title"].render("HOW TO PLAY", True, GOLD)
        screen.blit(
            title,
            title.get_rect(midtop=(panel.centerx, panel.top + 14))
        )

        key_x = panel.left + 35
        text_x = panel.left + 270
        text_width = panel.right - 35 - text_x
        line_height = 20
        y = panel.top + 68

        for heading, rows in PAGES[self.tutorial_page]:
            head = fonts["head"].render(heading, True, GOLD)
            screen.blit(head, (key_x, y))
            y += 28

            for key_text, description in rows:
                key_surface = fonts["key"].render(key_text, True, GOLD)
                screen.blit(key_surface, (key_x, y))

                for line in _wrap(fonts["text"], description, text_width):
                    line_surface = fonts["text"].render(
                        line, True, COLOR_TEXT
                    )
                    screen.blit(line_surface, (text_x, y))
                    y += line_height

                y += 3

            y += 6

        self.tutorial_back_button.midbottom = (
            panel.centerx,
            panel.bottom - 12
        )
        self._draw_button(screen, self.tutorial_back_button, "Back", mouse)

        self.tutorial_prev_button.midbottom = (
            panel.centerx - 200,
            panel.bottom - 12
        )
        self.tutorial_next_button.midbottom = (
            panel.centerx + 200,
            panel.bottom - 12
        )

        if self.tutorial_page > 0:
            self._draw_button(
                screen, self.tutorial_prev_button, "< Prev", mouse
            )

        if self.tutorial_page < len(PAGES) - 1:
            self._draw_button(
                screen, self.tutorial_next_button, "Next >", mouse
            )

        page_label = fonts["key"].render(
            f"Page {self.tutorial_page + 1} / {len(PAGES)}",
            True,
            (200, 200, 200)
        )
        screen.blit(
            page_label,
            page_label.get_rect(
                midright=(panel.right - 30, panel.top + 34)
            )
        )

menu = SettingsMenu()