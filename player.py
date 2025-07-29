# Player 및 SideWing 클래스

# player.py
import pyxel
import math
from config import WIDTH, HEIGHT, FPS, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW, COLOR_ULTIMATE
from bullet import PlayerBullet # PlayerBullet 클래스 임포트

class Player:
    def __init__(self, game_ref): 
        self.game = game_ref 
        self.w = 50
        self.h = 40
        self.x = (WIDTH - self.w) // 2
        self.y = HEIGHT - 20 - self.h
        self.speedx = 0
        self.speedy = 0
        self.player_speed = 5
        
        self.shoot_delay = 250
        self.last_shot = pyxel.frame_count * (1000 / FPS) 
        
        self.power = 1 
        self.lives = 3
        self.hidden = False
        self.hide_timer = pyxel.frame_count * (1000 / FPS)
        self.invincible = False
        self.invincible_timer = pyxel.frame_count * (1000 / FPS)
        self.invincible_duration = 2000 
        self.hide_duration = 500 

        self.wing_count = 0
        self.visible = True

        # 궁극기 관련 변수 추가
        self.ultimate_gauge = 0
        self.ultimate_max_gauge = 5000 # 궁극기 게이지 최대치
        self.ultimate_active = False # 궁극기 발동 여부
        self.ultimate_active_timer = 0
        self.ultimate_active_duration = 300 # 궁극기 발동 지속 시간 (ms)
        self.ultimate_shoot_interval = 50 # 궁극기 총알 발사 간격 (ms)
        self.last_ultimate_shot = pyxel.frame_count * (1000 / FPS)

    def update(self):
        current_time_ms = pyxel.frame_count * (1000 / FPS)

        if self.invincible and current_time_ms - self.invincible_timer > self.invincible_duration:
            self.invincible = False
            self.visible = True 
        elif self.invincible:
            if int(current_time_ms / 50) % 2 == 0:
                self.visible = True
            else:
                self.visible = False
        else:
            self.visible = True 

        self.speedx = 0
        self.speedy = 0

        if not self.hidden:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.speedx = -self.player_speed
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.speedx = self.player_speed
            if pyxel.btn(pyxel.KEY_UP):
                self.speedy = -self.player_speed
            if pyxel.btn(pyxel.KEY_DOWN):
                self.speedy = self.player_speed
            
            if pyxel.btn(pyxel.KEY_SPACE):
                self.shoot()

            # F 키로 궁극기 발동
            if pyxel.btnp(pyxel.KEY_F) and self.ultimate_gauge >= self.ultimate_max_gauge:
                self.activate_ultimate()

            self.x += self.speedx
            self.y += self.speedy

            self.x = max(0, min(self.x, WIDTH - self.w))
            self.y = max(0, min(self.y, HEIGHT - self.h))

        # 궁극기 발동 중 처리
        if self.ultimate_active:
            if current_time_ms - self.ultimate_active_timer > self.ultimate_active_duration:
                self.ultimate_active = False
            elif current_time_ms - self.last_ultimate_shot > self.ultimate_shoot_interval:
                self.last_ultimate_shot = current_time_ms
                self.game.spawn_ultimate_bullets() # Game 클래스의 메서드 호출

        if self.hidden and current_time_ms - self.hide_timer > self.hide_duration: 
            self.hidden = False
            self.invincible = True 
            self.invincible_timer = current_time_ms
            self.x = (WIDTH - self.w) // 2 
            self.y = HEIGHT - 20 - self.h
            self.visible = True 


    def shoot(self):
        now = pyxel.frame_count * (1000 / FPS)
        current_shoot_delay = self.shoot_delay / (1 + (self.power - 1) * 0.5)

        if now - self.last_shot > current_shoot_delay:
            self.last_shot = now
            if self.power == 1:
                self.game.bullets.append(PlayerBullet(self.x + self.w // 2 - 2, self.y, 4, 15))
            elif self.power == 2:
                self.game.bullets.append(PlayerBullet(self.x + 10, self.y, 6, 18))
                self.game.bullets.append(PlayerBullet(self.x + self.w - 10 - 6, self.y, 6, 18))
            elif self.power == 3:
                self.game.bullets.append(PlayerBullet(self.x + self.w // 2 - 3, self.y, 6, 20))
                self.game.bullets.append(PlayerBullet(self.x + 5, self.y + 10, 6, 18))
                self.game.bullets.append(PlayerBullet(self.x + self.w - 5 - 6, self.y + 10, 6, 18))
            
            for wing in self.game.side_wings: 
                if wing.active:
                    wing.shoot()

    def powerup(self):
        if self.power < 3:
            self.power += 1

    def gain_life(self):
        if self.lives < 3:
            self.lives += 1

    def add_wing(self):
        if self.wing_count < 2:
            self.wing_count += 1
            if self.wing_count == 1:
                self.game.side_wings.append(SideWing(self.game.player, -1)) 
            elif self.wing_count == 2:
                self.game.side_wings.append(SideWing(self.game.player, 1)) 
            
            if len(self.game.side_wings) >= 1:
                self.game.side_wings[0].offset_x = -70 
                self.game.side_wings[0].offset_y = 0
            if len(self.game.side_wings) >= 2:
                self.game.side_wings[1].offset_x = 70
                self.game.side_wings[1].offset_y = 0

    def activate_ultimate(self):
        self.ultimate_gauge = 0 
        self.ultimate_active = True
        self.ultimate_active_timer = pyxel.frame_count * (1000 / FPS)
        self.last_ultimate_shot = pyxel.frame_count * (1000 / FPS) 

    def hide(self):
        self.visible = False 
        self.hidden = True
        self.hide_timer = pyxel.frame_count * (1000 / FPS) 
        self.x = -1000 
        self.y = -1000

        for wing in self.game.side_wings: 
            wing.active = False 
        self.game.side_wings = [] 
        self.wing_count = 0

    def draw(self):
        if self.visible: 
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_BLUE)


class SideWing:
    def __init__(self, parent_player, side): 
        self.w = 30
        self.h = 25
        self.parent = parent_player
        self.side = side 
        self.offset_x = 0
        self.offset_y = 0
        self.x = self.parent.x + self.parent.w // 2 + self.offset_x - self.w // 2 
        self.y = self.parent.y + self.parent.h // 2 + self.offset_y - self.h // 2
        self.shoot_delay = 300
        self.last_shot = pyxel.frame_count * (1000 / FPS)
        self.active = True

    def update(self):
        self.x = self.parent.x + self.parent.w // 2 + self.offset_x - self.w // 2
        self.y = self.parent.y + self.parent.h // 2 + self.offset_y - self.h // 2

    def shoot(self):
        now = pyxel.frame_count * (1000 / FPS)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.parent.game.bullets.append(PlayerBullet(self.x + self.w // 2 - 2, self.y, 4, 15)) 

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_GREEN)