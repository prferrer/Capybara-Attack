import pygame


SKILL_DATA = {
    "Fire": {
        "range": 180,
        "width": 80,
        "size": 100
    },
    "Ice": {
        "range": 120,
        "width": 80,
        "size": 100
    },
    "Lightning": {
        "range": 200,
        "width": 100,
        "size": 100
    },
    "Light": {
        "range": 190,
        "width": 100,
        "size": 110
    },
    "Dark": {
        "range": 170,
        "width": 110,
        "size": 120
    },
    "Water": {
        "range": 200,
        "width": 120,
        "size": 120
    },
    "Wind": {
        "range": 220,
        "width": 100,
        "size": 110
    },
    "Earth": {
        "range": 150,
        "width": 120,
        "size": 125
    },
    "Poison": {
        "range": 175,
        "width": 100,
        "size": 105
    },
    "Explosion": {
        "range": 150,
        "width": 140,
        "size": 140
    }
}

class SkillEffect:
    def __init__(self, skill, position, facing_right):
        self.skill = skill
        self.facing_right = facing_right

        skill_sound = None

        if skill == "Fire":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/firesfx.mp3")
        elif skill == "Ice":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/icesfx.mp3")
        elif skill == "Lightning":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/lightningsfx.mp3")
        elif skill == "Light":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/lightsfx.mp3")
        elif skill == "Dark":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/darksfx.mp3")
        elif skill == "Water":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/watersfx.mp3")
        elif skill == "Wind":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/windsfx.mp3")
        elif skill == "Earth":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/earthsfx.mp3")
        elif skill == "Poison":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/poisonsfx.mp3")
        elif skill == "Explosion":
            skill_sound = pygame.mixer.Sound("assets/audio/skills/explosionsfx.mp3")

        if skill_sound:
            skill_sound.set_volume(0.7)
            skill_sound.play()

        self.images = []

        skill_size = SKILL_DATA.get(
            skill,
            SKILL_DATA["Fire"]
        )["size"]

        frame_count = 5 if skill in (
            "Fire",
            "Ice",
            "Lightning"
        ) else 6

        for i in range(1, frame_count + 1):

            if skill == "Fire":
                filename = (
                    f"assets/images/skills/fire_right{i}.png"
                )
            elif skill == "Ice":
                filename = (
                    f"assets/images/skills/ice{i}.png"
                )
            elif skill == "Lightning":
                filename = (
                    f"assets/images/skills/lightning{i}.png"
                )
            else:
                filename = (
                    f"assets/images/skills/{skill.lower()}{i}.png"
                )

            image = pygame.image.load(
                filename
            ).convert_alpha()

            image = pygame.transform.scale(
                image,
                (skill_size, skill_size)
            )

            self.images.append(image)

        self.position = position
        self.frame = 0
        self.timer = 0
        self.finished = False

    def update(self):
        self.timer += 1

        if self.timer >= 5:
            self.timer = 0
            self.frame += 1

            if self.frame >= len(self.images):
                self.finished = True

    def draw(self, screen):
        if self.frame >= len(self.images):
            return

        image = self.images[self.frame]

        if not self.facing_right:
            image = pygame.transform.flip(
                image,
                True,
                False
            )

        x = (
            self.position[0]
            - image.get_width() // 2
        )

        y = (
            self.position[1]
            - image.get_height() // 2
        )

        screen.blit(
            image,
            (x, y)
        )

    @staticmethod
    def get_range(skill):
        return SKILL_DATA.get(
            skill,
            SKILL_DATA["Fire"]
        )["range"]

    @staticmethod
    def get_width(skill):
        return SKILL_DATA.get(
            skill,
            SKILL_DATA["Fire"]
        )["width"]