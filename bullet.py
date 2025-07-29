# PlayerBullet 및 EnemyBullet 클래스

# bullet.py
import pyxel
from config import WIDTH, HEIGHT, COLOR_YELLOW, COLOR_LIGHT_GREY

class PlayerBullet:
    def __init__(self, x, y, w, h, speedx=0, speedy=-10):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speedx = speedx # 궁극기 총알을 위해 추가
        self.speedy = speedy # 일반 총알의 기본값은 위로(-10)
        self.active = True

    def update(self):
        if not self.active: return
        self.x += self.speedx # x축 이동 적용
        self.y += self.speedy
        if self.y + self.h < 0 or self.x < -self.w or self.x > WIDTH: # 화면 밖으로 나가면 비활성화
            self.active = False

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_YELLOW)


class EnemyBullet:
    def __init__(self, x, y, speedx=0, speedy=7): # speedx, speedy 인자를 받을 수 있도록 변경
        self.x = x
        self.y = y
        self.w = 6
        self.h = 12
        self.speedx = speedx
        self.speedy = speedy
        self.active = True

    def update(self):
        if not self.active: return
        self.x += self.speedx
        self.y += self.speedy
        if self.y > HEIGHT or self.y + self.h < 0 or \
           self.x > WIDTH or self.x + self.w < 0:
            self.active = False

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_LIGHT_GREY)