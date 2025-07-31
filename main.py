# main.py

import pyxel
import random
import math

# 다른 파일에서 클래스와 상수를 가져옵니다.
# 실제 실행 시에는 아래 import 문을 사용하여 파일들을 분리하거나,
# 모든 코드를 하나의 파일에 순서대로 붙여넣을 수 있습니다.

# config.py 에서 모든 상수 가져오기
from config import *
# bullet.py 에서 클래스 가져오기
from bullet import *
# player.py 에서 클래스 가져오기
from player import *
# enemy.py 에서 클래스 가져오기
from enemy import Enemy, Boss
# item.py 에서 클래스 가져오기
from item import Item


class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="1945 Shooter Enhanced", fps=FPS)

        self.player = Player(WIDTH / 2, HEIGHT - 30)
        self.player_bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.items = []

        self.boss = None
        self.current_stage = 1
        self.stage_timer = 0
        self.enemies_spawned_this_stage = 0
        self.stage_completed = False

        self.ultimate_gauge = 0 # 궁극기 게이지 추가
        self.ultimate_effect_timer = 0 # 궁극기 이펙트 타이머

        self.game_state = "TITLE"

        pyxel.run(self.update, self.draw)

    def _start_game(self):
        self.game_state = "PLAYING"
        self.player = Player(WIDTH / 2, HEIGHT - 30)
        self.player_bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.items = []
        self.boss = None
        self.current_stage = 1
        self.stage_timer = 0
        self.enemies_spawned_this_stage = 0
        self.stage_completed = False
        self.ultimate_gauge = 0 # 게임 시작 시 게이지 초기화
        self.ultimate_effect_timer = 0 # 이펙트 타이머 초기화
        pyxel.pal() # 게임 시작 시 팔레트 리셋 (혹시 이전 게임의 궁극기 효과가 남아있을 수 있으므로)

    def update(self):
        if self.game_state == "TITLE":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self._start_game()
        elif self.game_state == "PLAYING":
            self._update_playing()
        elif self.game_state == "GAME_OVER" or self.game_state == "STAGE_CLEAR":
            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.game_state == "STAGE_CLEAR":
                    if self.current_stage < 2:
                        self.current_stage += 1
                        self.enemies_spawned_this_stage = 0
                        self.stage_timer = 0
                        self.enemies = []
                        self.enemy_bullets = []
                        self.items = []
                        self.boss = None
                        self.stage_completed = False
                        self.game_state = "PLAYING"
                        pyxel.pal() # 다음 스테이지 진입 시 팔레트 리셋
                    else:
                        self._start_game()
                else:
                    self._start_game()

    def _update_playing(self):
        self.stage_timer += 1

        self.player.update()
        if pyxel.btn(pyxel.KEY_SPACE):
            new_bullets = self.player.shoot()
            if new_bullets:
                self.player_bullets.extend(new_bullets)

        # 궁극기 사용 (F 키)
        if pyxel.btnp(pyxel.KEY_F) and self.ultimate_gauge >= ULTIMATE_GAUGE_MAX:
            self._activate_ultimate()

        # 궁극기 이펙트 타이머 감소
        if self.ultimate_effect_timer > 0:
            self.ultimate_effect_timer -= 1
            if self.ultimate_effect_timer == 0:
                pyxel.pal() # 팔레트 리셋


        for bullet in self.player_bullets:
            bullet.update()
        self.player_bullets = [b for b in self.player_bullets if b.active]

        current_stage_enemies_limit = 0
        if self.current_stage == 1:
            current_stage_enemies_limit = STAGE1_ENEMY_COUNT
        elif self.current_stage == 2:
            current_stage_enemies_limit = STAGE2_ENEMY_COUNT

        # 보스가 없으면 일반 적 스폰 (보스 등장 후에는 일반 적 스폰 중단)
        if self.boss is None and self.enemies_spawned_this_stage < current_stage_enemies_limit:
            # 보스 등장 시간을 고려하여 적 스폰을 멈추고 보스를 생성
            if self.current_stage == 1 and self.stage_timer >= STAGE1_BOSS_ACTIVE_TIME:
                self.enemies_spawned_this_stage = current_stage_enemies_limit # 더 이상 일반 적 스폰 안함
            elif self.current_stage == 2 and self.stage_timer >= STAGE2_BOSS_ACTIVE_TIME:
                self.enemies_spawned_this_stage = current_stage_enemies_limit # 더 이상 일반 적 스폰 안함
            else: # 보스 등장 시간 전에는 계속 스폰
                if pyxel.frame_count % 60 == 0:
                    enemy_x = random.randint(0, WIDTH - ENEMY_SIZE)
                    enemy_y = -ENEMY_SIZE
                    enemy_types = ["A", "B", "C", "D"]
                    selected_type = random.choice(enemy_types)

                    self.enemies.append(Enemy(enemy_x, enemy_y, selected_type, self.player))
                    self.enemies_spawned_this_stage += 1


        new_enemy_bullets = []
        
        active_enemies = []
        for enemy in self.enemies:
            enemy_bullets_from_enemy = enemy.update(self.player.x, self.player.y)
            new_enemy_bullets.extend(enemy_bullets_from_enemy)

            if enemy.is_alive:
                active_enemies.append(enemy)
        self.enemies = active_enemies # 죽은 적 제거는 _handle_collisions에서 최종적으로 처리

        # 보스 등장 조건 및 보스 생성
        # 모든 일반 적이 스폰되었고, 보스가 아직 없으면 보스 생성
        if self.boss is None and self.enemies_spawned_this_stage >= current_stage_enemies_limit:
            if self.current_stage == 1:
                self.boss = Boss(WIDTH / 2 - BOSS_WIDTH / 2, 20, self.player)
            elif self.current_stage == 2:
                self.boss = Boss(WIDTH / 2 - BOSS_WIDTH / 2, 20, self.player)


        if self.boss:
            boss_bullets, boss_minions = self.boss.update()
            self.enemy_bullets.extend(boss_bullets)
            self.enemies.extend(boss_minions)
            # 보스가 죽으면 스테이지 완료 처리 및 아이템 드랍
            if not self.boss.is_alive:
                self.boss = None
                self.stage_completed = True
                if random.random() < ITEM_BOSS_DROP_PROBABILITY: # 보스는 항상 드랍
                    self.items.append(Item(WIDTH / 2, HEIGHT / 2, random.choice(['hp_up', 'wing', 'option']))) # 보스 드랍 아이템


        self.enemy_bullets.extend(new_enemy_bullets)

        for bullet in self.enemy_bullets:
            bullet.update()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.active]

        for item in self.items:
            item.update()
        self.items = [i for i in self.items if i.active]


        self._handle_collisions()

        if self.player.hp <= 0:
            self.game_state = "GAME_OVER"

        self._check_stage_completion()

    def _handle_collisions(self):
        # 플레이어 총알과 적 충돌
        new_player_bullets = []
        for bullet in self.player_bullets:
            hit_enemy = False
            for enemy in self.enemies:
                if bullet.active and enemy.is_alive and self._is_colliding(bullet, enemy):
                    enemy.take_damage(1)
                    bullet.active = False
                    hit_enemy = True
                    break
            if not hit_enemy:
                new_player_bullets.append(bullet)
        self.player_bullets = new_player_bullets

        # 죽은 적 처리 및 아이템 드랍/게이지 충전
        active_enemies_after_damage = []
        for enemy in self.enemies:
            if enemy.is_alive:
                active_enemies_after_damage.append(enemy)
            else:
                # 적 사망 시 아이템 드랍
                if random.random() < ITEM_DROP_PROBABILITY:
                    self.items.append(Item(enemy.x + enemy.w / 2, enemy.y + enemy.h / 2, random.choice(['hp_up', 'wing', 'option'])))
                self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_KILL) # 궁극기 게이지 충전
        self.enemies = active_enemies_after_damage


        # 플레이어 총알과 보스 충돌
        if self.boss and self.boss.is_alive:
            new_player_bullets_for_boss = []
            for bullet in self.player_bullets:
                if bullet.active and self._is_colliding(bullet, self.boss):
                    if self._is_colliding(bullet, self.boss, is_weak_point=True):
                        self.boss.take_damage(1, is_weak_point_hit=True)
                    else:
                        self.boss.take_damage(1)
                    bullet.active = False
                    self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_BOSS_HIT) # 보스 타격 시 게이지 충전
                if bullet.active:
                    new_player_bullets_for_boss.append(bullet)
            self.player_bullets = new_player_bullets_for_boss

        # 적 총알과 플레이어 충돌
        if self.player.is_alive:
            new_enemy_bullets_after_player_hit = []
            for e_bullet in self.enemy_bullets:
                if e_bullet.active and self._is_colliding(e_bullet, self.player):
                    self.player.take_damage(1)
                    e_bullet.active = False
                if e_bullet.active:
                    new_enemy_bullets_after_player_hit.append(e_bullet)
            self.enemy_bullets = new_enemy_bullets_after_player_hit

        # 적과 플레이어 충돌 (적이 플레이어에게 직접 박는 경우)
        if self.player.is_alive:
            active_enemies_after_player_collision = []
            for enemy in self.enemies:
                if enemy.is_alive and self._is_colliding(enemy, self.player):
                    self.player.take_damage(999) # 즉사
                    enemy.is_alive = False
                    self.ultimate_gauge = min(ULTIMATE_GAUGE_MAX, self.ultimate_gauge + ULTIMATE_GAUGE_PER_KILL) # 궁극기 게이지 충전
                if enemy.is_alive:
                    active_enemies_after_player_collision.append(enemy)
            self.enemies = active_enemies_after_player_collision


        # 아이템과 플레이어 충돌
        if self.player.is_alive:
            new_items_after_pickup = []
            for item in self.items:
                if item.active and self._is_colliding(item, self.player):
                    if item.type == 'hp_up':
                        self.player.gain_hp(1)
                    elif item.type == 'wing':
                        self.player.power_up('wing')
                    elif item.type == 'option':
                        self.player.power_up('option')
                    item.active = False
                if item.active:
                    new_items_after_pickup.append(item)
            self.items = new_items_after_pickup


    def _is_colliding(self, obj1, obj2, is_weak_point=False):
        if is_weak_point and hasattr(obj2, 'weak_point_x'):
            return (obj1.x < obj2.weak_point_x + obj2.weak_point_w and
                    obj1.x + obj1.w > obj2.weak_point_x and
                    obj1.y < obj2.weak_point_y + obj2.weak_point_h and
                    obj1.y + obj1.h > obj2.weak_point_y)
        else:
            return (obj1.x < obj2.x + obj2.w and
                    obj1.x + obj1.w > obj2.x and
                    obj1.y < obj2.y + obj2.h and
                    obj1.y + obj1.h > obj2.y)

    def _activate_ultimate(self):
        # 궁극기 발동 시 게이지 소모
        self.ultimate_gauge = 0
        num_bullets = 24 # 발사할 총알 수
        for i in range(num_bullets):
            angle = 2 * math.pi * i / num_bullets
            dx = math.cos(angle)
            dy = math.sin(angle)
            bullet_x = self.player.x + self.player.w / 2 - PLAYER_START_BULLET_W / 2
            bullet_y = self.player.y
            # 사방으로 발사하는 총알은 플레이어 총알 속도를 기준으로 하되, 방향을 dx, dy로 조절
            self.player_bullets.append(PlayerBullet(bullet_x, bullet_y, PLAYER_START_BULLET_W, PLAYER_START_BULLET_H, speedy=dy * PLAYER_BULLET_SPEED, speedx=dx * PLAYER_BULLET_SPEED))

        # 궁극기 이펙트 유지 (색상 반전)
        pyxel.pal(0, 7)
        pyxel.pal(7, 0)
        pyxel.pal(COLOR_BLUE, COLOR_RED)
        pyxel.pal(COLOR_RED, COLOR_BLUE)
        self.ultimate_effect_timer = ULTIMATE_EFFECT_DURATION

    def _check_stage_completion(self):
        if self.boss is None and self.stage_completed:
            if self.current_stage < 2:
                self.game_state = "STAGE_CLEAR"
            else:
                self.game_state = "GAME_OVER"

    def draw(self):
        # 궁극기 이펙트가 활성화된 동안 배경 색상 변경
        if self.ultimate_effect_timer > 0:
            pyxel.cls(COLOR_WHITE if pyxel.frame_count % 4 < 2 else COLOR_BLACK) # 화면 깜빡임 효과
        elif self.current_stage == 1:
            pyxel.cls(STAGE1_BACKGROUND_COLOR)
        elif self.current_stage == 2:
            pyxel.cls(STAGE2_BACKGROUND_COLOR)


        if self.game_state == "TITLE":
            title_text = "1945 Shooter"
            start_text = "PRESS RETURN TO START"
            pyxel.text(WIDTH / 2 - len(title_text) * 4 / 2, HEIGHT / 2 - 10, title_text, COLOR_WHITE)
            pyxel.text(WIDTH / 2 - len(start_text) * 4 / 2, HEIGHT / 2 + 10, start_text, COLOR_YELLOW)
        elif self.game_state == "PLAYING":
            self.player.draw()
            for bullet in self.player_bullets:
                bullet.draw()
            for enemy in self.enemies:
                enemy.draw()
            for e_bullet in self.enemy_bullets:
                e_bullet.draw()
            for item in self.items:
                item.draw()
            if self.boss:
                self.boss.draw()

            # HUD (Head-Up Display)
            pyxel.text(5, 5, f"HP: {self.player.hp}", COLOR_GREEN)
            pyxel.text(5, 15, f"STAGE: {self.current_stage}", COLOR_WHITE)

            # 궁극기 게이지 표시
            ultimate_gauge_text = "ULTIMATE (F)"
            pyxel.text(5, HEIGHT - 20, ultimate_gauge_text, COLOR_WHITE)
            pyxel.rect(5, HEIGHT - 10, ULTIMATE_GAUGE_MAX, 5, COLOR_BLACK) # 게이지 바 배경
            
            # 궁극기 게이지 가득 차면 깜빡임 효과
            if self.ultimate_gauge >= ULTIMATE_GAUGE_MAX and pyxel.frame_count % 10 < 5:
                pyxel.rect(5, HEIGHT - 10, self.ultimate_gauge, 5, COLOR_WHITE) # 흰색으로 깜빡
            else:
                pyxel.rect(5, HEIGHT - 10, self.ultimate_gauge, 5, COLOR_ULTIMATE_GAUGE) # 원래 색상

            # 궁극기 발동 시 메시지 표시
            if self.ultimate_effect_timer > 0:
                ultimate_message = "ULTIMATE!"
                pyxel.text(WIDTH / 2 - len(ultimate_message) * 4 / 2, HEIGHT / 2 - 20, ultimate_message, COLOR_YELLOW)


            current_stage_enemies_limit = 0
            if self.current_stage == 1:
                current_stage_enemies_limit = STAGE1_ENEMY_COUNT
            elif self.current_stage == 2:
                current_stage_enemies_limit = STAGE2_ENEMY_COUNT

            if self.boss is None and self.enemies_spawned_this_stage < current_stage_enemies_limit:
                enemies_remaining_text = f"ENEMIES REMAINING: {current_stage_enemies_limit - self.enemies_spawned_this_stage}"
                pyxel.text(WIDTH - len(enemies_remaining_text) * 4 - 5, 5, enemies_remaining_text, COLOR_WHITE)
            elif self.boss and self.boss.is_alive:
                boss_active_text = "BOSS ACTIVE"
                pyxel.text(WIDTH - len(boss_active_text) * 4 - 5, 15, boss_active_text, COLOR_RED)


        elif self.game_state == "GAME_OVER":
            game_over_text = "GAME OVER"
            restart_text = "PRESS RETURN TO RESTART"
            pyxel.text(WIDTH / 2 - len(game_over_text) * 4 / 2, HEIGHT / 2 - 10, game_over_text, COLOR_RED)
            pyxel.text(WIDTH / 2 - len(restart_text) * 4 / 2, HEIGHT / 2 + 10, restart_text, COLOR_YELLOW)
        elif self.game_state == "STAGE_CLEAR":
            stage_clear_text = f"STAGE {self.current_stage} CLEAR!" # 현재 스테이지 +1이 아니라 현재 스테이지 번호가 나오도록 수정
            next_stage_text = "PRESS RETURN FOR NEXT STAGE"
            if self.current_stage == 2: # 마지막 스테이지 클리어 시
                next_stage_text = "PRESS RETURN TO RESTART" # 재시작 메시지로 변경
            pyxel.text(WIDTH / 2 - len(stage_clear_text) * 4 / 2, HEIGHT / 2 - 10, stage_clear_text, COLOR_GREEN)
            pyxel.text(WIDTH / 2 - len(next_stage_text) * 4 / 2, HEIGHT / 2 + 10, next_stage_text, COLOR_YELLOW)

Game()