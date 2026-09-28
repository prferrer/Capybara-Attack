import os

import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_TEXT,
    COLOR_BORDER,
)

# Video shown (and looped) on the start screen.
# Any format OpenCV can read works (.mp4, .avi, .webm ...).
VIDEO_PATH = "assets/videos/capybara-loading.mp4"

# resolve relative to the project folder, not the terminal's current folder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where the buttons go, as a fraction of the VIDEO area (not the window).
# The title "Capybara Attack" is baked into the video, so the buttons sit
# just under it. Tweak these two numbers to move them.
BUTTONS_CENTER_X = 0.51   # 0 = left edge, 1 = right edge
BUTTONS_CENTER_Y = 0.43   # 0 = top of video, 1 = bottom of video

try:
    import cv2
except ImportError:  # game still runs, just without the video
    cv2 = None


class LoopingVideo:
    """
    Plays a video as pygame frames and restarts it when it ends.
    The video keeps its aspect ratio: it is scaled to the window width and
    centered vertically (black bars if the window is taller than the video).
    """

    def __init__(self, path):
        self.capture = None
        self.frame_surface = None
        self.frame_time = 1000 / 30
        self.next_frame_at = 0
        self.error = None
        self.hint = None

        # area of the window the video occupies (whole window until known)
        self.rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

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
            self.hint = "Video file not found - see console for the path it looked in"
        else:
            capture = cv2.VideoCapture(path)

            if not capture.isOpened():
                self.error = f"OpenCV could not open the video: {path}"
                self.hint = "OpenCV could not open the video - see console"
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

        video_h = round(SCREEN_WIDTH * src_h / src_w)
        self.size = (SCREEN_WIDTH, video_h)
        self.rect = pygame.Rect(
            0, (SCREEN_HEIGHT - video_h) // 2, SCREEN_WIDTH, video_h
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

        if self.frame_surface is not None and now < self.next_frame_at:
            return

        ok, frame = self.capture.read()

        if not ok:
            # end of video -> jump back to the first frame (loop forever)
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.capture.read()

            if not ok:
                return

        if (frame.shape[1], frame.shape[0]) != self.size:
            frame = cv2.resize(frame, self.size)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.frame_surface = pygame.image.frombuffer(
            frame.tobytes(), self.size, "RGB"
        )

        # keep a steady frame rate; if we fell behind, don't try to catch up
        self.next_frame_at += self.frame_time

        if now - self.next_frame_at > self.frame_time * 3:
            self.next_frame_at = now + self.frame_time

    def draw(self, screen, hint_font):
        screen.fill((0, 0, 0))

        if self.frame_surface is not None:
            screen.blit(self.frame_surface, self.rect.topleft)
            return

        # Fallback if the video can't play: plain gradient plus a small
        # hint at the bottom saying why. The game still starts.
        for y in range(SCREEN_HEIGHT):
            shade = 25 + int(40 * y / SCREEN_HEIGHT)
            pygame.draw.line(
                screen, (shade, shade + 15, shade),
                (0, y), (SCREEN_WIDTH, y)
            )

        if self.hint:
            draw_text_with_shadow(
                screen, hint_font, self.hint, (255, 200, 120),
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
            )

    def close(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None


def draw_text_with_shadow(screen, font, text, color, center):
    shadow = font.render(text, True, (0, 0, 0))
    label = font.render(text, True, color)

    label_rect = label.get_rect(center=center)

    screen.blit(shadow, label_rect.move(2, 2))
    screen.blit(label, label_rect)

    return label_rect


def draw_tutorial(screen, title_font, font, back_rect, hovering_back):
    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
    )
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    draw_text_with_shadow(
        screen, title_font, "HOW TO PLAY", COLOR_TEXT,
        (SCREEN_WIDTH // 2, 90)
    )

    lines = [
        "W A S D / Arrow keys  -  Move your capybara",
        "Stay close to an enemy  -  You attack automatically",
        "E  -  Choose a skill at the campsite",
        "Click the skill button (bottom right)  -  Cast your skill",
        "SPACE  -  Go to the next day",
        "",
        "Defeat enemies to earn gold. Don't let your HP hit 0!",
    ]

    for index, line in enumerate(lines):
        if line:
            draw_text_with_shadow(
                screen, font, line, COLOR_TEXT,
                (SCREEN_WIDTH // 2, 180 + index * 50)
            )

    color = (255, 235, 150) if hovering_back else COLOR_TEXT
    draw_text_with_shadow(screen, font, "< Back", color, back_rect.center)


def run_start_screen(screen, clock):
    """
    Shows the looping video with Start / Tutorial buttons.
    Returns True when the player presses Start, False if they quit.
    """
    title_font = pygame.font.Font(None, 96)
    button_font = pygame.font.Font(None, 52)
    text_font = pygame.font.Font(None, 34)

    hint_font = pygame.font.Font(None, 24)

    video = LoopingVideo(VIDEO_PATH)

    # Buttons sit under the title baked into the video.
    center_x = int(SCREEN_WIDTH * BUTTONS_CENTER_X)
    center_y = video.rect.top + int(video.rect.height * BUTTONS_CENTER_Y)

    # START button on the left, "Tutorial" text button beside it.
    start_rect = pygame.Rect(0, 0, 200, 60)
    start_rect.center = (center_x - 95, center_y)

    tutorial_center = (center_x + 145, center_y)
    tutorial_rect = pygame.Rect(0, 0, 160, 50)
    tutorial_rect.center = tutorial_center

    back_rect = pygame.Rect(0, 0, 140, 50)
    back_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)

    showing_tutorial = False
    result = False
    running = True

    while running:
        mouse_position = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                result = False
                running = False

            elif event.type == pygame.KEYDOWN:
                if showing_tutorial:
                    if event.key == pygame.K_ESCAPE:
                        showing_tutorial = False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    result = True
                    running = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if showing_tutorial:
                    if back_rect.collidepoint(mouse_position):
                        showing_tutorial = False
                elif start_rect.collidepoint(mouse_position):
                    result = True
                    running = False
                elif tutorial_rect.collidepoint(mouse_position):
                    showing_tutorial = True

        video.update()
        video.draw(screen, hint_font)

        if showing_tutorial:
            draw_tutorial(
                screen,
                title_font,
                text_font,
                back_rect,
                back_rect.collidepoint(mouse_position)
            )
        else:
            # Start button
            hovering_start = start_rect.collidepoint(mouse_position)
            fill = (110, 150, 90) if hovering_start else (80, 115, 65)

            pygame.draw.rect(screen, fill, start_rect, border_radius=12)
            pygame.draw.rect(
                screen, COLOR_BORDER, start_rect, 3, border_radius=12
            )
            draw_text_with_shadow(
                screen, button_font, "START", COLOR_TEXT, start_rect.center
            )

            # Tutorial text button (underlined + yellow on hover)
            hovering_tutorial = tutorial_rect.collidepoint(mouse_position)
            color = (255, 235, 150) if hovering_tutorial else COLOR_TEXT
            label_rect = draw_text_with_shadow(
                screen, text_font, "Tutorial", color, tutorial_center
            )

            if hovering_tutorial:
                pygame.draw.line(
                    screen,
                    color,
                    (label_rect.left, label_rect.bottom + 2),
                    (label_rect.right, label_rect.bottom + 2),
                    2
                )

        pygame.display.flip()
        clock.tick(FPS)

    video.close()

    return result
