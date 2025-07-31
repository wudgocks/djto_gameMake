# enemy.py

import pyxel
import random
import math
# config.py 에 정의된 상수 사용을 위해 주석 처리 (main.py에 포함 시)
from config import * # bullet.py 에 정의된 클래스 사용을 위해 주석 처리 (main.py에 포함 시)

from bullet import *

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
            self.color = COLOR_RED
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