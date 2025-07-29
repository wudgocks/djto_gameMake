# Enemy 및 Boss 클래스

# enemy.py
import pyxel
import random
import math
from config import WIDTH, HEIGHT, FPS, COLOR_RED, COLOR_BOSS, COLOR_PURPLE, COLOR_CYAN
from bullet import EnemyBullet # EnemyBullet 클래스 임포트

class Enemy:
    def __init__(self, game_ref):
        self.game = game_ref 
        self.w = 40
        self.h = 30
        self.x = random.randrange(WIDTH - self.w)
        self.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.choice([-1, 1]) * random.randrange(0, 2) 
        self.shoot_delay = random.randrange(1000, 3000)
        self.last_shot = pyxel.frame_count * (1000 / FPS)
        self.active = True
        self.hp = 10 # 적 체력 추가

    def update(self):
        if not self.active: return

        self.y += self.speedy
        self.x += self.speedx 

        if self.x < 0 or self.x + self.w > WIDTH:
            self.speedx *= -1

        if self.y > HEIGHT + 10 or self.x < -self.w or self.x > WIDTH + self.w: # 화면 밖으로 완전히 벗어나면
            self.reset()
            
        now = pyxel.frame_count * (1000 / FPS)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # 플레이어를 향해 총알 발사하도록 각도 계산
            player_center_x = self.game.player.x + self.game.player.w // 2
            player_center_y = self.game.player.y + self.game.player.h // 2
            
            enemy_center_x = self.x + self.w // 2
            enemy_center_y = self.y + self.h // 2
            
            # 플레이어와 적 사이의 벡터 계산
            dx = player_center_x - enemy_center_x
            dy = player_center_y - enemy_center_y
            
            # 각도 계산 (라디안)
            angle = math.atan2(dy, dx)
            
            # 총알 속도
            bullet_speed = 5
            speed_x = bullet_speed * math.cos(angle)
            speed_y = bullet_speed * math.sin(angle)
            
            self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h, speed_x, speed_y))

    def reset(self):
        self.x = random.randrange(WIDTH - self.w)
        self.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.choice([-1, 1]) * random.randrange(0, 2) 
        self.active = True
        self.hp = 10 # 체력 재설정

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_RED)


class Boss:
    def __init__(self, game_ref, boss_type=1): # 보스 타입 인자 추가
        self.game = game_ref 
        self.boss_type = boss_type
        self.w = 150
        self.h = 150
        self.x = (WIDTH - self.w) // 2
        self.y = -200
        self.speedy = 1
        self.speedx = 2
        self.shoot_delay = 500
        self.last_shot = pyxel.frame_count * (1000 / FPS)
        self.state = "DESCENDING"
        self.active = True

        # 보스 타입에 따른 설정
        if self.boss_type == 1:
            self.hp = 1000
            self.color = COLOR_BOSS # 기본 빨간색 보스
            self.shoot_delay = 500
        elif self.boss_type == 2:
            self.hp = 1500
            self.color = COLOR_PURPLE # 보라색 보스
            self.shoot_delay = 400
            self.speedx = 3 # 좀 더 빠름
        elif self.boss_type == 3:
            self.hp = 2000
            self.color = COLOR_CYAN # 청록색 보스
            self.shoot_delay = 300
            self.speedx = 4 # 더 빠름
        # TODO: 더 많은 보스 타입과 패턴 추가 가능

    def update(self):
        if not self.active: return

        current_time_ms = pyxel.frame_count * (1000 / FPS)

        if self.state == "DESCENDING":
            self.y += self.speedy
            if self.y >= 50:
                self.state = "ATTACKING"
                self.speedy = 0
        elif self.state == "ATTACKING":
            self.x += self.speedx
            if self.x < 0 or self.x + self.w > WIDTH:
                self.speedx *= -1

            now = pyxel.frame_count * (1000 / FPS)
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()
        
        elif self.state == "DEFEATED":
            self.active = False

    def shoot(self):
        bullet_speed = 3
        # 보스 타입에 따른 총알 패턴
        if self.boss_type == 1:
            # 8방향 기본 패턴
            angles = [0, 45, 90, 135, 180, 225, 270, 315]
            for angle_deg in angles:
                rad = math.radians(angle_deg)
                dx = bullet_speed * math.cos(rad)
                dy = bullet_speed * math.sin(rad)
                self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h // 2 - 6, dx, dy))
        elif self.boss_type == 2:
            # 플레이어를 조준하는 샷 + 3방향 확산
            player_center_x = self.game.player.x + self.game.player.w // 2
            player_center_y = self.game.player.y + self.game.player.h // 2
            
            boss_center_x = self.x + self.w // 2
            boss_center_y = self.y + self.h // 2
            
            target_angle = math.atan2(player_center_y - boss_center_y, player_center_x - boss_center_x)
            
            spread_angles = [-15, 0, 15] # 3방향 확산
            for offset_deg in spread_angles:
                angle_rad = target_angle + math.radians(offset_deg)
                dx = bullet_speed * math.cos(angle_rad)
                dy = bullet_speed * math.sin(angle_rad)
                self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h // 2 - 6, dx, dy))
        elif self.boss_type == 3:
            # 회전하며 샷 발사 (시간에 따라 각도 변화)
            num_bullets = 8
            base_angle_offset = (pyxel.frame_count * 5) % 360 # 프레임에 따라 각도 회전
            for i in range(num_bullets):
                angle_deg = (360 / num_bullets * i + base_angle_offset) % 360
                rad = math.radians(angle_deg)
                dx = bullet_speed * math.cos(rad)
                dy = bullet_speed * math.sin(rad)
                self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h // 2 - 6, dx, dy))

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, self.color) # 보스 색상 적용