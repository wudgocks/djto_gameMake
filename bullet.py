# bullet.py

import pyxel
import math
from config import * 

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