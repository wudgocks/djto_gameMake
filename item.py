# Item 클래스

# item.py
import pyxel
from config import WIDTH, HEIGHT, COLOR_ORANGE, COLOR_PURPLE, COLOR_CYAN

class Item:
    def __init__(self, x, y, item_type):
        self.x = x - 10
        self.y = y - 10
        self.w = 20
        self.h = 20
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
            color = COLOR_ORANGE
            if self.type == 'hp_up':
                color = COLOR_PURPLE
            elif self.type == 'wing':
                color = COLOR_CYAN
            pyxel.rect(self.x, self.y, self.w, self.h, color)