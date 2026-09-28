import pygame


class SkillEffect:
    def __init__(self, skill, position, facing_right):
        self.skill = skill
        self.facing_right = facing_right

        self.images = []

        for i in range(1, 6):
            if skill == "Fire":
                filename = f"assets/images/skills/skills/fire_right{i}.png"
            elif skill == "Ice":
                filename = f"assets/images/skills/ice{i}.png"
            else:
                filename = f"assets/images/skills/lightning{i}.png"

            image = pygame.image.load(
                filename
            ).convert_alpha()

            image = pygame.transform.scale(
                image,
                (96, 96)
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

            if self.frame >= 5:
                self.finished = True

    def draw(self, screen):
        image = self.images[self.frame]

        if self.skill == "Fire" and not self.facing_right:
            image = pygame.transform.flip(
                image,
                True,
                False
            )

        x = self.position[0] - image.get_width() // 2
        y = self.position[1] - image.get_height() // 2

        screen.blit(image, (x, y))