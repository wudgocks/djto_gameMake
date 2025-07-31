# item.py

import pyxel
import random
# config.py 에 정의된 상수 사용을 위해 주석 처리 (main.py에 포함 시)
from config import * 

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