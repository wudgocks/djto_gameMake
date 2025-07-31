# player.py

import pyxel
from config import *
from bullet import *

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