import pyxel
import random
import math

# 게임 상수 (Pygame과 동일하게 유지)
WIDTH = 480
HEIGHT = 640
FPS = 60 

# Pyxel 색상 팔레트 (RGB 대신 0-15 인덱스)
COLOR_BLACK = 0
COLOR_WHITE = 7
COLOR_RED = 8
COLOR_GREEN = 11
COLOR_BLUE = 6
COLOR_YELLOW = 9
COLOR_LIGHT_GREY = 13
COLOR_ORANGE = 10
COLOR_PURPLE = 5
COLOR_CYAN = 12
COLOR_BOSS = 8
COLOR_ULTIMATE = 10 # 궁극기 게이지 색상

# 충돌 감지 함수 (Pyxel은 sprite 모듈이 없으므로 직접 구현)
def is_colliding(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
    return (obj1_x < obj2_x + obj2_w and
            obj1_x + obj1_w > obj2_x and
            obj1_y < obj2_y + obj2_h and
            obj1_y + obj1_h > obj2_y)

# --- 게임 오브젝트 클래스 정의 ---

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
                self.game.spawn_ultimate_bullets() 

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

    def update(self):
        if not self.active: return

        self.y += self.speedy
        self.x += self.speedx 

        if self.x < 0 or self.x + self.w > WIDTH:
            self.speedx *= -1

        if self.y > HEIGHT + 10 or self.x < -25 or self.x > WIDTH + 20:
            self.reset()
        
        now = pyxel.frame_count * (1000 / FPS)
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h))

    def reset(self):
        self.x = random.randrange(WIDTH - self.w)
        self.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.choice([-1, 1]) * random.randrange(0, 2) 
        self.active = True

    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_RED)


class Boss:
    def __init__(self, game_ref):
        self.game = game_ref 
        self.w = 150
        self.h = 150
        self.x = (WIDTH - self.w) // 2
        self.y = -200
        self.speedy = 1
        self.speedx = 2
        self.hp = 1000
        self.shoot_delay = 500
        self.last_shot = pyxel.frame_count * (1000 / FPS)
        self.state = "DESCENDING"
        self.active = True

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
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        for angle_deg in angles:
            rad = math.radians(angle_deg)
            dx = bullet_speed * math.cos(rad)
            dy = bullet_speed * math.sin(rad)
            self.game.enemy_bullets.append(EnemyBullet(self.x + self.w // 2 - 3, self.y + self.h // 2 - 6, dx, dy))


    def draw(self):
        if self.active:
            pyxel.rect(self.x, self.y, self.w, self.h, COLOR_BOSS)


class PlayerBullet:
    # speedx를 추가하여 초기화 시 받을 수 있도록 함. (기본값은 0)
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
    def __init__(self, x, y, speedx=0, speedy=7):
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


# --- Game 클래스 (메인 게임 루프) ---

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
        self.boss_instance = None
        self.boss_spawned = False
        self.score = 0
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
        for i in range(5):
            self.enemies.append(Enemy(self)) 
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_RETURN) and not self.game_started:
            self.game_started = True
        
        if pyxel.btnp(pyxel.KEY_R) and self.game_over:
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
        if not self.boss_spawned and self.score >= self.boss_score_threshold and not self.boss_instance:
            for enemy in self.enemies:
                enemy.active = False
            self.enemies = []

            self.boss_instance = Boss(self) 
            self.boss_spawned = True
        
        # 플레이어 총알과 적 충돌 처리
        for enemy in self.enemies:
            for bullet in self.bullets:
                if bullet.active and enemy.active and \
                   is_colliding(bullet.x, bullet.y, bullet.w, bullet.h, enemy.x, enemy.y, enemy.w, enemy.h):
                    enemy.active = False
                    bullet.active = False
                    self.score += 100
                    # **수정: 적 파괴 시 궁극기 게이지 증가량을 500으로 변경**
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
                        for eb in self.enemy_bullets:
                            eb.active = False
                        self.enemy_bullets = []
                        
                        self.boss_instance = None
                        self.boss_spawned = False
                        self.reset_game_objects() 
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
                    for remaining_eb in self.enemy_bullets:
                        remaining_eb.active = False
                    self.enemy_bullets = []

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
                fill = (self.boss_instance.hp / 1000) * bar_length
                
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