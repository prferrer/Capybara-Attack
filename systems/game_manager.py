
class GameManager:
    def __init__(self):
        self.day = 1
        self.max_day = 50
        self.state = "EXPLORING"

    def next_day(self):
        if self.day < self.max_day:
            self.day += 1
            self.state = "EXPLORING"
        else:
            self.state = "BOSS"

    def is_boss_day(self):
        return self.day == self.max_day