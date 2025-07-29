# main.py
import pyxel
import random
import math

# 각 모듈에서 필요한 클래스와 상수를 임포트
from config import (
    WIDTH, HEIGHT, FPS, 
    COLOR_BLACK, COLOR_WHITE, COLOR_RED, COLOR_GREEN, 
    COLOR_BLUE, COLOR_YELLOW, COLOR_LIGHT_GREY, COLOR_ORANGE, 
    COLOR_PURPLE, COLOR_CYAN, COLOR_BOSS, COLOR_ULTIMATE
)
from utils import is_colliding
from player import Player, SideWing
from enemy import Enemy, Boss
from bullet import PlayerBullet, EnemyBullet
from item import Item

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="1945 Shooter Pyxel", fps=FPS)
        
        self.player = Player(self) 
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.items = []
        self.side_wings = []
        self.boss_instance = None
        self.boss_spawned = False
        self.current_boss_type = 1 # 현재 보스 타입 추적
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.boss_score_threshold = 2000

        self.reset_game_objects()
        pyxel.run(self.update, self.draw)

    def reset_game_objects(self):
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.items = []
        self.side_wings = [] 
        # self.score = 0 # 점수는 게임 오버 시에만 초기화되어야 함 (주석 처리 또는 if self.game_over: 조건 추가)
        self.game_over = False

        # 플레이어 초기 상태 재설정
        self.player.x = (WIDTH - self.player.w) // 2
        self.player.y = HEIGHT - 20 - self.player.h
        self.player.power = 1
        self.player.lives = 3
        self.player.hidden = False
        self.player.invincible = False
        self.player.wing_count = 0
        self.player.visible = True
        self.player.ultimate_gauge = 0 # 궁극기 게이지 초기화

        # 초기 적 생성
        if not self.boss_instance: # 보스가 없을 때만 일반 적 생성
            for i in range(5):
                self.enemies.append(Enemy(self)) 
    
    def spawn_boss(self, boss_type): # 보스 생성 함수 추가
        for enemy in self.enemies:
            enemy.active = False # 기존 적들 비활성화
        self.enemies = [] # 적 리스트 비우기
        self.boss_instance = Boss(self, boss_type)
        self.boss_spawned = True
        self.enemy_bullets = [] # 보스 등장 시 기존 적 총알 제거

    def update(self):
        if pyxel.btnp(pyxel.KEY_RETURN) and not self.game_started:
            self.game_started = True
            
        if pyxel.btnp(pyxel.KEY_R) and self.game_over:
            self.score = 0 # 게임 오버 시에만 점수 초기화
            self.current_boss_type = 1 # 보스 타입도 초기화
            self.reset_game_objects()
            self.game_started = True

        if not self.game_started or self.game_over:
            return

        self.player.update()
        for enemy in self.enemies: 
            enemy.update()
        for bullet in self.bullets: 
            bullet.update()
        for eb in self.enemy_bullets: 
            eb.update()
        for item in self.items: 
            item.update()
        for wing in self.side_wings: 
            wing.update()
        
        if self.boss_instance and self.boss_instance.active:
            self.boss_instance.update()

        # 죽거나 비활성화된 오브젝트 제거
        self.enemies[:] = [e for e in self.enemies if e.active]
        self.bullets[:] = [b for b in self.bullets if b.active]
        self.enemy_bullets[:] = [eb for eb in self.enemy_bullets if eb.active]
        self.items[:] = [item for item in self.items if item.active]
        self.side_wings[:] = [wing for wing in self.side_wings if wing.active]


        # 보스 등장 조건
        # score 대신 current_boss_type을 기준으로 보스 등장 시점 제어
        if not self.boss_spawned and not self.boss_instance: # 보스가 없고 스폰되지 않았다면
            if self.current_boss_type == 1 and self.score >= self.boss_score_threshold:
                self.spawn_boss(1)
            elif self.current_boss_type == 2 and self.score >= self.boss_score_threshold + 5000: # 2번째 보스
                self.spawn_boss(2)
            elif self.current_boss_type == 3 and self.score >= self.boss_score_threshold + 15000: # 3번째 보스
                self.spawn_boss(3)
            # TODO: 더 많은 보스 등장 조건 추가

        # 플레이어 총알과 적 충돌 처리
        for enemy in self.enemies:
            for bullet in self.bullets:
                if bullet.active and enemy.active and \
                    is_colliding(bullet.x, bullet.y, bullet.w, bullet.h, enemy.x, enemy.y, enemy.w, enemy.h):
                    enemy.hp -= 10 # 적 체력 감소
                    bullet.active = False
                    if enemy.hp <= 0: # 적 체력이 0 이하면
                        enemy.active = False
                        self.score += 100
                        self.player.ultimate_gauge = min(self.player.ultimate_gauge + 500, self.player.ultimate_max_gauge)
                        
                        drop_chance = random.random()
                        item_type_to_drop = None
                        if drop_chance < 0.15:
                            item_type_to_drop = 'powerup'
                        elif drop_chance < 0.20:
                            item_type_to_drop = 'hp_up'
                        elif drop_chance < 0.25:
                            item_type_to_drop = 'wing'
                        
                        if item_type_to_drop:
                            self.items.append(Item(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, item_type_to_drop))
            
            # 적이 죽거나 화면 밖으로 나갔을 때 새로운 적 생성 (보스 없을 때만)
            if not self.boss_instance and not enemy.active and enemy.y < HEIGHT:
                self.enemies.append(Enemy(self))


        # 플레이어 총알과 보스 충돌 처리
        if self.boss_instance and self.boss_instance.active and self.boss_instance.state == "ATTACKING":
            for bullet in self.bullets:
                if bullet.active and \
                    is_colliding(bullet.x, bullet.y, bullet.w, bullet.h, self.boss_instance.x, self.boss_instance.y, self.boss_instance.w, self.boss_instance.h):
                    bullet.active = False
                    self.boss_instance.hp -= 10
                    if self.boss_instance.hp <= 0:
                        self.boss_instance.state = "DEFEATED"
                        self.score += 5000
                        for eb in self.enemy_bullets: # 보스가 죽으면 모든 총알 제거
                            eb.active = False
                        self.enemy_bullets = []
                        
                        self.boss_instance = None # 보스 인스턴스 초기화
                        self.boss_spawned = False # 보스 스폰 상태 초기화
                        self.current_boss_type += 1 # 다음 보스 타입으로 증가
                        self.player.ultimate_gauge = min(self.player.ultimate_gauge + self.player.ultimate_max_gauge / 2, self.player.ultimate_max_gauge) # 보스 잡으면 궁극기 게이지 절반 채워주기
                        self.reset_game_objects() # 게임 오브젝트만 초기화 (점수, 보스 타입은 유지)
                        self.game_started = True 
                        break


        # 적 총알과 플레이어 충돌 처리
        if not self.player.invincible:
            for eb in self.enemy_bullets:
                if eb.active and \
                    is_colliding(eb.x, eb.y, eb.w, eb.h, self.player.x, self.player.y, self.player.w, self.player.h):
                    eb.active = False
                    self.player.lives -= 1
                    self.player.hide() 
                    for remaining_eb in self.enemy_bullets: # 플레이어 피격 시 모든 적 총알 제거
                        remaining_eb.active = False
                    self.enemy_bullets = []

                    if self.player.lives <= 0:
                        self.game_over = True
                    break

        # 플레이어와 적 충돌 처리 (이제 적도 체력이 있으므로, 플레이어와 충돌하면 플레이어 체력만 감소)
        if not self.player.invincible:
            for enemy in self.enemies:
                if enemy.active and \
                   is_colliding(self.player.x, self.player.y, self.player.w, self.player.h, enemy.x, enemy.y, enemy.w, enemy.h):
                    enemy.active = False # 적은 파괴
                    self.player.lives -= 1 # 플레이어 체력 감소
                    self.player.hide()
                    
                    if self.player.lives <= 0:
                        self.game_over = True
                    break


        # 플레이어와 아이템 충돌 처리
        for item in self.items:
            if item.active and \
                is_colliding(item.x, item.y, item.w, item.h, self.player.x, self.player.y, self.player.w, self.player.h):
                item.active = False
                if item.type == 'powerup':
                    self.player.powerup()
                elif item.type == 'hp_up':
                    self.player.gain_life()
                elif item.type == 'wing':
                    self.player.add_wing()

    # 궁극기 총알 생성 함수
    def spawn_ultimate_bullets(self):
        num_bullets = 10 
        spread_angle = 120 
        base_angle = 90 

        for i in range(num_bullets):
            angle_offset = (i - (num_bullets - 1) / 2) * (spread_angle / num_bullets)
            angle_deg = base_angle + angle_offset
            
            rad = math.radians(angle_deg)
            bullet_speed = 10
            dx = bullet_speed * math.cos(rad)
            dy = -bullet_speed * math.sin(rad) 

            # PlayerBullet의 __init__에 speedx, speedy를 전달하도록 수정
            self.bullets.append(PlayerBullet(self.player.x + self.player.w // 2 - 3, self.player.y, 6, 15, speedx=dx, speedy=dy))


    def draw(self):
        pyxel.cls(COLOR_BLACK)

        # 텍스트 중앙 정렬 및 확대 효과 (여러 번 겹쳐 그리기)
        if not self.game_started:
            title_text = "1945 Style Shooter"
            start_text = "Press ENTER to Start"
            
            base_x_title = WIDTH // 2 - (len(title_text) * 4) 
            base_y_title = HEIGHT // 4
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    pyxel.text(base_x_title + dx, base_y_title + dy, title_text, COLOR_LIGHT_GREY if (dx, dy) != (0, 0) else COLOR_WHITE)

            base_x_start = WIDTH // 2 - (len(start_text) * 4)
            base_y_start = HEIGHT // 2
            pyxel.text(base_x_start + 1, base_y_start + 1, start_text, COLOR_BLACK) 
            pyxel.text(base_x_start, base_y_start, start_text, COLOR_WHITE) 
            
        elif self.game_over:
            gameover_text = "GAME OVER"
            score_text = f"Score: {self.score}"
            restart_text = "Press 'R' to Restart"
            
            base_x_go = WIDTH // 2 - (len(gameover_text) * 4)
            base_y_go = HEIGHT // 4
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    pyxel.text(base_x_go + dx, base_y_go + dy, gameover_text, COLOR_RED if (dx, dy) != (0, 0) else COLOR_WHITE)

            base_x_score = WIDTH // 2 - (len(score_text) * 4)
            base_y_score = HEIGHT // 2 - 20
            pyxel.text(base_x_score, base_y_score, score_text, COLOR_WHITE)
            
            base_x_restart = WIDTH // 2 - (len(restart_text) * 4)
            base_y_restart = HEIGHT // 2 + 40
            pyxel.text(base_x_restart, base_y_restart, restart_text, COLOR_WHITE)

        else: # 게임 플레이 중
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()
            for bullet in self.bullets:
                bullet.draw()
            for eb in self.enemy_bullets:
                eb.draw()
            for item in self.items:
                item.draw()
            for wing in self.side_wings:
                wing.draw()

            if self.boss_instance and self.boss_instance.active:
                self.boss_instance.draw()

            # UI 텍스트 그리기
            score_ui_text = f"Score: {self.score}"
            power_ui_text = f"P:{self.player.power}"
            
            pyxel.text(WIDTH // 2 - (len(score_ui_text) * 4), 10, score_ui_text, COLOR_WHITE) 
            self.draw_lives(10, 10, self.player.lives, 3)
            pyxel.text(WIDTH - (len(power_ui_text) * 8) - 10, 10, power_ui_text, COLOR_ORANGE) 

            # 궁극기 게이지 그리기
            gauge_width = 100
            gauge_height = 8
            gauge_x = WIDTH // 2 - gauge_width // 2
            gauge_y = HEIGHT - 20
            fill_width = (self.player.ultimate_gauge / self.player.ultimate_max_gauge) * gauge_width
            
            pyxel.rect(gauge_x, gauge_y, fill_width, gauge_height, COLOR_ULTIMATE) # 채워진 부분
            pyxel.rectb(gauge_x, gauge_y, gauge_width, gauge_height, COLOR_WHITE) # 테두리
            pyxel.text(gauge_x + gauge_width // 2 - 16, gauge_y - 10, "ULT", COLOR_WHITE)


            if self.boss_instance and self.boss_instance.active and self.boss_instance.state == "ATTACKING":
                bar_length = 200
                bar_height = 8
                # 보스의 최대 HP를 기준으로 HP 바 길이를 계산해야 합니다.
                boss_max_hp = 0
                if self.boss_instance.boss_type == 1: boss_max_hp = 1000
                elif self.boss_instance.boss_type == 2: boss_max_hp = 1500
                elif self.boss_instance.boss_type == 3: boss_max_hp = 2000
                
                fill = (self.boss_instance.hp / boss_max_hp) * bar_length 
                
                pyxel.rect(WIDTH // 2 - bar_length // 2, 20, fill, bar_height, COLOR_GREEN)
                pyxel.rectb(WIDTH // 2 - bar_length // 2, 20, bar_length, bar_height, COLOR_WHITE)

    def draw_lives(self, x, y, lives, max_lives):
        for i in range(max_lives):
            if i < lives:
                pyxel.rect(x + i * 20, y, 15, 10, COLOR_GREEN)
            else:
                pyxel.rectb(x + i * 20, y, 15, 10, COLOR_LIGHT_GREY)


if __name__ == "__main__":
    Game()