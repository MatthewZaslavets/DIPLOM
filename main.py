import pygame
from pygame import mixer
import random
import json
import os

# --------------------------------------------------------------------------------------------------------INITIALIZATION
pygame.init()
mixer.init()
# --------------------------------------------------------------------------------------------------------GAME CONSTANTS
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
COLORS = {
    "PURPLE": (75, 0, 130),
    "GOLD": (212, 175, 55),
    "DARK_GOLD": (180, 150, 45),
    "RED": (255, 0, 0),
    "YELLOW": (255, 255, 0),
    "WHITE": (255, 255, 255),
    "BLUE": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "BLACK": (0, 0, 0),
}
FONTS = {
    "count": pygame.font.Font("assets/fonts/turok.ttf", 80),
    "score": pygame.font.Font("assets/fonts/turok.ttf", 30),
    "menu": pygame.font.Font("assets/fonts/turok.ttf", 40),
    "small": pygame.font.Font("assets/fonts/turok.ttf", 20),
    "stats": pygame.font.Font("assets/fonts/turok.ttf", 24),
    "victory": pygame.font.Font("assets/fonts/turok.ttf", 60),
    "result": pygame.font.Font("assets/fonts/turok.ttf", 80)
}
STATE_MENU = "MENU"
STATE_SELECT = "SELECT"
STATE_FIGHT = "FIGHT"
STATE_HISTORY = "HISTORY"
game_mode = "PVP"
# Setting files
SETTINGS_FILE = "SMFG_settings.json"
HISTORY_FILE = "SMFG_history.json"


# Loading settings
def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                return settings.get("music_on", True), settings.get("sound_on", True)
    except:
        pass
    return True, True


def save_settings(music_on, sound_on):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump({"music_on": music_on, "sound_on": sound_on}, f)


def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []


def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-10:], f)  # Only keeping the last 10 matches


# ------------------------------------------------------------------------------------------------------------GAME SETUP
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SUPER MASSIVE FIGHT GAME")
music_on, sound_on = load_settings()
match_history = load_history()
clock = pygame.time.Clock()
# Loading background music
mixer.music.load("assets/audio/music.mp3")
mixer.music.set_volume(0.5)
if music_on:
    mixer.music.play(-1, 0.0, 5000)
# Loading background images
bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
bg_image_effect = pygame.image.load("assets/images/background/background1.jpg").convert_alpha()
# --------------------------------------------------------------------------------------------------------GAME VARIABLES
current_state = STATE_MENU
selected_fighters = []
fighter_1 = None
fighter_2 = None
selection_stage = 0  # 0 = player 1/player, 1 = player 2/opponent
intro_count = 3
last_count_update = pygame.time.get_ticks()
round_over = False
round_over_time = 0
ROUND_OVER_COOLDOWN = 2000
game_paused = False
result_text = ""
show_result = False
pause_btn = None
# Sage's curse effect variables
sage_effect_active = False
sage_effect_start_time = 0
sage_effect_duration = 8000
last_damage_time = 0
sage_effect_target = None
sage_effect_caster = None
damage_ticks = 0
max_damage_ticks = 8
# --------------------------------------------------------------------------------------------------------CHARACTER DATA
CHARACTER_DATA = {
    "Knight": {
        "data": [162, 4, [72, 56]],
        "animations": [10, 8, 1, 7, 7, 3, 7, 3, 3],
        "sheet": "assets/images/knight/Sprites/warrior1.png",
        "sheet2": "assets/images/knight/Sprites/warrior1.png",
        "sound": "assets/audio/sword.wav",
        "stats": {
            "health": 100,
            "speed": 9,
            "special_cooldown": 6000,
            "special_cast_time": 500,
            "damage": {"attack1": 15, "attack2": 10, "special": 0},
            "attack_range": 2,
            "animation_speed": 60,
            "special_type": "global_stun",
            "block_stamina": 60,
            "damage_frames": {"attack1": 5, "attack2": 3},
            "reaction_time": (50, 250)
        }
    },
    "Mage": {
        "data": [250, 3, [112, 107]],
        "animations": [8, 8, 1, 8, 8, 3, 7, 3, 3],
        "sheet": "assets/images/mage/Sprites/mage1.png",
        "sheet2": "assets/images/mage/Sprites/mage1.png",  # Alternate sprite sheet
        "sound": "assets/audio/magic.wav",
        "stats": {
            "health": 80,
            "speed": 6,
            "special_cooldown": 4000,
            "special_cast_time": 500,
            "damage": {"attack1": 25, "attack2": 15, "special": 15},
            "attack_range": 4,
            "animation_speed": 60,
            "special_type": "global_attack",
            "block_stamina": 40,
            "damage_frames": {"attack1": 6, "attack2": 4},
            "reaction_time": (100, 400)  # Average reactions
        }
    },
    "Ranger": {
        "data": [162, 4, [72, 56]],
        "animations": [10, 8, 1, 7, 7, 3, 7, 3, 3],
        "sheet": "assets/images/ranger/Sprites/Ranger.png",
        "sheet2": "assets/images/ranger/Sprites/Ranger.png",  # Alternate sprite sheet
        "sound": "assets/audio/sword.wav",
        "stats": {
            "health": 100,
            "speed": 10,
            "special_cooldown": 3000,
            "special_cast_time": 100,
            "damage": {"attack1": 15, "attack2": 10, "special": 10},
            "attack_range": 3,
            "animation_speed": 50,
            "special_type": "screen_dash",
            "dash_speed": 25,
            "dash_distance": int(SCREEN_WIDTH * 1.5),
            "block_stamina": 60,
            "damage_frames": {"attack1": 3, "attack2": 5},
            "reaction_time": (100, 300)  # Slightly faster than average
        }
    },
    "Warlock": {
        "data": [250, 3, [112, 107]],
        "animations": [8, 8, 1, 8, 8, 3, 7, 3, 3],
        "sheet": "assets/images/warlock/Sprites/mage1.png",
        "sheet2": "assets/images/warlock/Sprites/mage1.png",  # Alternate sprite sheet
        "sound": "assets/audio/magic.wav",
        "stats": {
            "health": 90,
            "speed": 6,
            "special_cooldown": 3000,
            "special_cast_time": 500,
            "damage": {"attack1": 15, "attack2": 15, "special": 25},
            "attack_range": 3,
            "animation_speed": 55,
            "special_type": "health_steal",
            "steal_amount": 25,
            "block_stamina": 45,
            "damage_frames": {"attack1": 4, "attack2": 5},
            "reaction_time": (150, 450)  # Slower reactions = blocks less
        }
    },
    "Guardian": {
        "data": [162, 4, [72, 56]],
        "animations": [10, 8, 1, 7, 7, 3, 7, 3, 3],
        "sheet": "assets/images/guardian/Sprites/warrior1.png",
        "sheet2": "assets/images/guardian/Sprites/warrior1.png",  # Alternate sprite sheet
        "sound": "assets/audio/sword.wav",
        "stats": {
            "health": 110,
            "speed": 7,
            "special_cooldown": 2500,
            "special_cast_time": 0,
            "damage": {"attack1": 10, "attack2": 10, "special": 0},
            "attack_range": 1.5,
            "animation_speed": 55,
            "special_type": "pull_root",
            "root_duration": 2000,
            "pull_distance": 100,
            "pull_speed": 15,
            "block_stamina": 65,
            "damage_frames": {"attack1": 5, "attack2": 3},
            "reaction_time": (75, 200)  # Very fast reactions = blocks often
        }
    },
    "Sage": {
        "data": [250, 3, [112, 107]],
        "animations": [8, 8, 1, 8, 8, 3, 7, 3, 3],
        "sheet": "assets/images/sage/Sprites/mage1.png",
        "sheet2": "assets/images/sage/Sprites/mage1.png",  # Alternate sprite sheet
        "sound": "assets/audio/magic.wav",
        "stats": {
            "health": 85,
            "speed": 9,
            "special_cooldown": 10000,
            "special_cast_time": 1000,
            "damage": {"attack1": 10, "attack2": 5, "special": 0},
            "attack_range": 1.5,
            "animation_speed": 60,
            "special_type": "curse_effect",
            "block_stamina": 60,
            "damage_frames": {"attack1": 5, "attack2": 4},
            "reaction_time": (50, 150),
            "curse_damage_multiplier": 2
        }
    }
}
CHARACTER_DESCRIPTIONS = {
    "Knight": "Balanced fighter with stun special",
    "Mage": "Ranged caster with screen-wide special attack",
    "Ranger": "Fast fighter with a screen-crossing dash",
    "Warlock": "Powerful mage with life drain special ability",
    "Guardian": "Short-range fighter with pull-root capabilities",
    "Sage": "Curse master with low damage but good burst state"
}


# ---------------------------------------------------------------------------------------------------------FIGHTER CLASS
class Fighter:
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, stats, is_ai=False):
        self.player = player
        self.is_ai = is_ai
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.animation_speed = stats["animation_speed"]
        self.rect = pygame.Rect(x, y, 80, 180)
        self.vel_y = 0
        self.running = False
        self.jump_count = 0
        self.speed = stats["speed"]
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.blocking = False
        self.attack_range = stats["attack_range"]
        self.attack_start_time = 0
        self.damage_applied = False
        self.attack_target = None
        self.damage_values = stats["damage"]
        self.health = stats["health"]
        self.alive = True
        self.attack_cancelled = False
        self.steal_amount = stats.get("steal_amount", 0)
        self.block_stamina = stats["block_stamina"]
        self.current_block_stamina = self.block_stamina
        self.block_exhausted = False
        self.block_exhaust_start = 0
        self.block_exhaust_duration = 2000
        self.special_type = stats.get("special_type", None)
        self.dashing = False
        self.dash_speed = stats.get("dash_speed", 0)
        self.dash_distance = stats.get("dash_distance", SCREEN_WIDTH)
        self.dash_direction = 1
        self.has_dash_contact = False
        self.dash_start_x = 0
        self.dash_distance_traveled = 0
        self.stunned = False
        self.stun_start_time = 0
        self.stun_duration = 2000
        self.root_duration = stats.get("root_duration", 2000)
        self.rooted = False
        self.root_start_time = 0
        self.being_pulled = False
        self.pull_target_x = 0
        self.pull_speed = stats.get("pull_speed", 15)
        self.special_cooldown = 0
        self.special_last_used = 0
        self.stats = stats
        self.last_block_attempt = 0
        self.reaction_time = stats.get("reaction_time", (200, 400))
        self.block_attempt_time = 0
        self.attack_detected = False
        self.defensive_mode = False
        self.curse_damage_multiplier = stats.get("curse_damage_multiplier", 1.0)

    def load_images(self, sheet, steps):
        animations = []
        for row, count in enumerate(steps):
            frames = []
            for col in range(count):
                frame = sheet.subsurface(col * self.size, row * self.size, self.size, self.size)
                scaled_frame = pygame.transform.scale(
                    frame, (self.size * self.image_scale, self.size * self.image_scale))
                frames.append(scaled_frame)
            animations.append(frames)
        return animations

    def move(self, screen_width, screen_height, surface, target, round_over):
        GRAVITY = 2
        dx = dy = 0
        self.running = False
        self.blocking = False
        if self.stunned:
            if pygame.time.get_ticks() - self.stun_start_time >= self.stun_duration:
                self.stunned = False
            return
        if self.rooted and pygame.time.get_ticks() - self.root_start_time >= self.root_duration:
            self.rooted = False
        if self.block_exhausted:
            if pygame.time.get_ticks() - self.block_exhaust_start >= self.block_exhaust_duration:
                self.block_exhausted = False
                self.current_block_stamina = self.block_stamina
            self.blocking = False
        if self.being_pulled:
            if abs(self.rect.centerx - self.pull_target_x) > self.pull_speed:
                if self.rect.centerx < self.pull_target_x:
                    self.rect.x += self.pull_speed
                else:
                    self.rect.x -= self.pull_speed
                self.hit = True
                return
            else:
                self.being_pulled = False
                self.rooted = True
                self.root_start_time = pygame.time.get_ticks()
                self.hit = True
                # Handling AI blocking
        current_time = pygame.time.get_ticks()
        if self.is_ai and not self.attacking and not self.hit and not round_over and not game_paused:
            # Checking if the character should block based on reaction time
            if (self.attack_detected and current_time >= self.block_attempt_time and
                    not self.block_exhausted and self.current_block_stamina > 0):
                self.blocking = True
                self.attack_detected = False
            # Sage-specific behavior
            if self.special_type == "curse_effect":
                if sage_effect_active and sage_effect_caster == self:
                    # Aggressive mode when curse is active - maintain optimal range and attack frequently
                    distance = abs(target.rect.centerx - self.rect.centerx)
                    attack_range = self.attack_range * self.rect.width
                    optimal_range = attack_range * 0.8  # Stay closer during curse effect

                    # More aggressive movement
                    if distance > optimal_range * 1.1:
                        # Move toward opponent more aggressively
                        dx = self.speed * (1 if target.rect.centerx > self.rect.centerx else -1) * 1.2
                        self.running = True
                    elif distance < optimal_range * 0.7:
                        # Move away slightly but not too much
                        dx = -self.speed * (1 if target.rect.centerx > self.rect.centerx else -1) * 0.5
                        self.running = True

                    # More frequent attacks during curse effect
                    if distance < attack_range * 1.2 and self.attack_cooldown == 0:
                        # Higher chance to attack during curse effect
                        if random.random() < 0.8:  # 80% chance to attack when in range
                            self.initiate_attack(1 if random.random() < 0.6 else 2, target)
                else:
                    # Defensive mode when curse is not active
                    if not sage_effect_active or sage_effect_caster != self:
                        self.defensive_mode = True
                        distance = abs(target.rect.centerx - self.rect.centerx)
                        if distance < self.attack_range * self.rect.width * 1.5:
                            if target.attacking:  # Block when being attacked
                                self.blocking = True
                            elif not self.blocking:  # Only move if not blocking
                                dx = -self.speed if target.rect.centerx > self.rect.centerx else self.speed
                                self.running = True
            # Guardian-specific behavior
            elif self.special_type == "pull_root":
                if current_time - self.special_last_used < self.stats["special_cooldown"]:
                    self.defensive_mode = True
                    distance = abs(target.rect.centerx - self.rect.centerx)
                    if distance < self.attack_range * self.rect.width * 1.5:
                        self.blocking = True
                else:
                    self.defensive_mode = False
        if not self.attacking and self.alive and not round_over and not self.hit and not game_paused:
            if self.is_ai:
                distance = target.rect.centerx - self.rect.centerx
                abs_distance = abs(distance)
                direction = 1 if distance > 0 else -1
                attack_range = self.attack_range * self.rect.width
                current_time = pygame.time.get_ticks()
                direct_distance = abs_distance
                wrapped_distance = screen_width - abs_distance
                use_wrapped_path = wrapped_distance < direct_distance
                if use_wrapped_path:
                    abs_distance = wrapped_distance
                    direction *= -1
                # Calculating optimal range based on character type
                if self.special_type in ["global_attack", "health_steal"] or \
                        (self.special_type == "curse_effect" and sage_effect_active and sage_effect_caster == self):
                    optimal_range = attack_range * 1.2  # Slightly beyond attack range for ranged characters
                else:
                    optimal_range = attack_range * 0.9  # Close for melee characters
                    # Knight AI
                if self.special_type == "global_stun":
                    if (current_time - self.special_last_used >= self.stats["special_cooldown"] and
                            abs_distance > attack_range * 1.5):
                        self.initiate_attack(8, target)
                    elif abs_distance < attack_range * 1.1 and self.attack_cooldown == 0:
                        self.initiate_attack(1 if random.random() < 0.7 else 2, target)
                    else:
                        if not self.blocking:
                            if abs_distance > optimal_range:
                                dx = self.speed * direction
                                self.running = True
                            elif abs_distance < optimal_range * 0.8:
                                dx = -self.speed * direction
                                self.running = True
                                # Wizard AI
                elif self.special_type == "global_attack":
                    if (current_time - self.special_last_used >= self.stats["special_cooldown"] and
                            abs_distance > attack_range * 1.5):
                        self.initiate_attack(8, target)
                    elif abs_distance < attack_range * 1.1 and self.attack_cooldown == 0:
                        self.initiate_attack(1 if random.random() < 0.6 else 2, target)
                    else:
                        if not self.blocking:
                            if abs_distance > optimal_range * 1.2:
                                dx = self.speed * direction * 0.8
                                self.running = True
                            elif abs_distance < optimal_range * 0.8:
                                dx = -self.speed * direction
                                self.running = True
                                # Ranger AI
                elif self.special_type == "screen_dash":
                    if (current_time - self.special_last_used >= self.stats["special_cooldown"] and
                            abs_distance > attack_range * 2):
                        self.initiate_attack(8, target)
                    elif abs_distance < attack_range * 1.1 and self.attack_cooldown == 0:
                        self.initiate_attack(1 if random.random() < 0.7 else 2, target)
                    else:
                        if not self.blocking:
                            if abs_distance > optimal_range:
                                dx = self.speed * direction
                                self.running = True
                            elif abs_distance < optimal_range * 0.8:
                                dx = -self.speed * direction
                                self.running = True
                                # Warlock AI
                elif self.special_type == "health_steal":
                    if (current_time - self.special_last_used >= self.stats["special_cooldown"] and
                            optimal_range * 0.9 < abs_distance < optimal_range * 1.1):
                        self.initiate_attack(8, target)

                    if abs_distance < attack_range * 1.1 and self.attack_cooldown == 0:
                        self.initiate_attack(1 if random.random() < 0.6 else 2, target)
                    else:
                        if not self.blocking:
                            if abs_distance > optimal_range * 1.1:
                                dx = self.speed * direction * 0.7
                                self.running = True
                            elif abs_distance < optimal_range * 0.9:
                                dx = -self.speed * direction * 0.7
                                self.running = True
                                # Guardian AI
                elif self.special_type == "pull_root":
                    if target.rooted:
                        if abs_distance < attack_range * 1.1:
                            if self.attack_cooldown == 0:
                                self.initiate_attack(1 if random.random() < 0.8 else 2, target)
                        else:
                            if not self.blocking:
                                dx = self.speed * direction
                                self.running = True
                    elif (current_time - self.special_last_used >= self.stats["special_cooldown"]):
                        self.initiate_attack(8, target)
                    else:
                        if abs_distance < attack_range * 2:
                            if not self.blocking:
                                dx = -self.speed * direction
                                self.running = True
                        elif abs_distance > attack_range * 3:
                            if not self.blocking:
                                dx = self.speed * direction * 0.5
                                self.running = True
                                # Sage AI
                elif self.special_type == "curse_effect":
                    if sage_effect_active and sage_effect_caster == self:
                        # Aggressive mode when curse is active - maintain optimal range and attack frequently
                        if abs_distance < attack_range * 1.2 and self.attack_cooldown == 0:
                            # Higher chance to attack during curse effect
                            if random.random() < 0.8:  # 80% chance to attack when in range
                                self.initiate_attack(1 if random.random() < 0.7 else 2, target)
                        else:
                            if not self.blocking:
                                # More aggressive movement during curse effect
                                if abs_distance > optimal_range * 1.1:
                                    dx = self.speed * direction * 1.2  # Faster movement toward opponent
                                    self.running = True
                                elif abs_distance < optimal_range * 0.7:
                                    dx = -self.speed * direction * 0.8  # Slightly back off
                                    self.running = True
                    else:
                        # Defensive mode when curse is not active
                        if (current_time - self.special_last_used >= self.stats["special_cooldown"]):
                            if abs_distance > attack_range * 2.5:
                                self.initiate_attack(8, target)
                            else:
                                if target.attacking:  # Block when being attacked
                                    self.blocking = True
                                elif not self.blocking:  # Only move if not blocking
                                    dx = -self.speed * direction
                                    self.running = True
                        else:
                            if abs_distance < attack_range * 1.1 and self.attack_cooldown == 0:
                                self.initiate_attack(1 if random.random() < 0.6 else 2, target)
                                # Player controls
            else:
                keys = pygame.key.get_pressed()
                if self.player == 1:
                    if keys[pygame.K_s] and not self.block_exhausted:
                        self.blocking = True
                    elif keys[pygame.K_y]:
                        self.initiate_attack(8, target)
                    else:
                        if not self.rooted:
                            if keys[pygame.K_a]:
                                dx = -self.speed
                                self.running = True
                            if keys[pygame.K_d]:
                                dx = self.speed
                                self.running = True
                        if keys[pygame.K_w] and self.jump_count < 1 and not self.rooted:
                            self.vel_y = -30
                            self.jump_count += 1
                        if keys[pygame.K_r]:
                            self.initiate_attack(1, target)
                        elif keys[pygame.K_t]:
                            self.initiate_attack(2, target)
                else:
                    if keys[pygame.K_DOWN] and not self.block_exhausted:
                        self.blocking = True
                    elif keys[pygame.K_KP3]:
                        self.initiate_attack(8, target)
                    else:
                        if not self.rooted:
                            if keys[pygame.K_LEFT]:
                                dx = -self.speed
                                self.running = True
                            if keys[pygame.K_RIGHT]:
                                dx = self.speed
                                self.running = True
                        if keys[pygame.K_UP] and self.jump_count < 1 and not self.rooted:
                            self.vel_y = -30
                            self.jump_count += 1
                        if keys[pygame.K_KP1]:
                            self.initiate_attack(1, target)
                        elif keys[pygame.K_KP2]:
                            self.initiate_attack(2, target)
        if self.dashing and not self.hit and not game_paused:
            dx = self.dash_speed * self.dash_direction * 3
            self.rect.x += dx
            self.dash_distance_traveled += abs(dx)
            # Checking for collision with the opponent during dash
            if not self.has_dash_contact and self.rect.colliderect(target.rect):
                self.has_dash_contact = True
                if not target.blocking or target.block_exhausted:
                    target.health -= self.damage_values["special"]
                    target.hit = True
                    target.stunned = False
                elif target.blocking and not target.block_exhausted:
                    target.current_block_stamina -= self.damage_values["special"]
                    if target.current_block_stamina <= 0:
                        target.block_exhausted = True
                        target.block_exhaust_start = pygame.time.get_ticks()
                        target.blocking = False
            if self.dash_distance_traveled >= self.dash_distance:
                self.dashing = False
                self.has_dash_contact = False
                self.dash_distance_traveled = 0
        else:
            self.vel_y += GRAVITY
            dy += self.vel_y
        if self.rect.right < 0:
            self.rect.left = screen_width
        elif self.rect.left > screen_width:
            self.rect.right = 0
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            dy = screen_height - 110 - self.rect.bottom
            self.jump_count = 0
        direct_distance = abs(target.rect.centerx - self.rect.centerx)
        wrapped_distance = screen_width - direct_distance
        if direct_distance < wrapped_distance:
            self.flip = target.rect.centerx < self.rect.centerx
        else:
            self.flip = target.rect.centerx > self.rect.centerx
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if not self.rooted and not self.being_pulled and not self.dashing:
            self.rect.x += dx
        self.rect.y += dy

    def initiate_attack(self, attack_type, target):
        if self.hit or game_paused:
            return
        # Notifying target about an upcoming attack
        if target.is_ai:
            reaction_delay = random.randint(target.reaction_time[0], target.reaction_time[1])
            target.block_attempt_time = pygame.time.get_ticks() + reaction_delay
            target.attack_detected = True
        if attack_type == 8:
            current_time = pygame.time.get_ticks()
            if current_time - self.special_last_used < self.stats["special_cooldown"]:
                return
            self.attacking = True
            self.attack_type = 8
            if sound_on:
                self.attack_sound.play()
            self.attack_start_time = current_time
            self.damage_applied = False
            self.attack_target = target
            self.attack_cancelled = False
            self.special_last_used = 0
            if self.stats["special_cast_time"] == 0:
                self.apply_special_effect()
        elif self.attack_cooldown == 0:
            self.attacking = True
            self.attack_type = attack_type
            if sound_on:
                self.attack_sound.play()
            self.attack_start_time = pygame.time.get_ticks()
            self.damage_applied = False
            self.attack_target = target
            self.attack_cancelled = False
            if ((attack_type == 1 and self.stats["damage_frames"]["attack1"] == 1) or
                    (attack_type == 2 and self.stats["damage_frames"]["attack2"] == 1)):
                self.apply_attack_damage()

    def update(self):
        if game_paused:
            return
        current_time = pygame.time.get_ticks()
        if self.hit and self.attacking:
            self.attacking = False
            self.attack_cancelled = True
            self.dashing = False
            self.set_action(5)
            return
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.set_action(6)
        elif self.hit:
            self.set_action(5)
            self.stunned = False
        elif self.dashing:
            self.set_action(8)
        elif self.attacking:
            if self.attack_type == 1:
                self.set_action(3)
                if (self.frame_index + 1) == self.stats["damage_frames"]["attack1"] and not self.damage_applied:
                    self.apply_attack_damage()
            elif self.attack_type == 2:
                self.set_action(4)
                if (self.frame_index + 1) == self.stats["damage_frames"]["attack2"] and not self.damage_applied:
                    self.apply_attack_damage()
            elif self.attack_type == 8:
                self.set_action(8)
                if not self.damage_applied and not self.attack_cancelled:
                    cast_progress = current_time - self.attack_start_time
                    if cast_progress < self.stats["special_cast_time"]:
                        if self.frame_index >= len(self.animation_list[self.action]) - 1:
                            self.frame_index = 0
                    else:
                        self.apply_special_effect()
        elif self.blocking:
            self.set_action(7)
        elif self.jump_count > 0 and self.vel_y < 0:
            self.set_action(2)
        elif self.running:
            self.set_action(1)
        else:
            self.set_action(0)
        if not (self.attacking and self.attack_type == 8 and not self.damage_applied and
                (current_time - self.attack_start_time) < self.stats["special_cast_time"]):
            if current_time - self.update_time > self.animation_speed:
                self.frame_index += 1
                self.update_time = current_time
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action in (3, 4):
                    if not self.damage_applied and not self.attack_cancelled:
                        self.apply_attack_damage()
                    self.attacking = False
                    self.damage_applied = True
                    self.attack_cooldown = 20
                elif self.action == 8:
                    if not self.damage_applied and not self.attack_cancelled:
                        if (current_time - self.attack_start_time) >= self.stats["special_cast_time"]:
                            self.apply_special_effect()
                    self.attacking = False
                    self.damage_applied = True
                elif self.action == 5:
                    self.hit = False
                    self.attack_cooldown = 20
                elif self.action == 7:
                    self.blocking = False
        self.image = self.animation_list[self.action][self.frame_index]

    def apply_special_effect(self):
        current_time = pygame.time.get_ticks()
        if self.attack_cancelled:
            return
        if self.special_type == "global_attack":
            if self.attack_target:
                if self.attack_target.blocking and not self.attack_target.block_exhausted:
                    damage = min(self.damage_values["special"], self.attack_target.current_block_stamina)
                    self.attack_target.current_block_stamina -= damage
                    if self.attack_target.current_block_stamina <= 0:
                        self.attack_target.block_exhausted = True
                        self.attack_target.block_exhaust_start = current_time
                        self.attack_target.blocking = False
                        remaining_damage = abs(self.attack_target.current_block_stamina)
                        self.attack_target.health -= remaining_damage
                        self.attack_target.hit = True
                else:
                    self.attack_target.health -= self.damage_values["special"]
                    self.attack_target.hit = True
                self.damage_applied = True
                self.special_last_used = current_time
        elif self.special_type == "global_stun":
            if self.attack_target and not self.attack_target.stunned:
                self.attack_target.stunned = True
                self.attack_target.stun_start_time = current_time
                if self.attack_target.attacking:
                    self.attack_target.attack_cancelled = True
                    self.attack_target.attacking = False
                    self.attack_target.dashing = False
                self.damage_applied = True
                self.special_last_used = current_time
        elif self.special_type == "health_steal":
            if self.attack_target:
                attack_area = pygame.Rect(
                    self.rect.centerx - (self.attack_range * self.rect.width * self.flip),
                    self.rect.y,
                    self.attack_range * self.rect.width,
                    self.rect.height
                )
                if attack_area.colliderect(self.attack_target.rect):
                    if self.attack_target.blocking and not self.attack_target.block_exhausted:
                        damage = min(self.steal_amount, self.attack_target.current_block_stamina)
                        self.attack_target.current_block_stamina -= damage
                        if self.attack_target.current_block_stamina <= 0:
                            self.attack_target.block_exhausted = True
                            self.attack_target.block_exhaust_start = current_time
                            self.attack_target.blocking = False
                            remaining_damage = abs(self.attack_target.current_block_stamina)
                            self.attack_target.health -= remaining_damage
                            self.attack_target.hit = True
                            steal = min(self.steal_amount, self.attack_target.health + remaining_damage)
                            self.health = min(100, self.health + steal)
                    else:
                        steal = min(self.steal_amount, self.attack_target.health)
                        self.attack_target.health -= steal
                        self.health = min(100, self.health + steal)
                        self.attack_target.hit = True
                self.damage_applied = True
                self.special_last_used = current_time
        elif self.special_type == "curse_effect":
            if self.attack_target and not self.attack_cancelled:
                global sage_effect_active, sage_effect_start_time, sage_effect_target, \
                    sage_effect_caster, last_damage_time, damage_ticks
                sage_effect_active = True
                sage_effect_start_time = current_time
                last_damage_time = sage_effect_start_time
                damage_ticks = 0
                sage_effect_target = self.attack_target
                sage_effect_caster = self
                self.damage_applied = True
                self.special_last_used = current_time
        elif self.special_type == "screen_dash":
            self.dashing = True
            self.has_dash_contact = False
            self.dash_direction = -1 if self.flip else 1
            self.dash_start_x = self.rect.centerx
            self.dash_distance_traveled = 0
            self.damage_applied = True
            self.special_last_used = current_time
        elif self.special_type == "pull_root":
            pull_direction = 1 if self.rect.centerx < self.attack_target.rect.centerx else -1
            target_x = self.rect.centerx + (self.stats["pull_distance"] * pull_direction)
            self.attack_target.being_pulled = True
            self.attack_target.pull_target_x = target_x
            self.attack_target.hit = True
            if self.attack_target.attacking:
                self.attack_target.attack_cancelled = True
                self.attack_target.attacking = False
                self.attack_target.dashing = False
            self.damage_applied = True
            self.special_last_used = current_time

    def apply_attack_damage(self):
        if self.attack_type in (1, 2, 8) and not self.attack_cancelled:
            attack_area = pygame.Rect(
                self.rect.centerx - (self.attack_range * self.rect.width * self.flip),
                self.rect.y,
                self.attack_range * self.rect.width,
                self.rect.height
            )
            if (self.attack_target and
                    attack_area.colliderect(self.attack_target.rect)):
                # Calculate damage with potential multiplier (for Sage during curse)
                damage_multiplier = self.curse_damage_multiplier if (
                        self.special_type == "curse_effect" and sage_effect_active and sage_effect_caster == self) else 1.0

                if self.attack_target.blocking and not self.attack_target.block_exhausted:
                    if self.attack_type == 1:
                        damage = min(int(self.damage_values["attack1"] * damage_multiplier),
                                     self.attack_target.current_block_stamina)
                    elif self.attack_type == 2:
                        damage = min(int(self.damage_values["attack2"] * damage_multiplier),
                                     self.attack_target.current_block_stamina)
                    else:
                        damage = min(int(self.damage_values["special"] * damage_multiplier),
                                     self.attack_target.current_block_stamina)
                    self.attack_target.current_block_stamina -= damage
                    if self.attack_target.current_block_stamina <= 0:
                        self.attack_target.block_exhausted = True
                        self.attack_target.block_exhaust_start = pygame.time.get_ticks()
                        self.attack_target.blocking = False
                        remaining_damage = abs(self.attack_target.current_block_stamina)
                        self.attack_target.health -= remaining_damage
                        self.attack_target.hit = True
                        if self.special_type == "health_steal" and self.attack_type == 8:
                            steal = min(self.steal_amount, remaining_damage)
                            self.health = min(100, self.health + steal)
                elif not self.attack_target.blocking or self.attack_target.block_exhausted:
                    if self.special_type == "health_steal" and self.attack_type == 8:
                        steal = min(self.steal_amount, self.attack_target.health)
                        self.attack_target.health -= steal
                        self.health = min(100, self.health + steal)
                        self.attack_target.hit = True
                    else:
                        if self.attack_type == 1:
                            damage = int(self.damage_values["attack1"] * damage_multiplier)
                        elif self.attack_type == 2:
                            damage = int(self.damage_values["attack2"] * damage_multiplier)
                        else:
                            damage = int(self.damage_values["special"] * damage_multiplier)
                        self.attack_target.health -= damage
                        self.attack_target.hit = True
                self.attack_target.stunned = False
        self.damage_applied = True

    def set_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        flipped_img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            flipped_img,
            (
                self.rect.x - self.offset[0] * self.image_scale,
                self.rect.y - self.offset[1] * self.image_scale
            )
        )


def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def draw_text_right(text, font, color, y, margin=20):
    surf = font.render(text, True, color)
    x = SCREEN_WIDTH - surf.get_width() - margin
    screen.blit(surf, (x, y))


def draw_button(text, x, y, w, h, font, base_color, text_color, is_pressed=False):
    if is_pressed:
        w2, h2 = int(w * 0.95), int(h * 0.95)
        x2 = x + (w - w2) // 2
        y2 = y + (h - h2) // 2
        pygame.draw.rect(screen, COLORS["DARK_GOLD"], (x2, y2, w2, h2), border_radius=8)
        rect = pygame.Rect(x2, y2, w2, h2)
    else:
        pygame.draw.rect(screen, base_color, (x, y, w, h), border_radius=8)
        rect = pygame.Rect(x, y, w, h)
    lbl = font.render(text, True, text_color)
    lx = rect.x + (rect.w - lbl.get_width()) // 2
    ly = rect.y + (rect.h - lbl.get_height()) // 2
    screen.blit(lbl, (lx, ly))
    return rect


def draw_bg():
    current_time = pygame.time.get_ticks()
    if sage_effect_active and current_time >= sage_effect_start_time and current_time <= sage_effect_start_time + sage_effect_duration:
        scaled_bg = pygame.transform.scale(bg_image_effect, (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))


def draw_health_value(health, x, y, align_left=True):
    health_text = FONTS["stats"].render(f"HP: {health}", True, COLORS["RED"])
    if align_left:
        screen.blit(health_text, (x, y))
    else:
        draw_text_right(f"HP: {health}", FONTS["stats"], COLORS["RED"], y)


def draw_stamina_value(fighter, x, y, align_left=True):
    current_time = pygame.time.get_ticks()
    if fighter.block_exhausted:
        cooldown_remaining = max(0, fighter.block_exhaust_duration - (current_time - fighter.block_exhaust_start))
        text = f"    CD: {cooldown_remaining // 1000 + 1}s"
    else:
        text = f"ST: {max(0, fighter.current_block_stamina)}/{fighter.block_stamina}"

    if align_left:
        stamina_text = FONTS["stats"].render(text, True, COLORS["GREEN"])
        screen.blit(stamina_text, (x, y))
    else:
        draw_text_right(text, FONTS["stats"], COLORS["GREEN"], y)


def draw_cooldown_value(fighter, x, y, align_left=True):
    current_time = pygame.time.get_ticks()
    cooldown_remaining = max(0, fighter.stats["special_cooldown"] - (current_time - fighter.special_last_used))
    if cooldown_remaining > 0:
        text = f"CD: {cooldown_remaining // 1000 + 1}s"
    else:
        text = "READY"

    if align_left:
        cooldown_text = FONTS["stats"].render(text, True, COLORS["BLUE"])
        screen.blit(cooldown_text, (x, y))
    else:
        draw_text_right(text, FONTS["stats"], COLORS["BLUE"], y)


def create_fighter(player_num, char_name, x_pos, flip, is_ai=False):
    char_data = CHARACTER_DATA[char_name]
    # Use alternate sprite sheet if this is player 2 and both players selected the same character
    if player_num == 2 and len(selected_fighters) == 2 and selected_fighters[0] == selected_fighters[1]:
        sheet = pygame.image.load(char_data["sheet2"]).convert_alpha()
    else:
        sheet = pygame.image.load(char_data["sheet"]).convert_alpha()
    sound = pygame.mixer.Sound(char_data["sound"])
    sound.set_volume(0.5 if "sword" in char_data["sound"] else 0.75)
    return Fighter(
        player_num, x_pos, 310, flip,
        char_data["data"], sheet, char_data["animations"], sound,
        char_data["stats"], is_ai
    )


def handle_sage_effect():
    global sage_effect_active, sage_effect_start_time, sage_effect_target, sage_effect_caster
    global last_damage_time, damage_ticks
    current_time = pygame.time.get_ticks()
    if (fighter_1 and not fighter_1.alive) or (fighter_2 and not fighter_2.alive):
        sage_effect_active = False
        return
    if sage_effect_active:
        if current_time - sage_effect_start_time >= sage_effect_duration:
            sage_effect_active = False
        else:
            if (current_time - last_damage_time >= 1000 and
                    damage_ticks < max_damage_ticks):
                if sage_effect_target and sage_effect_target.alive:
                    sage_effect_target.health -= 15
                if sage_effect_caster and sage_effect_caster.alive:
                    sage_effect_caster.health -= 5
                last_damage_time = current_time
                damage_ticks += 1


def draw_result_text(text):
    surf = FONTS["result"].render(text, True, COLORS["RED"])
    text_rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(surf, text_rect)


def add_to_history(winner, fighter1, fighter2, game_mode, premature=False):
    match_info = {
        "date": pygame.time.get_ticks(),
        "fighter1": fighter1,
        "fighter2": fighter2,
        "game_mode": game_mode,
        "winner": winner,
        "premature": premature
    }
    match_history.append(match_info)
    save_history(match_history)


def draw_history():
    screen.fill(COLORS["PURPLE"])
    title = FONTS["menu"].render("MATCH HISTORY", True, COLORS["GOLD"])
    screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 30))
    back_btn = draw_button(
        "BACK", 20, 20, 100, 40,
        FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
        pygame.Rect(20, 20, 100, 40).collidepoint((mx, my)) and md
    )
    if not match_history:
        no_history = FONTS["menu"].render("No matches played yet", True, COLORS["GOLD"])
        screen.blit(no_history, ((SCREEN_WIDTH - no_history.get_width()) // 2, SCREEN_HEIGHT // 2))
    else:
        for i, match in enumerate(reversed(match_history[-10:])):  # Show last 10 matches
            y_pos = 100 + i * 50
            if y_pos > SCREEN_HEIGHT - 100:
                break
            if match["premature"]:
                result = "Game closed"
            elif match["winner"] == "Player 1":
                result = f"{match['fighter1']} won"
            elif match["winner"] == "Player 2":
                result = f"{match['fighter2']} won"
            else:
                result = match["winner"]
            mode = "PVP" if match["game_mode"] == "PVP" else "PVE"
            match_text = f"{match['fighter1']} vs {match['fighter2']} ({mode}) - {result}"
            text = FONTS["small"].render(match_text, True, COLORS["GOLD"])
            screen.blit(text, (50, y_pos))
    return back_btn


def draw_pause_button():
    btn_text = "PAUSED" if game_paused else "PAUSE"
    btn = draw_button(
        btn_text, SCREEN_WIDTH // 2 - 50, 10, 100, 30,
        FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
                  pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 30).collidepoint((mx, my)) and md
    )
    return btn


# --------------------------------------------------------------------------------------------------------MAIN GAME LOOP
run = True
while run:
    clock.tick(FPS)
    handle_sage_effect()
    mx, my = pygame.mouse.get_pos()
    md = pygame.mouse.get_pressed()[0]
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if fighter_1 and fighter_2 and current_state == STATE_FIGHT and not round_over:
                # Record premature game end
                add_to_history("Game closed", selected_fighters[0], selected_fighters[1], game_mode, True)
            save_settings(music_on, sound_on)
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU:
                if pvp_btn.collidepoint((mx, my)):
                    game_mode = "PVP"
                    current_state = STATE_SELECT
                    selection_stage = 0
                elif pve_btn.collidepoint((mx, my)):
                    game_mode = "PVE"
                    current_state = STATE_SELECT
                    selection_stage = 0
                elif music_btn.collidepoint((mx, my)):
                    music_on = not music_on
                    save_settings(music_on, sound_on)
                    if music_on:
                        mixer.music.play(-1, 0.0, 5000)
                    else:
                        mixer.music.stop()
                elif sound_btn.collidepoint((mx, my)):
                    sound_on = not sound_on
                    save_settings(music_on, sound_on)
                elif history_btn.collidepoint((mx, my)):
                    current_state = STATE_HISTORY
            elif current_state == STATE_SELECT:
                if back_btn.collidepoint((mx, my)):
                    current_state = STATE_MENU
                    selected_fighters = []
                    selection_stage = 0
                else:
                    for i, btn in enumerate(selection_buttons):
                        if btn.collidepoint((mx, my)):
                            char_name = list(CHARACTER_DATA.keys())[i]
                            selected_fighters.append(char_name)
                            if len(selected_fighters) == 2:
                                if game_mode == "PVE":
                                    fighter_1 = create_fighter(1, selected_fighters[0], 300, False)
                                    fighter_2 = create_fighter(2, selected_fighters[1], 600, True, is_ai=True)
                                else:
                                    fighter_1 = create_fighter(1, selected_fighters[0], 300, False)
                                    fighter_2 = create_fighter(2, selected_fighters[1], 600, True)
                                current_state = STATE_FIGHT
                                selection_stage = 0
                            else:
                                selection_stage = 1
            elif current_state == STATE_HISTORY:
                if back_btn.collidepoint((mx, my)):
                    current_state = STATE_MENU
            elif current_state == STATE_FIGHT and not round_over:
                if pause_btn and pause_btn.collidepoint((mx, my)):
                    game_paused = not game_paused
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and current_state == STATE_FIGHT and not round_over:
                game_paused = not game_paused
    if current_state == STATE_MENU:
        screen.fill(COLORS["PURPLE"])
        title = FONTS["count"].render("SUPER MASSIVE FIGHT GAME", True, COLORS["GOLD"])
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 10))
        controls_p1 = [
            "Player 1 Controls:",
            "A/D - Move Left/Right",
            "W - Jump",
            "S - Block",
            "R - Attack 1",
            "T - Attack 2",
            "Y - Special ability"
        ]
        for i, line in enumerate(controls_p1):
            draw_text(line, FONTS["small"], COLORS["GOLD"], 20, 200 + i * 25)
        controls_p2 = [
            "Player 2 Controls:",
            "Left/Right arrow keys - Move Left/Right",
            "Up arrow key - Jump",
            "Down arrow key - Block",
            "KP1 - Attack 1",
            "KP2 - Attack 2",
            "KP3 - Special ability"
        ]
        for i, line in enumerate(controls_p2):
            draw_text_right(line, FONTS["small"], COLORS["GOLD"], 200 + i * 25)
        pvp_btn = draw_button(
            "PVP", (SCREEN_WIDTH - 160) // 2, 250, 160, 60,
            FONTS["menu"], COLORS["GOLD"], COLORS["PURPLE"],
                   pygame.Rect((SCREEN_WIDTH - 160) // 2, 250, 160, 60).collidepoint((mx, my)) and md
        )
        pve_btn = draw_button(
            "PVE", (SCREEN_WIDTH - 160) // 2, 350, 160, 60,
            FONTS["menu"], COLORS["GOLD"], COLORS["PURPLE"],
                   pygame.Rect((SCREEN_WIDTH - 160) // 2, 350, 160, 60).collidepoint((mx, my)) and md
        )
        music_text = "Music: ON" if music_on else "Music: OFF"
        music_btn = draw_button(
            music_text, (SCREEN_WIDTH - 160) // 2, 450, 160, 40,
            FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
                        pygame.Rect((SCREEN_WIDTH - 160) // 2, 450, 160, 40).collidepoint((mx, my)) and md
        )
        sound_text = "Sound: ON" if sound_on else "Sound: OFF"
        sound_btn = draw_button(
            sound_text, (SCREEN_WIDTH - 160) // 2, 500, 160, 40,
            FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
                        pygame.Rect((SCREEN_WIDTH - 160) // 2, 500, 160, 40).collidepoint((mx, my)) and md
        )
        history_btn = draw_button(
            "Match History", (SCREEN_WIDTH - 200) // 2, 550, 200, 40,
            FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
                             pygame.Rect((SCREEN_WIDTH - 200) // 2, 550, 200, 40).collidepoint((mx, my)) and md
        )
    elif current_state == STATE_SELECT:
        screen.fill(COLORS["PURPLE"])
        if game_mode == "PVP":
            if selection_stage == 0:
                header_text = "PLAYER 1 - SELECT YOUR FIGHTER"
            else:
                header_text = "PLAYER 2 - SELECT YOUR FIGHTER"
        else:
            if selection_stage == 0:
                header_text = "SELECT YOUR FIGHTER"
            else:
                header_text = "SELECT OPPONENT"
        header = FONTS["menu"].render(header_text, True, COLORS["GOLD"])
        screen.blit(header, ((SCREEN_WIDTH - header.get_width()) // 2, 50))
        back_btn = draw_button(
            "BACK", 20, 20, 100, 40,
            FONTS["small"], COLORS["GOLD"], COLORS["PURPLE"],
            pygame.Rect(20, 20, 100, 40).collidepoint((mx, my)) and md
        )
        selection_buttons = []
        char_names = list(CHARACTER_DATA.keys())
        for i, char_name in enumerate(char_names):
            row = i // 2
            col = i % 2
            x = (SCREEN_WIDTH - 400) // 2 + col * 200
            y = 150 + row * 120
            btn = draw_button(
                char_name, x, y, 180, 80, FONTS["menu"],
                COLORS["GOLD"], COLORS["PURPLE"],
                pygame.Rect(x, y, 180, 80).collidepoint((mx, my)) and md
            )
            selection_buttons.append(btn)
            # Show description when hovering
            if btn.collidepoint((mx, my)):
                desc = CHARACTER_DESCRIPTIONS[char_name]
                desc_surf = FONTS["small"].render(desc, True, COLORS["PURPLE"])
                # Position description below the button
                desc_y = y + 90
                # Make sure description doesn't go off screen
                if desc_y + desc_surf.get_height() > SCREEN_HEIGHT - 50:
                    desc_y = y - 30  # Show above if near bottom
                # Draw semi-transparent background for readability
                desc_bg = pygame.Surface((desc_surf.get_width() + 10, desc_surf.get_height() + 5))
                desc_bg.set_alpha(200)
                desc_bg.fill(COLORS["YELLOW"])
                screen.blit(desc_bg, (x + (180 - desc_bg.get_width()) // 2, desc_y - 2))
                screen.blit(desc_surf, (x + (180 - desc_surf.get_width()) // 2, desc_y))
    elif current_state == STATE_HISTORY:
        back_btn = draw_history()
    elif current_state == STATE_FIGHT:
        draw_bg()
        # Player 1 stats (left-aligned)
        draw_health_value(fighter_1.health, 20, 20, True)
        draw_stamina_value(fighter_1, 20, 50, True)
        draw_cooldown_value(fighter_1, 20, 80, True)

        # Player 2 stats (right-aligned)
        draw_health_value(fighter_2.health, 0, 20, False)
        draw_stamina_value(fighter_2, 0, 50, False)
        draw_cooldown_value(fighter_2, 0, 80, False)

        if not round_over:
            pause_btn = draw_pause_button()
        if intro_count > 0:
            draw_text(str(intro_count), FONTS["count"], COLORS["RED"],
                      SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 3)
            if pygame.time.get_ticks() - last_count_update >= 1000 and not game_paused:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()
        else:
            if not game_paused:
                fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
                fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        for fighter in (fighter_1, fighter_2):
            fighter.update()
            fighter.draw(screen)
        if show_result:
            draw_result_text(result_text)
        if not round_over and not game_paused:
            if not fighter_1.alive:
                round_over = True
                round_over_time = pygame.time.get_ticks()
                if game_mode == "PVE":
                    result_text = "DEFEAT"
                    add_to_history("Player 2", selected_fighters[0], selected_fighters[1], game_mode)
                else:
                    result_text = "PLAYER 2 WINS"
                    add_to_history("Player 2", selected_fighters[0], selected_fighters[1], game_mode)
                show_result = True
            elif not fighter_2.alive:
                round_over = True
                round_over_time = pygame.time.get_ticks()
                if game_mode == "PVE":
                    result_text = "VICTORY"
                    add_to_history("Player 1", selected_fighters[0], selected_fighters[1], game_mode)
                else:
                    result_text = "PLAYER 1 WINS"
                    add_to_history("Player 1", selected_fighters[0], selected_fighters[1], game_mode)
                show_result = True
        else:
            if round_over and pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                show_result = False
                intro_count = 3
                selected_fighters = []
                current_state = STATE_SELECT
                selection_stage = 0
    pygame.display.update()
pygame.quit()