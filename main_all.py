# main.py (All-in-One, Debugged & Enhanced - Items, Power-ups, Ultimate - v9 Final - Difficulty Up)

import pyxel
import random
import math

# --- config.py 내용 시작 ---
# 게임 상수
WIDTH = 480
HEIGHT = 640
FPS = 60

# Pyxel 색상 팔레트 (RGB 대신 0-15 인덱스)
COLOR_BLACK = 0
COLOR_WHITE = 7
COLOR_RED = 8
COLOR_GREEN = 11 # HP UP 아이템 색상
COLOR_BLUE = 6
COLOR_YELLOW = 9 # OPTION 아이템 색상
COLOR_LIGHT_GREY = 13 # 적 총알 색상
COLOR_ORANGE = 10 # WING 아이템 색상
COLOR_PURPLE = 5
COLOR_CYAN = 12
COLOR_BOSS = 8
COLOR_ULTIMATE_GAUGE = 10 # 궁극기 게이지 색상 (주황색)
COLOR_BULLET_PLAYER_STRONG = 9 # 플레이어 총알 색상 (노란색)
COLOR_ITEM_OUTLINE = 7 # 아이템 외곽선 색상 (흰색)


# Player
PLAYER_SPEED = 3
PLAYER_BULLET_SPEED = 7
PLAYER_HP = 3 # 초기 플레이어 체력
PLAYER_MAX_HP = 5 # 최대 플레이어 체력 (아이템으로 증가 가능)

# Player Power-up
PLAYER_START_BULLET_W = 2
PLAYER_START_BULLET_H = 4
PLAYER_START_FIRE_RATE = 8 # 총알 발사 간격 (낮을수록 빠름)
PLAYER_MAX_POWER_LEVEL = 2 # 총알 강화 최대 레벨 (0:기본, 1:2줄, 2:3줄) - 최대 2번 업그레이드되도록 변경
PLAYER_OPTION_MAX = 2 # 옵션 최대 개수

# Enemy Bullet
ENEMY_BULLET_SPEED = 3
ENEMY_BULLET_WIDTH = 8  # 적 총알 너비
ENEMY_BULLET_HEIGHT = 8 # 적 총알 높이

# Enemy types
ENEMY_SIZE = 24 # 모든 적 기본 크기
ENEMY_TYPE_A_COLOR = COLOR_RED
ENEMY_TYPE_A_HP = 1
ENEMY_TYPE_A_SPEED = 1
ENEMY_TYPE_A_FIRE_RATE = 60 # A 타입 적 발사 간격 증가 (원래 90)
ENEMY_TYPE_A_WIDTH = ENEMY_SIZE
ENEMY_TYPE_A_HEIGHT = ENEMY_SIZE

ENEMY_TYPE_B_COLOR = COLOR_GREEN
ENEMY_TYPE_B_HP = 1
ENEMY_TYPE_B_SPEED = 0.8
ENEMY_TYPE_B_FIRE_RATE = 90 # B 타입 적 발사 간격 증가 (원래 120)
ENEMY_TYPE_B_WIDTH = ENEMY_SIZE
ENEMY_TYPE_B_HEIGHT = ENEMY_SIZE

ENEMY_TYPE_C_COLOR = COLOR_YELLOW # Zigzag enemy
ENEMY_TYPE_C_HP = 1
ENEMY_TYPE_C_SPEED = 1.5
ENEMY_TYPE_C_ZIGZAG_AMPLITUDE = 20
ENEMY_TYPE_C_ZIGZAG_FREQUENCY = 15
ENEMY_TYPE_C_FIRE_RATE = 60 # C 타입 적 발사 간격 증가 (원래 90)
ENEMY_TYPE_C_WIDTH = ENEMY_SIZE
ENEMY_TYPE_C_HEIGHT = ENEMY_SIZE

ENEMY_TYPE_D_COLOR = COLOR_PURPLE # Chasing enemy
ENEMY_TYPE_D_HP = 1
ENEMY_TYPE_D_SPEED = 0.5
ENEMY_TYPE_D_CHASE_THRESHOLD = 50
ENEMY_TYPE_D_WIDTH = ENEMY_SIZE
ENEMY_TYPE_D_HEIGHT = ENEMY_SIZE
ENEMY_TYPE_D_FIRE_RATE = 90 # D 타입 적 발사 간격 증가 (원래 120)

# Boss
BOSS_WIDTH = 120
BOSS_HEIGHT = 120
BOSS_HP = 300 # 보스 체력 유지
BOSS_COLOR = COLOR_BOSS

BOSS_PHASE1_HP_THRESHOLD = 200 # HP 역치 유지
BOSS_PHASE2_HP_THRESHOLD = 100 # HP 역치 유지

# Stages
STAGE1_ENEMY_COUNT = 10 # 적 개수 유지
STAGE1_BOSS_ACTIVE_TIME = 45 * FPS # 보스 등장 시간 증가 (원래 30 * FPS)
STAGE1_BACKGROUND_COLOR = COLOR_BLACK

STAGE2_ENEMY_COUNT = 15 # 적 개수 유지
STAGE2_BOSS_ACTIVE_TIME = 60 * FPS # 보스 등장 시간 증가 (원래 45 * FPS)
STAGE2_BACKGROUND_COLOR = COLOR_CYAN

ITEM_DROP_PROBABILITY = 0.5 # 일반 적 아이템 드랍 확률 유지
ITEM_BOSS_DROP_PROBABILITY = 1.0 # 보스 아이템 드랍 확률 유지
ITEM_SIZE = 24 # 아이템 크기 유지

# Ultimate
ULTIMATE_GAUGE_MAX = 100 # 궁극기 게이지 최대치 유지
ULTIMATE_GAUGE_PER_KILL = 10 # 적 한 마리당 얻는 게이지 유지
ULTIMATE_GAUGE_PER_BOSS_HIT = 3 # 보스에게 한 번 맞출 때 얻는 게이지 유지
ULTIMATE_EFFECT_DURATION = 15 # 궁극기 이펙트 지속 시간 유지
# --- config.py 내용 끝 ---


# --- bullet.py 내용 시작 ---
class PlayerBullet:
    def __init__(self, x, y, w, h, speedx=0, speedy=-10):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speedx = speedx
        self.speedy = speedy
        self.active = True

    def update(self):
        if not self.active: return
        self.x += self.speedx
        self.y += self.speedy
        if self.y + self.h < 0 or self.x < -self.w or self.x > WIDTH:
            self.active = False

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_BULLET_PLAYER_STRONG)


class EnemyBullet:
    def __init__(self, x, y, bullet_type="straight", target_x=None, target_y=None, speed=ENEMY_BULLET_SPEED):
        self.x = x
        self.y = y
        self.w = ENEMY_BULLET_WIDTH
        self.h = ENEMY_BULLET_HEIGHT
        self.speed = speed
        self.active = True
        self.bullet_type = bullet_type

        self.dx = 0
        self.dy = 0

        if bullet_type == "straight":
            self.dy = 1
        elif bullet_type == "aimed" and target_x is not None and target_y is not None:
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.dx = math.cos(angle)
            self.dy = math.sin(angle)

    def update(self):
        if not self.active: return

        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

        if self.y > HEIGHT or self.y + self.h < 0 or \
           self.x > WIDTH or self.x + self.w < 0:
            self.active = False

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_LIGHT_GREY)
# --- bullet.py 내용 끝 ---


# --- player.py 내용 시작 ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 16
        self.hp = PLAYER_HP
        self.is_alive = True
        self.flash_timer = 0
        self.fire_timer = 0
        self.fire_rate = PLAYER_START_FIRE_RATE # 초기 발사 속도

        self.bullet_w = PLAYER_START_BULLET_W
        self.bullet_h = PLAYER_START_BULLET_H

        self.options = [] # 옵션 리스트
        self.current_power_level = 0 # 총알 강화 레벨 (0: 기본, 1: 2줄, 2: 3줄)

    def update(self):
        if not self.is_alive:
            return

        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = max(self.x - PLAYER_SPEED, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = min(self.x + PLAYER_SPEED, WIDTH - self.w)
        if pyxel.btn(pyxel.KEY_UP):
            self.y = max(self.y - PLAYER_SPEED, 0)
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y = min(self.y + PLAYER_SPEED, HEIGHT - self.h)

        if self.flash_timer > 0:
            self.flash_timer -= 1

        self.fire_timer += 1

        # 옵션 위치 업데이트 (플레이어 따라다니게)
        if len(self.options) > 0:
            # 옵션 1 (왼쪽)
            self.options[0].x = self.x - self.options[0].w - 5
            self.options[0].y = self.y + self.h / 2 - self.options[0].h / 2
        if len(self.options) > 1:
            # 옵션 2 (오른쪽)
            self.options[1].x = self.x + self.w + 5
            self.options[1].y = self.y + self.h / 2 - self.options[1].h / 2


    def draw(self):
        if not self.is_alive:
            return

        if self.flash_timer > 0 and pyxel.frame_count % 4 < 2:
            return

        pyxel.rect(self.x, self.y, self.w, self.h, COLOR_BLUE)

        for opt in self.options:
            opt.draw()

    def shoot(self):
        bullets = []
        if self.is_alive and self.fire_timer >= self.fire_rate:
            self.fire_timer = 0
            # 플레이어 본체 총알
            bullets.append(PlayerBullet(self.x + self.w / 2 - self.bullet_w / 2, self.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))

            # 총알 강화 레벨에 따라 추가 총알 발사
            if self.current_power_level >= 1: # 2줄 이상
                bullets.append(PlayerBullet(self.x + self.w / 2 - self.bullet_w * 1.5 - 2, self.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))
                bullets.append(PlayerBullet(self.x + self.w / 2 + self.bullet_w * 0.5 + 2, self.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))
            if self.current_power_level >= 2: # 3줄 이상 (2줄 총알보다 더 바깥쪽으로)
                 bullets.append(PlayerBullet(self.x + self.w / 2 - self.bullet_w * 2.5 - 4, self.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))
                 bullets.append(PlayerBullet(self.x + self.w / 2 + self.bullet_w * 1.5 + 4, self.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))

            # 옵션 총알 발사
            for opt in self.options:
                bullets.append(PlayerBullet(opt.x + opt.w / 2 - self.bullet_w / 2, opt.y, self.bullet_w, self.bullet_h, speedy=-PLAYER_BULLET_SPEED))
        return bullets


    def take_damage(self, amount):
        if self.flash_timer > 0:
            return

        self.hp -= amount
        self.flash_timer = 30 # 0.5초 무적
        
        # 피격 시 강화 효과 감소 (총알 약화 및 옵션 제거)
        if self.current_power_level > 0:
            self.current_power_level -= 1
            self._update_bullet_power() # 총알 파워 레벨에 따른 스펙 업데이트
        
        # 옵션이 하나라도 있으면 하나 제거
        if len(self.options) > 0:
            self.options.pop() # 가장 마지막에 추가된 옵션 제거

        if self.hp <= 0:
            self.is_alive = False

    def gain_hp(self, amount):
        self.hp = min(self.hp + amount, PLAYER_MAX_HP)

    def power_up(self, item_type):
        if item_type == 'wing':
            if self.current_power_level < PLAYER_MAX_POWER_LEVEL: # 최대 레벨 제한 적용
                self.current_power_level += 1
                self._update_bullet_power() # 총알 파워 레벨에 따른 스펙 업데이트
        elif item_type == 'option':
            if len(self.options) < PLAYER_OPTION_MAX:
                self.options.append(Option(self.x, self.y, self)) # 플레이어 참조 전달
    
    def _update_bullet_power(self):
        # 파워 레벨에 따라 총알 크기 및 발사 속도 조정
        if self.current_power_level == 0: # 기본 (1줄)
            self.bullet_w = PLAYER_START_BULLET_W
            self.bullet_h = PLAYER_START_BULLET_H
            self.fire_rate = PLAYER_START_FIRE_RATE
        elif self.current_power_level == 1: # 2줄
            self.bullet_w = PLAYER_START_BULLET_W * 2
            self.bullet_h = PLAYER_START_BULLET_H * 2
            self.fire_rate = max(1, PLAYER_START_FIRE_RATE - 2)
        elif self.current_power_level == 2: # 3줄 (최대 레벨)
            self.bullet_w = PLAYER_START_BULLET_W * 3
            self.bullet_h = PLAYER_START_BULLET_H * 3
            self.fire_rate = max(1, PLAYER_START_FIRE_RATE - 4)


class Option:
    def __init__(self, x, y, player_ref):
        self.x = x
        self.y = y
        self.w = 12
        self.h = 12
        self.color = COLOR_YELLOW # 옵션 색상 (아이템 색상과 통일)
        self.player_ref = player_ref # 플레이어 객체 참조 (위치 추적용)
        self.is_alive = True

    def update(self):
        # 플레이어 update에서 직접 위치를 지정해주므로 여기서는 특별히 할 일 없음
        pass

    def draw(self):
        if self.is_alive:
            pyxel.rect(self.x, self.y, self.w, self.h, self.color)
# --- player.py 내용 끝 ---


# --- enemy.py 내용 시작 ---
class Enemy:
    def __init__(self, x, y, type_id, player_ref):
        self.x = x
        self.y = y
        self.type_id = type_id
        self.player_ref = player_ref
        self.fire_timer = 0
        self.is_alive = True

        if type_id == "A":
            self.hp = ENEMY_TYPE_A_HP
            self.color = ENEMY_TYPE_A_COLOR
            self.speed = ENEMY_TYPE_A_SPEED
            self.fire_rate = ENEMY_TYPE_A_FIRE_RATE
            self.w = ENEMY_TYPE_A_WIDTH
            self.h = ENEMY_TYPE_A_HEIGHT
            self.move_pattern = self._move_straight
            self.attack_pattern = self._attack_simple
        elif type_id == "B":
            self.hp = ENEMY_TYPE_B_HP
            self.color = ENEMY_TYPE_B_COLOR
            self.speed = ENEMY_TYPE_B_SPEED
            self.fire_rate = ENEMY_TYPE_B_FIRE_RATE
            self.w = ENEMY_TYPE_B_WIDTH
            self.h = ENEMY_TYPE_B_HEIGHT
            self.move_pattern = self._move_straight
            self.attack_pattern = self._attack_spread_aimed_wider # 새로운 패턴 유지
        elif type_id == "C":
            self.hp = ENEMY_TYPE_C_HP
            self.color = ENEMY_TYPE_C_COLOR
            self.speed = ENEMY_TYPE_C_SPEED
            self.fire_rate = ENEMY_TYPE_C_FIRE_RATE
            self.w = ENEMY_TYPE_C_WIDTH
            self.h = ENEMY_TYPE_C_HEIGHT
            self.initial_x = x
            self.move_pattern = self._move_zigzag
            self.attack_pattern = self._attack_none
        elif type_id == "D":
            self.hp = ENEMY_TYPE_D_HP
            self.color = COLOR_PURPLE
            self.speed = 0.5
            self.fire_rate = ENEMY_TYPE_D_FIRE_RATE
            self.w = ENEMY_TYPE_D_WIDTH
            self.h = ENEMY_TYPE_D_HEIGHT
            self.move_pattern = self._move_chase
            self.attack_pattern = self._attack_spread_aimed_sparser # 새로운 패턴 유지
        else:
            self.hp = 1
            self.color = COLOR_RED
            self.speed = 1
            self.fire_rate = 60
            self.w = ENEMY_SIZE
            self.h = ENEMY_SIZE
            self.move_pattern = self._move_straight
            self.attack_pattern = self._attack_simple

    def update(self, player_x, player_y):
        if not self.is_alive:
            return []

        self.move_pattern(player_x, player_y)
        self.fire_timer += 1
        bullets = []
        if self.fire_timer >= self.fire_rate:
            bullets = self.attack_pattern(player_x, player_y)
            if not isinstance(bullets, list):
                bullets = []
            bullets = [b for b in bullets if b.active]
            self.fire_timer = 0 # 총알 발사 후 타이머 리셋
        return bullets

    def draw(self):
        if not self.is_alive:
            return

        pyxel.rect(self.x, self.y, self.w, self.h, self.color)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False

    # --- Movement Patterns ---
    def _move_straight(self, player_x, player_y):
        self.y += self.speed
        if self.y > HEIGHT:
            self.is_alive = False

    def _move_zigzag(self, player_x, player_y):
        self.y += self.speed
        self.x = self.initial_x + ENEMY_TYPE_C_ZIGZAG_AMPLITUDE * math.sin(pyxel.frame_count / ENEMY_TYPE_C_ZIGZAG_FREQUENCY)
        if self.y > HEIGHT:
            self.is_alive = False

    def _move_chase(self, player_x, player_y):
        if self.y < HEIGHT / 3:
            self.y += self.speed
        else:
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

        if self.y > HEIGHT + self.h:
            self.is_alive = False

    # --- Attack Patterns ---
    def _attack_simple(self, player_x, player_y):
        return [EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, bullet_type="straight", speed=ENEMY_BULLET_SPEED)]

    def _attack_aimed(self, player_x, player_y):
        target_x = player_x + self.player_ref.w / 2
        target_y = player_y + self.player_ref.h / 2
        return [EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, bullet_type="aimed", target_x=target_x, target_y=target_y, speed=ENEMY_BULLET_SPEED)]

    def _attack_none(self, player_x, player_y):
        return []

    # 새로운 넓은 간격의 조준 스프레드 공격 패턴 (B 타입용, 확산 각도 유지)
    def _attack_spread_aimed_wider(self, player_x, player_y):
        bullets = []
        num_bullets = 3 # 쏠 총알 개수 유지
        spread_angle = math.pi / 3 # 전체 확산 각도 유지 (60도)
        
        # 플레이어를 향하는 기본 각도 계산
        base_angle = math.atan2(player_y - (self.y + self.h), player_x - (self.x + self.w / 2))

        for i in range(num_bullets):
            # 총알 간 간격을 균등하게 배분
            angle_offset = -spread_angle / 2 + (i / (num_bullets - 1)) * spread_angle if num_bullets > 1 else 0
            
            current_angle = base_angle + angle_offset
            
            # 총알이 목표 지점까지 정확히 조준되도록 임의의 먼 거리 (1000) 설정
            dx = math.cos(current_angle)
            dy = math.sin(current_angle)
            
            bullets.append(EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, 
                                       bullet_type="aimed", 
                                       target_x=self.x + dx * 1000, 
                                       target_y=self.y + dy * 1000, 
                                       speed=ENEMY_BULLET_SPEED))
        return bullets

    # 더 적은 총알로 더 듬성듬성한 조준 스프레드 공격 패턴 (D 타입용, 확산 각도 유지)
    def _attack_spread_aimed_sparser(self, player_x, player_y):
        bullets = []
        num_bullets = 2 # 쏠 총알 개수 유지
        spread_angle = math.pi / 2 # 전체 확산 각도 유지 (90도)
        
        base_angle = math.atan2(player_y - (self.y + self.h), player_x - (self.x + self.w / 2))

        for i in range(num_bullets):
            angle_offset = -spread_angle / 2 + (i / (num_bullets - 1)) * spread_angle if num_bullets > 1 else 0
            
            current_angle = base_angle + angle_offset
            
            dx = math.cos(current_angle)
            dy = math.sin(current_angle)
            
            bullets.append(EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, 
                                       bullet_type="aimed", 
                                       target_x=self.x + dx * 1000, 
                                       target_y=self.y + dy * 1000, 
                                       speed=ENEMY_BULLET_SPEED))
        return bullets


class Boss:
    def __init__(self, x, y, player_ref):
        self.x = x
        self.y = y
        self.w = BOSS_WIDTH
        self.h = BOSS_HEIGHT
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.color = BOSS_COLOR
        self.is_alive = True
        self.player_ref = player_ref

        self.phase = 1
        self.fire_timer = 0
        self.fire_rate = 60
        self.minion_spawn_timer = 0
        self.minion_spawn_rate = 180

        self.weak_point_w = self.w / 4
        self.weak_point_h = self.h / 4
        self.weak_point_x = self.x + self.w / 2 - self.weak_point_w / 2
        self.weak_point_y = self.y + self.h - self.weak_point_h - 5
        self.weak_point_color = COLOR_WHITE

        self.initial_y = y

    def update(self):
        if not self.is_alive:
            return [], []

        self.weak_point_x = self.x + self.w / 2 - self.weak_point_w / 2
        self.weak_point_y = self.y + self.h - self.weak_point_h - 5

        self._update_phase()
        self._move_pattern()

        self.fire_timer += 1
        new_bullets = []
        if self.fire_timer >= self.fire_rate:
            bullets = self._attack_pattern()
            if not isinstance(bullets, list):
                bullets = []
            new_bullets.extend(bullets)
            self.fire_timer = 0

        self.minion_spawn_timer += 1
        new_enemies = []
        if self.minion_spawn_timer >= self.minion_spawn_rate:
            enemies = self._spawn_minions()
            if not isinstance(enemies, list):
                enemies = []
            new_enemies.extend(enemies)
            self.minion_spawn_timer = 0

        return new_bullets, new_enemies

    def draw(self):
        if not self.is_alive:
            return

        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rect(self.weak_point_x, self.weak_point_y, self.weak_point_w, self.weak_point_h, self.weak_point_color)

        hp_bar_width = (self.hp / self.max_hp) * self.w
        pyxel.rect(self.x, self.y - 5, hp_bar_width, 3, COLOR_GREEN)

    def take_damage(self, amount, is_weak_point_hit=False):
        if is_weak_point_hit:
            self.hp -= amount * 2
            pyxel.text(self.x + self.w/2 - len("CRIT!")*2, self.y + self.h/2, "CRIT!", COLOR_YELLOW)
        else:
            self.hp -= amount

        if self.hp <= 0:
            self.is_alive = False

    # --- Phase System ---
    def _update_phase(self):
        if self.hp <= BOSS_PHASE2_HP_THRESHOLD and self.phase < 3:
            self.phase = 3
            self.fire_rate = 30
            self.minion_spawn_rate = 90
            self.color = COLOR_RED
        elif self.hp <= BOSS_PHASE1_HP_THRESHOLD and self.phase < 2:
            self.phase = 2
            self.fire_rate = 45
            self.color = COLOR_ORANGE

    # --- Boss Movement Patterns ---
    def _move_pattern(self):
        if self.phase == 1:
            self.x = (WIDTH / 2) + 60 * math.sin(pyxel.frame_count * 0.02) - self.w / 2
        elif self.phase >= 2:
            self.x = (WIDTH / 2) + 80 * math.sin(pyxel.frame_count * 0.04) - self.w / 2
            self.y = self.initial_y + 10 * math.sin(pyxel.frame_count * 0.03)

    # --- Boss Attack Patterns ---
    def _attack_pattern(self):
        bullets = []
        # 페이즈 1: 단일 조준 총알 (유지)
        if self.phase == 1:
            target_x = self.player_ref.x + self.player_ref.w / 2
            target_y = self.player_ref.y + self.player_ref.h / 2
            bullets.append(EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, bullet_type="aimed", target_x=target_x, target_y=target_y, speed=ENEMY_BULLET_SPEED * 1.5))
        
        # 페이즈 2: 부채꼴 총알 발사 수 증가 및 각도 간격 조정
        elif self.phase == 2:
            for i in range(-3, 4): # 총 7발 (원래 5발)
                angle_offset = i * math.pi / 12 # 각도 간격 약간 감소 (원래 pi/10 -> pi/5에서 pi/12로 변경)
                
                target_x = self.player_ref.x + self.player_ref.w / 2
                target_y = self.player_ref.y + self.player_ref.h / 2
                angle = math.atan2(target_y - (self.y + self.h), target_x - (self.x + self.w / 2)) + angle_offset
                dx = math.cos(angle)
                dy = math.sin(angle)
                bullets.append(EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, bullet_type="aimed", target_x=self.x + dx * 100, target_y=self.y + dy * 100, speed=ENEMY_BULLET_SPEED * 1.5))
        
        # 페이즈 3: 원형 총알 발사 수 증가
        elif self.phase == 3:
            for i in range(8): # 총 8발 (원래 4발 -> 다시 8발)
                angle = pyxel.frame_count * 0.1 + i * (math.pi * 2 / 8) # 8 유지 (더 촘촘하게)
                dx = math.cos(angle)
                dy = math.sin(angle)
                bullets.append(EnemyBullet(self.x + self.w / 2 - ENEMY_BULLET_WIDTH/2, self.y + self.h, bullet_type="aimed", target_x=self.x + dx * 100, target_y=self.y + dy * 100, speed=ENEMY_BULLET_SPEED * 2))

        return bullets

    # --- Minion Spawning (유지) ---
    def _spawn_minions(self):
        enemies = []
        if self.phase >= 2:
            enemies.append(Enemy(self.x + self.w/4, self.y + self.h, "A", self.player_ref))
            enemies.append(Enemy(self.x + self.w*3/4, self.y + self.h, "B", self.player_ref))
        return enemies
# --- enemy.py 내용 끝 ---


# --- item.py 내용 시작 ---
class Item:
    def __init__(self, x, y, item_type):
        self.x = x - ITEM_SIZE / 2
        self.y = y - ITEM_SIZE / 2
        self.w = ITEM_SIZE
        self.h = ITEM_SIZE
        self.type = item_type
        self.speedy = 3
        self.active = True

    def update(self):
        if not self.active: return
        self.y += self.speedy
        if self.y > HEIGHT:
            self.active = False

    def draw(self):
        if self.active:
            color = COLOR_ORANGE # 기본 (wing)
            if self.type == 'hp_up':
                color = COLOR_GREEN # 초록색
            elif self.type == 'option':
                color = COLOR_YELLOW # 노란색
            # 'wing' 아이템은 기본값인 COLOR_ORANGE (주황색) 유지

            # 아이템 외곽선 (깜빡이는 효과)
            if pyxel.frame_count % 10 < 5: # 10프레임 주기로 깜빡임
                pyxel.rectb(self.x - 2, self.y - 2, self.w + 4, self.h + 4, COLOR_ITEM_OUTLINE) # 외곽선 그리기
            
            pyxel.rect(self.x, self.y, self.w, self.h, color)
# --- item.py 내용 끝 ---


# --- main.py 본문 내용 시작 ---
class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="1945 Shooter Enhanced", fps=FPS)

        self.player = Player(WIDTH / 2, HEIGHT - 30)
        self.player_bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.items = []

        self.boss = None
        self.current_stage = 1
        self.stage_timer = 0
        self.enemies_spawned_this_stage = 0
        self.stage_completed = False

        self.ultimate_gauge = 0 # 궁극기 게이지 추가
        self.ultimate_effect_timer = 0 # 궁극기 이펙트 타이머

        self.game_state = "TITLE"

        pyxel.run(self.update, self.draw)

    def _start_game(self):
        self.game_state = "PLAYING"
        self.player = Player(WIDTH / 2, HEIGHT - 30)
        self.player_bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.items = []
        self.boss = None
        self.current_stage = 1
        self.stage_timer = 0
        self.enemies_spawned_this_stage = 0
        self.stage_completed = False
        self.ultimate_gauge = 0 # 게임 시작 시 게이지 초기화
        self.ultimate_effect_timer = 0 # 이펙트 타이머 초기화

    def update(self):
        if self.game_state == "TITLE":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self._start_game()
        elif self.game_state == "PLAYING":
            self._update_playing()
        elif self.game_state == "GAME_OVER" or self.game_state == "STAGE_CLEAR":
            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.game_state == "STAGE_CLEAR":
                    if self.current_stage < 2:
                        self.current_stage += 1
                        self.enemies_spawned_this_stage = 0
                        self.stage_timer = 0
                        self.enemies = []
                        self.enemy_bullets = []
                        self.items = []
                        self.boss = None
                        self.stage_completed = False
                        self.game_state = "PLAYING"
                    else:
                        self._start_game()
                else:
                    self._start_game()

    def _update_playing(self):
        self.stage_timer += 1

        self.player.update()
        if pyxel.btn(pyxel.KEY_SPACE):
            new_bullets = self.player.shoot()
            if new_bullets:
                self.player_bullets.extend(new_bullets)

        # 궁극기 사용 (F 키)
        if pyxel.btnp(pyxel.KEY_F) and self.ultimate_gauge >= ULTIMATE_GAUGE_MAX:
            self._activate_ultimate()

        # 궁극기 이펙트 타이머 감소
        if self.ultimate_effect_timer > 0:
            self.ultimate_effect_timer -= 1
            if self.ultimate_effect_timer == 0:
                pyxel.pal() # 팔레트 리셋


        for bullet in self.player_bullets:
            bullet.update()
        self.player_bullets = [b for b in self.player_bullets if b.active]

        current_stage_enemies_limit = 0
        if self.current_stage == 1:
            current_stage_enemies_limit = STAGE1_ENEMY_COUNT
        elif self.current_stage == 2:
            current_stage_enemies_limit = STAGE2_ENEMY_COUNT

        # 보스가 없으면 일반 적 스폰 (보스 등장 후에는 일반 적 스폰 중단)
        if self.boss is None and self.enemies_spawned_this_stage < current_stage_enemies_limit:
            # 보스 등장 시간을 고려하여 적 스폰을 멈추고 보스를 생성
            if self.current_stage == 1 and self.stage_timer >= STAGE1_BOSS_ACTIVE_TIME:
                self.enemies_spawned_this_stage = current_stage_enemies_limit # 더 이상 일반 적 스폰 안함
            elif self.current_stage == 2 and self.stage_timer >= STAGE2_BOSS_ACTIVE_TIME:
                 self.enemies_spawned_this_stage = current_stage_enemies_limit # 더 이상 일반 적 스폰 안함
            else: # 보스 등장 시간 전에는 계속 스폰
                if pyxel.frame_count % 60 == 0:
                    enemy_x = random.randint(0, WIDTH - ENEMY_SIZE)
                    enemy_y = -ENEMY_SIZE
                    enemy_types = ["A", "B", "C", "D"]
                    selected_type = random.choice(enemy_types)

                    self.enemies.append(Enemy(enemy_x, enemy_y, selected_type, self.player))
                    self.enemies_spawned_this_stage += 1


        new_enemy_bullets = []
        
        active_enemies = []
        for enemy in self.enemies:
            enemy_bullets_from_enemy = enemy.update(self.player.x, self.player.y)
            new_enemy_bullets.extend(enemy_bullets_from_enemy)

            if enemy.is_alive:
                active_enemies.append(enemy)
        self.enemies = active_enemies # 죽은 적 제거는 _handle_collisions에서 최종적으로 처리

        # 보스 등장 조건 및 보스 생성
        # 모든 일반 적이 스폰되었고, 보스가 아직 없으면 보스 생성
        if self.boss is None and self.enemies_spawned_this_stage >= current_stage_enemies_limit:
            if self.current_stage == 1:
                self.boss = Boss(WIDTH / 2 - BOSS_WIDTH / 2, 20, self.player)
            elif self.current_stage == 2:
                self.boss = Boss(WIDTH / 2 - BOSS_WIDTH / 2, 20, self.player)


        if self.boss:
            boss_bullets, boss_minions = self.boss.update()
            self.enemy_bullets.extend(boss_bullets)
            self.enemies.extend(boss_minions)
            # 보스가 죽으면 스테이지 완료 처리 및 아이템 드랍
            if not self.boss.is_alive:
                self.boss = None
                self.stage_completed = True
                if random.random() < ITEM_BOSS_DROP_PROBABILITY: # 보스는 항상 드랍
                    self.items.append(Item(WIDTH / 2, HEIGHT / 2, random.choice(['hp_up', 'wing', 'option']))) # 보스 드랍 아이템


        self.enemy_bullets.extend(new_enemy_bullets)

        for bullet in self.enemy_bullets:
            bullet.update()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

        for item in self.items:
            item.update()
        self.items = [i for i in self.items if i.active]


        self._handle_collisions()

        if self.player.hp <= 0:
            self.game_state = "GAME_OVER"

        self._check_stage_completion()

    def _handle_collisions(self):
        # 플레이어 총알과 적 충돌
        new_player_bullets = []
        for bullet in self.player_bullets:
            hit_enemy = False
            for enemy in self.enemies:
                if bullet.active and enemy.is_alive and self._is_colliding(bullet, enemy):
                    enemy.take_damage(1)
                    bullet.active = False
                    hit_enemy = True
                    break
            if not hit_enemy:
                new_player_bullets.append(bullet)
        self.player_bullets = new_player_bullets

        # 죽은 적 처리 및 아이템 드랍/게이지 충전
        active_enemies_after_damage = []
        for enemy in self.enemies:
            if enemy.is_alive:
                active_enemies_after_damage.append(enemy)
            else:
                # 적 사망 시 아이템 드랍
                if random.random() < ITEM_DROP_PROBABILITY:
                    self.items.append(Item(enemy.x + enemy.w / 2, enemy.y + enemy.h / 2, random.choice(['hp_up', 'wing', 'option'])))
                self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_KILL) # 궁극기 게이지 충전
        self.enemies = active_enemies_after_damage


        # 플레이어 총알과 보스 충돌
        if self.boss and self.boss.is_alive:
            new_player_bullets_for_boss = []
            for bullet in self.player_bullets:
                if bullet.active and self._is_colliding(bullet, self.boss):
                    if self._is_colliding(bullet, self.boss, is_weak_point=True):
                        self.boss.take_damage(1, is_weak_point_hit=True)
                    else:
                        self.boss.take_damage(1)
                    bullet.active = False
                    self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_BOSS_HIT) # 보스 타격 시 게이지 충전
                if bullet.active:
                    new_player_bullets_for_boss.append(bullet)
            self.player_bullets = new_player_bullets_for_boss

        # 적 총알과 플레이어 충돌
        if self.player.is_alive:
            new_enemy_bullets_after_player_hit = []
            for e_bullet in self.enemy_bullets:
                if e_bullet.active and self._is_colliding(e_bullet, self.player):
                    self.player.take_damage(1)
                    e_bullet.active = False
                if e_bullet.active:
                    new_enemy_bullets_after_player_hit.append(e_bullet)
            self.enemy_bullets = new_enemy_bullets_after_player_hit

        # 적과 플레이어 충돌 (적이 플레이어에게 직접 박는 경우)
        if self.player.is_alive:
            active_enemies_after_player_collision = []
            for enemy in self.enemies:
                if enemy.is_alive and self._is_colliding(enemy, self.player):
                    self.player.take_damage(999) # 즉사
                    enemy.is_alive = False
                    self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_KILL) # 궁극기 게이지 충전
                if enemy.is_alive:
                    active_enemies_after_player_collision.append(enemy)
            self.enemies = active_enemies_after_player_collision


        # 아이템과 플레이어 충돌
        if self.player.is_alive:
            new_items_after_pickup = []
            for item in self.items:
                if item.active and self._is_colliding(item, self.player):
                    if item.type == 'hp_up':
                        self.player.gain_hp(1)
                    elif item.type == 'wing':
                        self.player.power_up('wing')
                    elif item.type == 'option':
                        self.player.power_up('option')
                    item.active = False
                if item.active:
                    new_items_after_pickup.append(item)
            self.items = new_items_after_pickup


    def _is_colliding(self, obj1, obj2, is_weak_point=False):
        if is_weak_point and hasattr(obj2, 'weak_point_x'):
            return (obj1.x < obj2.weak_point_x + obj2.weak_point_w and
                    obj1.x + obj1.w > obj2.weak_point_x and
                    obj1.y < obj2.weak_point_y + obj2.weak_point_h and
                    obj1.y + obj1.h > obj2.weak_point_y)
        else:
            return (obj1.x < obj2.x + obj2.w and
                    obj1.x + obj1.w > obj2.x and
                    obj1.y < obj2.y + obj2.h and
                    obj1.y + obj1.h > obj2.y)

    def _activate_ultimate(self):
        # 궁극기 발동 시 게이지 소모 및 모든 적/적 총알 제거
        self.ultimate_gauge = 0
        self.enemies = []
        self.enemy_bullets = []
        
        # 궁극기 이펙트: 화면 색상 반전 (temporarily)
        # 0번 색 (검정)을 7번 색 (흰색)으로, 7번 색을 0번 색으로 바꿈
        pyxel.pal(0, 7)
        pyxel.pal(7, 0)
        # 다른 색상들도 궁극기 테마에 맞게 변경할 수 있음
        pyxel.pal(COLOR_BLUE, COLOR_RED) # 플레이어를 파란색에서 빨간색으로
        pyxel.pal(COLOR_RED, COLOR_BLUE) # 적을 빨간색에서 파란색으로
        self.ultimate_effect_timer = ULTIMATE_EFFECT_DURATION # 이펙트 지속 시간 설정

    def _check_stage_completion(self):
        if self.boss is None and self.stage_completed:
            if self.current_stage < 2:
                self.game_state = "STAGE_CLEAR"
            else:
                self.game_state = "GAME_OVER"

    def draw(self):
        # 궁극기 이펙트가 활성화된 동안 배경 색상 변경
        if self.ultimate_effect_timer > 0:
            pyxel.cls(COLOR_WHITE if pyxel.frame_count % 4 < 2 else COLOR_BLACK) # 화면 깜빡임 효과
        elif self.current_stage == 1:
            pyxel.cls(STAGE1_BACKGROUND_COLOR)
        elif self.current_stage == 2:
            pyxel.cls(STAGE2_BACKGROUND_COLOR)


        if self.game_state == "TITLE":
            title_text = "1945 Shooter"
            start_text = "PRESS RETURN TO START"
            pyxel.text(WIDTH / 2 - len(title_text) * 4 / 2, HEIGHT / 2 - 10, title_text, COLOR_WHITE)
            pyxel.text(WIDTH / 2 - len(start_text) * 4 / 2, HEIGHT / 2 + 10, start_text, COLOR_YELLOW)
        elif self.game_state == "PLAYING":
            self.player.draw()
            for bullet in self.player_bullets:
                bullet.draw()
            for enemy in self.enemies:
                enemy.draw()
            for e_bullet in self.enemy_bullets:
                e_bullet.draw()
            for item in self.items:
                item.draw()
            if self.boss:
                self.boss.draw()

            # HUD (Head-Up Display)
            pyxel.text(5, 5, f"HP: {self.player.hp}", COLOR_GREEN)
            pyxel.text(5, 15, f"STAGE: {self.current_stage}", COLOR_WHITE)

            # 궁극기 게이지 표시
            ultimate_gauge_text = "ULTIMATE (F)"
            pyxel.text(5, HEIGHT - 20, ultimate_gauge_text, COLOR_WHITE)
            pyxel.rect(5, HEIGHT - 10, ULTIMATE_GAUGE_MAX, 5, COLOR_BLACK) # 게이지 바 배경
            
            # 궁극기 게이지 가득 차면 깜빡임 효과
            if self.ultimate_gauge >= ULTIMATE_GAUGE_MAX and pyxel.frame_count % 10 < 5:
                pyxel.rect(5, HEIGHT - 10, self.ultimate_gauge, 5, COLOR_WHITE) # 흰색으로 깜빡
            else:
                pyxel.rect(5, HEIGHT - 10, self.ultimate_gauge, 5, COLOR_ULTIMATE_GAUGE) # 원래 색상

            # 궁극기 발동 시 메시지 표시
            if self.ultimate_effect_timer > 0:
                ultimate_message = "ULTIMATE!"
                pyxel.text(WIDTH / 2 - len(ultimate_message) * 4 / 2, HEIGHT / 2 - 20, ultimate_message, COLOR_YELLOW)


            current_stage_enemies_limit = 0
            if self.current_stage == 1:
                current_stage_enemies_limit = STAGE1_ENEMY_COUNT
            elif self.current_stage == 2:
                current_stage_enemies_limit = STAGE2_ENEMY_COUNT

            if self.boss is None and self.enemies_spawned_this_stage < current_stage_enemies_limit:
                 enemies_remaining_text = f"ENEMIES REMAINING: {current_stage_enemies_limit - self.enemies_spawned_this_stage}"
                 pyxel.text(WIDTH - len(enemies_remaining_text) * 4 - 5, 5, enemies_remaining_text, COLOR_WHITE)
            elif self.boss and self.boss.is_alive:
                 boss_active_text = "BOSS ACTIVE"
                 pyxel.text(WIDTH - len(boss_active_text) * 4 - 5, 15, boss_active_text, COLOR_RED)

        elif self.game_state == "GAME_OVER":
            game_over_text = "GAME OVER"
            restart_text = "PRESS RETURN TO RESTART"
            pyxel.text(WIDTH / 2 - len(game_over_text) * 4 / 2, HEIGHT / 2 - 10, game_over_text, COLOR_RED)
            pyxel.text(WIDTH / 2 - len(restart_text) * 4 / 2, HEIGHT / 2 + 10, restart_text, COLOR_YELLOW)
        elif self.game_state == "STAGE_CLEAR":
            stage_clear_text = f"STAGE {self.current_stage-1} CLEAR!"
            next_stage_text = "PRESS RETURN FOR NEXT STAGE"
            pyxel.text(WIDTH / 2 - len(stage_clear_text) * 4 / 2, HEIGHT / 2 - 10, stage_clear_text, COLOR_GREEN)
            pyxel.text(WIDTH / 2 - len(next_stage_text) * 4 / 2, HEIGHT / 2 + 10, next_stage_text, COLOR_YELLOW)

Game()