import pygame

from settings import (
    PLAYER_SIZE,
    PLAYER_SPEED,
    ROOM_X,
    ROOM_Y,
    ROOM_WIDTH,
    ROOM_HEIGHT,
    TILE_SIZE
)

MAX_HP_LIMIT = 300
MAX_ATTACK_LIMIT = 100
MAX_DEFENSE_LIMIT = 50
MAX_GOLD_LIMIT = 9999

SKILL_COOLDOWNS = {
    "Fire": 3000,
    "Ice": 4000,
    "Lightning": 5000,
    "Light": 4000,
    "Dark": 5000,
    "Water": 3500,
    "Wind": 3000,
    "Earth": 5000,
    "Poison": 3500,
    "Explosion": 6000
}


class Player:
    def __init__(self, x, y, weapon_type="sword"):
        self.rect = pygame.Rect(
            x,
            y,
            PLAYER_SIZE,
            PLAYER_SIZE
        )

        self.speed = PLAYER_SPEED

        weapon_stats = {
            "sword": {
                "hp": 100,
                "attack": 10,
                "defense": 5,
                "skill_slots": 3
            },
            "katana": {
                "hp": 80,
                "attack": 16,
                "defense": 2,
                "skill_slots": 2
            },
            "staff": {
                "hp": 85,
                "attack": 8,
                "defense": 3,
                "skill_slots": 5
            },
            "shield": {
                "hp": 160,
                "attack": 4,
                "defense": 12,
                "skill_slots": 3
            }
        }

        self.weapon_type = weapon_type

        stats = weapon_stats.get(
            weapon_type,
            weapon_stats["sword"]
        )

        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.attack = stats["attack"]
        self.defense = stats["defense"]
        self.skill_slots = stats["skill_slots"]

        self.gold = 0
        self.inventory = []
        self.inventory_slots = 6
        self.gold_multiplier = 1.0
        
        #all 4 characters
        self.hit_sound = pygame.mixer.Sound("assets/audio/capyplayer/capygothit.mp3")
        self.hit_sound.set_volume(1.0)
        
        self.attack_sound = None
        self.weapon_skill_sound = None
        
        if self.weapon_type == "sword":
            self.attack_sound = pygame.mixer.Sound("assets/audio/capyplayer/sword/capyslay.mp3")
            self.weapon_skill_sound = pygame.mixer.Sound("assets/audio/capyplayer/sword/berserksfx.mp3")
            
        elif self.weapon_type == "katana":
            self.attack_sound = pygame.mixer.Sound("assets/audio/capyplayer/katana/katanaslashsfx.mp3")
            self.weapon_skill_sound = pygame.mixer.Sound("assets/audio/capyplayer/katana/dashsfx.mp3")
            
        elif self.weapon_type == "staff":
            self.attack_sound = pygame.mixer.Sound("assets/audio/capyplayer/staff/staffattack.MP3")
            self.weapon_skill_sound = pygame.mixer.Sound("assets/audio/capyplayer/staff/overchargesfx.MP3")
            
        elif self.weapon_type == "shield":
            self.attack_sound = pygame.mixer.Sound("assets/audio/capyplayer/shield/shieldbash.MP3")
            self.weapon_skill_sound = pygame.mixer.Sound("assets/audio/capyplayer/shield/barriersfx.MP3")
            
        # Set volumes safely
        if self.attack_sound:
            self.attack_sound.set_volume(0.6)
            
        if self.weapon_skill_sound:
            self.weapon_skill_sound.set_volume(0.6)
        
        
        self.skills = []
        self.selected_skill = None
        self.skill_damage = 0
        self.skill_cooldowns = {}
        self.skill_last_uses = {}
        self.skill_cooldown_reduction = 0
        
        self.weapon_skill_cooldown = 0
        self.weapon_skill_last_use = -999999

        self.weapon_skill_active_until = 0
        self.weapon_skill_visual_until = 0
        self.weapon_skill_invulnerable = False
        self.weapon_skill_damage_multiplier = 1.0
        self.weapon_skill_cooldown_reduction = 0

        self.barrier_active = False
        self.lifesteal_active = False

        weapon_assets = {
            "sword": {
                "idle": "assets/images/player/idle1.png",
                "run": "assets/images/player/run{}.png",
                "attack_right": "assets/images/player/attack_right{}.png",
                "attack_left": "assets/images/player/attack_left{}.png"
            },
            "katana": {
                "idle": "assets/images/player/katana_idle1.png",
                "run": "assets/images/player/katana_running{}.png",
                "attack": "assets/images/player/katana_attacking{}.png"
            },
            "staff": {
                "idle": "assets/images/player/staff_idle1.png",
                "run": "assets/images/player/staff_running{}.png",
                "attack": "assets/images/player/staff_attacking{}.png"
            },
            "shield": {
                "idle": "assets/images/player/shield_idle1.png",
                "run": "assets/images/player/shield_run{}.png",
                "attack": "assets/images/player/shield_attack{}.png"
            }
        }

        assets = weapon_assets.get(
            self.weapon_type,
            weapon_assets["sword"]
        )

        self.idle_image = pygame.image.load(
            assets["idle"]
        ).convert_alpha()

        self.run_images = []

        for i in range(1, 6):
            image = pygame.image.load(
                assets["run"].format(i)
            ).convert_alpha()

            self.run_images.append(image)

        self.attack_right_images = []
        self.attack_left_images = []

        for i in range(1, 6):

            if "attack_right" in assets:
                right_image = pygame.image.load(
                    assets["attack_right"].format(i)
                ).convert_alpha()

                left_image = pygame.image.load(
                    assets["attack_left"].format(i)
                ).convert_alpha()

            else:
                right_image = pygame.image.load(
                    assets["attack"].format(i)
                ).convert_alpha()

                left_image = pygame.transform.flip(
                    right_image,
                    True,
                    False
                )

            self.attack_right_images.append(
                right_image
            )

            self.attack_left_images.append(
                left_image
            )

        self.idle_image = pygame.transform.scale(
            self.idle_image,
            (PLAYER_SIZE, PLAYER_SIZE)
        )

        self.run_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.run_images
        ]

        self.attack_right_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.attack_right_images
        ]

        self.attack_left_images = [
            pygame.transform.scale(
                image,
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            for image in self.attack_left_images
        ]

        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8

        self.facing_right = True
        self.is_moving = False
        self.is_attacking = False
        
    def add_gold(self, amount):
        self.gold = min(
        MAX_GOLD_LIMIT,
        self.gold + amount
    )

    def increase_attack(self, amount):
        self.attack = min(
            MAX_ATTACK_LIMIT,
            self.attack + amount
        )

    def increase_defense(self, amount):
        self.defense = min(
            MAX_DEFENSE_LIMIT,
            self.defense + amount
        )

    def increase_max_hp(self, amount):
        old_max_hp = self.max_hp

        self.max_hp = min(
            MAX_HP_LIMIT,
            self.max_hp + amount
        )

        actual_increase = self.max_hp - old_max_hp
        self.hp = min(
            self.max_hp,
            self.hp + actual_increase
        )

    def update(self, walls):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing_right = False

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing_right = True

        self.is_moving = dx != 0 or dy != 0

        self.rect.x += dx
        self.rect.y += dy

        left_limit = ROOM_X
        right_limit = ROOM_X + ROOM_WIDTH
        top_limit = ROOM_Y
        bottom_limit = ROOM_Y + ROOM_HEIGHT

        self.rect.left = max(self.rect.left, left_limit)
        self.rect.right = min(self.rect.right, right_limit)

        self.rect.top = max(self.rect.top, top_limit)
        self.rect.bottom = min(self.rect.bottom, bottom_limit)

        if self.is_attacking:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1

                if self.current_frame >= 5:
                    self.current_frame = 0
                    self.is_attacking = False

        elif self.is_moving:
            self.animation_timer += 1

            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (
                    self.current_frame + 1
                ) % 5

        else:
            self.current_frame = 0
            self.animation_timer = 0
            
    def update_weapon_skill_state(self):
        current_time = pygame.time.get_ticks()

        if (
            self.weapon_skill_active_until > 0
            and current_time >= self.weapon_skill_active_until
        ):
            self.weapon_skill_active_until = 0
            self.weapon_skill_invulnerable = False
            self.barrier_active = False
            self.lifesteal_active = False
            self.weapon_skill_damage_multiplier = 1.0
            self.weapon_skill_cooldown_reduction = 0

    def attack_enemy(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.current_frame = 0
            self.animation_timer = 0
            
            self.attack_sound.play()  # Play capyslay

    def draw(self, screen):
        current_time = pygame.time.get_ticks()
        if self.is_attacking:
            if self.facing_right:
                image = self.attack_right_images[
                    self.current_frame
                ]
            else:
                image = self.attack_left_images[
                    self.current_frame
                ]

        elif self.is_moving:
            image = self.run_images[
                self.current_frame
            ]

            if not self.facing_right:
                image = pygame.transform.flip(
                    image,
                    True,
                    False
                )

        else:
            image = self.idle_image

            if not self.facing_right:
                image = pygame.transform.flip(
                    image,
                    True,
                    False
                )

        if not self.facing_right and (
            self.is_attacking
            or self.is_moving
            or not self.is_attacking
        ):
            pass

        if self.weapon_skill_visual_until > current_time:

            if self.weapon_type == "sword":
                effect_color = (220, 45, 45)

            elif self.weapon_type == "katana":
                effect_color = (100, 220, 255)

            elif self.weapon_type == "staff":
                effect_color = (180, 80, 255)

            else:
                effect_color = (70, 150, 255)

            mask = pygame.mask.from_surface(
                image
            )

            outline = mask.outline()

            if len(outline) > 2:
                points = [
                    (
                        self.rect.x + point[0],
                        self.rect.y + point[1]
                    )
                    for point in outline
                ]

                pygame.draw.lines(
                    screen,
                    effect_color,
                    True,
                    points,
                    3
                )

            center = self.rect.center

            pygame.draw.circle(
                screen,
                effect_color,
                center,
                PLAYER_SIZE // 2 + 8,
                2
            )

            if self.weapon_type == "shield":
                pygame.draw.circle(
                    screen,
                    (90, 180, 255),
                    center,
                    PLAYER_SIZE // 2 + 14,
                    3
                )

        screen.blit(
            image,
            self.rect
        )
        
    def add_skill(self, name, damage):
            if len(self.skills) >= self.skill_slots:
                return False
    
            if name in [skill[0] for skill in self.skills]:
                return False
    
            self.skills.append((name, damage))
            
            cooldown = SKILL_COOLDOWNS.get(
                name,
                3000
            )

            self.skill_cooldowns[name] = cooldown
            self.skill_last_uses[name] = -cooldown
    
            if self.selected_skill is None:
                self.selected_skill = name
                self.skill_damage = damage
    
            return True
        
    def get_skill_cooldown(self, name):
        base_cooldown = self.skill_cooldowns.get(
            name,
            3000
        )

        return max(
            500,
            base_cooldown
            - self.skill_cooldown_reduction
            - self.weapon_skill_cooldown_reduction
        )

    def get_skill_cooldown_remaining(
        self,
        name,
        current_time
    ):
        cooldown = self.get_skill_cooldown(name)

        last_use = self.skill_last_uses.get(
            name,
            -cooldown
        )

        return max(
            0,
            cooldown
            - (
                current_time
                - last_use
            )
        )

    def select_skill(self, index):
        if 0 <= index < len(self.skills):
            self.selected_skill = self.skills[index][0]
            self.skill_damage = self.skills[index][1]
            return True

        return False

    def replace_skill(self, index, name, damage):
        if not 0 <= index < len(self.skills):
            return False

        if name in [skill[0] for skill in self.skills]:
            return False

        old_name = self.skills[index][0]

        self.skills[index] = (name, damage)

        self.skill_cooldowns.pop(
            old_name,
            None
        )

        self.skill_last_uses.pop(
            old_name,
            None
        )

        cooldown = SKILL_COOLDOWNS.get(
            name,
            3000
        )

        self.skill_cooldowns[name] = cooldown
        self.skill_last_uses[name] = -cooldown

        if self.selected_skill == old_name:
            self.select_skill(index)

        return True