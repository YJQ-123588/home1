import pygame
import os
from config.settings import *
from core.animation import Animation, load_swk2_frames, load_cattle_frames, load_magic_frames, load_cattle_die_frames


class FightScene:
    """回合制打斗场景 — 普攻/技能/大招"""

    STATE_INTRO = -1
    STATE_READY = 0
    STATE_PLAYER_ATK = 1
    STATE_MONSTER_HURT = 2
    STATE_MONSTER_ATK = 3
    STATE_PLAYER_HURT = 4
    STATE_WIN = 5
    STATE_LOSE = 6
    STATE_MONSTER_DIE = 7  # 怪物死亡动画

    def __init__(self, monster_name="牛妖", monster_hp=100, monster_max_hp=100, monster_atk=15,
                 is_boss=False, intro_text="", player_hp=PLAYER_BASE_HP,
                 player_max_hp=PLAYER_BASE_HP, player_atk=PLAYER_BASE_ATK,
                 ultimate_unlocked=False):
        # 战斗背景
        try:
            self.bg = pygame.image.load(TEMPLE_IMG).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 100))
            self.bg.blit(dark, (0, 0))
        except Exception:
            self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg.fill((50, 30, 20))

        # 字体
        try:
            self.font = pygame.font.Font(FONT_PATH, 28)
            self.small_font = pygame.font.Font(FONT_PATH, 20)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 28)
            self.small_font = pygame.font.SysFont('simhei', 20)

        # 玩家属性
        self.player_hp = player_hp
        self.player_max_hp = player_max_hp
        self.player_atk = player_atk
        self.player_name = "孙悟空"
        self.ultimate_unlocked = ultimate_unlocked

        # 怪物属性
        self.monster_name = monster_name
        self.monster_hp = monster_hp
        self.monster_max_hp = monster_max_hp
        self.monster_atk = monster_atk

        # 加载动画
        self.player_frames = load_swk2_frames(IMG_PATH, colorkey=(0, 0, 0))
        self.monster_frames = load_cattle_frames(IMG_PATH, 'fight', colorkey=(0, 0, 0))
        self.magic_appear = load_magic_frames(IMG_PATH, 'appear', colorkey=(0, 0, 0))
        self.magic_disappear = load_magic_frames(IMG_PATH, 'disappear', colorkey=(0, 0, 0))
        self.die_frames = load_cattle_die_frames(IMG_PATH, colorkey=(0, 0, 0))

        # 战斗精灵尺寸（放大两倍）
        player_size = (160, 160)  # 原80x80，放大两倍
        monster_size = (600, 600) if is_boss else (300, 300)  # BOSS为普通怪物的两倍，普通怪物放大1.5倍
        self.is_boss = is_boss
        self.player_frames = [pygame.transform.scale(f, player_size)
                              for f in self.player_frames[:16]]
        monster_dir0 = self.monster_frames.get(0, [])
        self.monster_frames_scaled = [pygame.transform.scale(f, monster_size)
                                      for f in monster_dir0]
        
        # 死亡动画帧
        self.die_frames_scaled = [pygame.transform.scale(f, monster_size)
                                  for f in self.die_frames]

        # 大招特效帧：放大2倍
        effect_normal_size = (150, 150)
        effect_ultimate_size = (300, 300)
        self.magic_appear_normal = [pygame.transform.scale(f, effect_normal_size)
                                    for f in self.magic_appear]
        self.magic_disappear_normal = [pygame.transform.scale(f, effect_normal_size)
                                       for f in self.magic_disappear]
        self.magic_appear_ultimate = [pygame.transform.scale(f, effect_ultimate_size)
                                      for f in self.magic_appear]
        self.magic_disappear_ultimate = [pygame.transform.scale(f, effect_ultimate_size)
                                         for f in self.magic_disappear]

        # 动画对象（默认显示第一帧，不播放）
        self.player_anim = Animation(self.player_frames, 4) if self.player_frames else None
        self.monster_anim = Animation(self.monster_frames_scaled, 6) if self.monster_frames_scaled else None
        self.die_anim = Animation(self.die_frames_scaled, 4) if self.die_frames_scaled else None
        self.player_playing = False   # 是否正在播放动画
        self.monster_playing = False
        self.die_playing = False

        # 战斗背景音乐
        self._play_battle_bgm()

        # 加载音效
        self.normal_atk_sound = None
        self.skill_sound = None
        self.ultimate_sound = None
        try:
            full_sound = pygame.mixer.Sound(SOUND_SWK)
            raw = full_sound.get_raw()
            full_len = len(raw)

            self.normal_atk_sound = pygame.mixer.Sound(buffer=raw[:full_len // 4])
            self.normal_atk_sound.set_volume(0.7)

            self.skill_sound = pygame.mixer.Sound(buffer=raw[:full_len // 2])
            self.skill_sound.set_volume(0.7)

            self.ultimate_sound = full_sound
            self.ultimate_sound.set_volume(0.7)
        except Exception:
            pass

        # 战斗状态
        self.intro_text = intro_text
        if intro_text:
            self.state = self.STATE_INTRO
            self.message = intro_text
        else:
            self.state = self.STATE_READY
            self.message = "请选择行动！"
        self.state_timer = 0
        self.done = False
        self.win = False
        self.avoided = False  # 是否避战退出

        # 当前攻击类型
        self.current_atk_type = "normal"

        # 特效
        self.effect_frames = None
        self.effect_anim = None
        self.effect_x = 0
        self.effect_y = 0

        # 战斗区域大边框
        if is_boss:
            # BOSS战：战斗区域扩大，怪物在右半部分
            self.battle_area = pygame.Rect(10, 50, 780, 520)
            self.player_pos = (180, 350)   # 玩家在左半部分
            self.monster_pos = (550, 200)  # BOSS在右半部分
        else:
            # 普通战斗
            self.battle_area = pygame.Rect(20, 70, 760, 400)
            self.player_pos = (200, 300)   # 玩家在左半部分中心
            self.monster_pos = (600, 300)  # 怪物在右半部分中心
        
        # 保存怪物高度，用于计算特效位置
        self.monster_height = monster_size[1]

    def _play_battle_bgm(self):
        """播放战斗背景音乐"""
        try:
            pygame.mixer.music.load(BGM_TEMPLE)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"战斗音乐加载失败: {e}")

    def _play_normal_atk_sound(self):
        """播放普攻音效（1/4）"""
        if self.normal_atk_sound:
            self.normal_atk_sound.play()

    def _play_skill_sound(self):
        """播放技能音效（1/2）"""
        if self.skill_sound:
            self.skill_sound.play()

    def _play_ultimate_sound(self):
        """播放大招音效（全部）"""
        if self.ultimate_sound:
            self.ultimate_sound.play()

    def _draw_character_at_position(self, surface, pos, anim, is_hurt=False, hurt_timer=0):
        """在指定位置绘制角色动画"""
        if anim:
            img = anim.get_current_frame()
            if img:
                if is_hurt and hurt_timer % 4 < 2:
                    return
                img_rect = img.get_rect(center=pos)
                surface.blit(img, img_rect)

    def _draw_hp_bar(self, surface, x, y, current, maximum):
        bar_w = 150
        bar_h = 15
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h))
        ratio = max(0, current / maximum)
        fill_w = int(bar_w * ratio)
        if ratio > 0.5:
            bar_color = GREEN
        elif ratio > 0.25:
            bar_color = YELLOW
        else:
            bar_color = RED
        pygame.draw.rect(surface, bar_color, (x, y, fill_w, bar_h))
        pygame.draw.rect(surface, WHITE, (x, y, bar_w, bar_h), 2)
        hp_text = self.small_font.render(f"{current}/{maximum}", True, WHITE)
        surface.blit(hp_text, (x + bar_w + 5, y - 3))

    def handle_event(self, event):
        # 开场喊话
        if self.state == self.STATE_INTRO:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.state = self.STATE_READY
                self.state_timer = 0
                self.message = "请选择行动！"
            return

        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_READY:
                if event.key == pygame.K_1:
                    self._player_attack("normal")
                elif event.key == pygame.K_2:
                    self._player_attack("skill")
                elif event.key == pygame.K_3 and self.ultimate_unlocked:
                    self._player_attack("ultimate")
                elif event.key == pygame.K_4:
                    self._avoid_battle()
            elif self.state in (self.STATE_WIN, self.STATE_LOSE):
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.done = True

        if event.type == pygame.MOUSEBUTTONDOWN and self.state == self.STATE_READY:
            mx, my = event.pos
            if 50 <= mx <= 170 and 500 <= my <= 550:
                self._player_attack("normal")
            elif 200 <= mx <= 320 and 500 <= my <= 550:
                self._player_attack("skill")
            elif self.ultimate_unlocked and 350 <= mx <= 470 and 500 <= my <= 550:
                self._player_attack("ultimate")
            elif 500 <= mx <= 620 and 500 <= my <= 550:
                self._avoid_battle()

    def _player_attack(self, atk_type="normal"):
        self.state = self.STATE_PLAYER_ATK
        self.state_timer = 0
        self.current_atk_type = atk_type

        # 播放攻击音效
        if atk_type == "normal":
            self._play_normal_atk_sound()
        elif atk_type == "skill":
            self._play_skill_sound()
        elif atk_type == "ultimate":
            self._play_ultimate_sound()

        # 播放玩家动画
        self.player_playing = True
        if self.player_anim:
            self.player_anim.reset()

        # 特效位置：怪物模型底部
        eff_cx = self.monster_pos[0]
        eff_bottom = self.monster_pos[1] + self.monster_height // 2

        if atk_type == "normal":
            damage = self.player_atk
            self.message = "孙悟空发起普通攻击！"
            self.effect_frames = self.magic_disappear_normal
            eff_size = 150

        elif atk_type == "skill":
            damage = self.player_atk + 35
            self.message = "孙悟空使用了「如意金箍棒」！"
            self.effect_frames = self.magic_appear_normal
            eff_size = 150

        elif atk_type == "ultimate":
            damage = self.player_atk + 75
            self.message = "孙悟空发动大招「七十二变」！！"
            self.effect_frames = self.magic_appear_ultimate + self.magic_disappear_ultimate
            eff_size = 250

        # 特效居中于怪物底部
        self.effect_x = eff_cx - eff_size // 2
        self.effect_y = eff_bottom - eff_size

        self.monster_hp = max(0, self.monster_hp - damage)

        if self.effect_frames:
            self.effect_anim = Animation(self.effect_frames, 2)

    def _monster_attack(self):
        self.state = self.STATE_MONSTER_ATK
        self.state_timer = 0
        self.player_hp = max(0, self.player_hp - self.monster_atk)
        self.message = f"{self.monster_name}发起攻击！"
        # 播放怪物动画
        self.monster_playing = True
        if self.monster_anim:
            self.monster_anim.reset()

    def _avoid_battle(self):
        """避战：退出战斗但扣20血量"""
        self.player_hp = max(1, self.player_hp - 20)
        self.avoided = True
        self.done = True
        self.message = "孙悟空选择避战，损失20点生命值！"

    def update(self):
        if self.done:
            return

        self.state_timer += 1

        if self.state == self.STATE_INTRO:
            if self.state_timer >= 90:
                self.state = self.STATE_READY
                self.state_timer = 0
                self.message = "请选择行动！"
            return

        if self.state == self.STATE_PLAYER_ATK:
            if self.effect_anim:
                self.effect_anim.update()
            atk_duration = 80 if self.current_atk_type == "ultimate" else 60
            if self.state_timer >= atk_duration:
                self.player_playing = False
                if self.monster_hp <= 0:
                    # 播放怪物死亡动画
                    self.state = self.STATE_MONSTER_DIE
                    self.state_timer = 0
                    self.message = f"{self.monster_name}被击败了！"
                    self.die_playing = True
                    if self.die_anim:
                        self.die_anim.reset()
                else:
                    self.state = self.STATE_MONSTER_HURT
                    self.state_timer = 0
                    self.message = f"{self.monster_name}受到了伤害！"

        elif self.state == self.STATE_MONSTER_DIE:
            # 更新死亡动画
            if self.die_anim and self.die_playing:
                self.die_anim.update()
            # 死亡动画播放完毕后显示胜利
            if self.state_timer >= 42:  # 约1.4秒
                self.die_playing = False
                self.state = self.STATE_WIN
                self.message = "战斗胜利！按空格键继续"
                self.win = True

        elif self.state == self.STATE_MONSTER_HURT:
            if self.state_timer >= 30:
                self._monster_attack()

        elif self.state == self.STATE_MONSTER_ATK:
            if self.state_timer >= 40:
                self.monster_playing = False
                if self.player_hp <= 0:
                    self.state = self.STATE_LOSE
                    self.message = "战斗失败...按空格键继续"
                else:
                    self.state = self.STATE_PLAYER_HURT
                    self.state_timer = 0
                    self.message = "孙悟空受到了伤害！"

        elif self.state == self.STATE_PLAYER_HURT:
            if self.state_timer >= 30:
                self.state = self.STATE_READY
                self.message = "请选择行动！"

        # 只在攻击时播放动画，平时静止
        if self.player_anim and self.player_playing:
            self.player_anim.update()
        if self.monster_anim and self.monster_playing:
            self.monster_anim.update()

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        # 绘制战斗区域大边框
        pygame.draw.rect(screen, (180, 160, 100), self.battle_area, 3)
        # 半透明背景
        battle_bg = pygame.Surface((self.battle_area.w, self.battle_area.h), pygame.SRCALPHA)
        battle_bg.fill((20, 20, 40, 100))
        screen.blit(battle_bg, self.battle_area.topleft)

        # 绘制角色动画
        player_hurt = (self.state == self.STATE_PLAYER_HURT)
        monster_hurt = (self.state == self.STATE_MONSTER_HURT)
        self._draw_character_at_position(screen, self.player_pos,
                                        self.player_anim, player_hurt, self.state_timer)
        
        # 怪物死亡动画或正常动画
        if self.state == self.STATE_MONSTER_DIE and self.die_playing:
            self._draw_character_at_position(screen, self.monster_pos,
                                            self.die_anim, False, 0)
        else:
            self._draw_character_at_position(screen, self.monster_pos,
                                            self.monster_anim, monster_hurt, self.state_timer)

        # 特效
        if self.effect_anim and self.state == self.STATE_PLAYER_ATK:
            effect_img = self.effect_anim.get_current_frame()
            if effect_img:
                effect_img = effect_img.convert()
                effect_img.set_colorkey((0, 0, 0))
                screen.blit(effect_img, (self.effect_x, self.effect_y))

        # 血条
        self._draw_hp_bar(screen, 50, 40, self.player_hp, self.player_max_hp)
        self._draw_hp_bar(screen, 450, 40, self.monster_hp, self.monster_max_hp)

        # 名字
        name1 = self.font.render(self.player_name, True, WHITE)
        screen.blit(name1, (50, 10))
        if self.is_boss:
            name2 = self.font.render(f"BOSS - {self.monster_name}", True, RED)
        else:
            name2 = self.font.render(self.monster_name, True, WHITE)
        screen.blit(name2, (450, 10))

        # 消息
        if self.state == self.STATE_INTRO:
            intro_surface = self.font.render(self.message, True, YELLOW)
            intro_x = SCREEN_WIDTH // 2 - intro_surface.get_width() // 2
            intro_y = SCREEN_HEIGHT // 2 - 20
            bg_bar = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
            bg_bar.fill((0, 0, 0, 180))
            screen.blit(bg_bar, (0, intro_y - 10))
            screen.blit(intro_surface, (intro_x, intro_y))
            hint = self.small_font.render("按任意键开始战斗", True, WHITE)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, intro_y + 40))
        else:
            msg_surface = self.font.render(self.message, True, WHITE)
            screen.blit(msg_surface, (50, 450))

        # 按钮（文字版本）
        if self.state == self.STATE_READY:
            # 普攻按钮
            pygame.draw.rect(screen, GREEN, (50, 500, 120, 50))
            btn_text = self.font.render("普攻", True, BLACK)
            screen.blit(btn_text, (85, 510))

            # 技能按钮
            pygame.draw.rect(screen, YELLOW, (200, 500, 120, 50))
            btn_text = self.font.render("金箍棒", True, BLACK)
            screen.blit(btn_text, (215, 510))

            # 大招按钮
            if self.ultimate_unlocked:
                pygame.draw.rect(screen, PURPLE, (350, 500, 120, 50))
                btn_text = self.font.render("七十二变", True, WHITE)
                screen.blit(btn_text, (365, 510))

            # 避战按钮
            pygame.draw.rect(screen, (150, 80, 80), (500, 500, 120, 50))
            btn_text = self.font.render("避战", True, WHITE)
            screen.blit(btn_text, (535, 510))

        # 胜利/失败画面
        if self.state == self.STATE_WIN:
            try:
                win_img = pygame.image.load(WIN_IMG).convert()
                win_img = pygame.transform.scale(win_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                win_img.set_alpha(180)
                screen.blit(win_img, (0, 0))
            except Exception:
                pass
            win_text = self.font.render("战斗胜利！", True, YELLOW)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20))

        elif self.state == self.STATE_LOSE:
            try:
                fail_img = pygame.image.load(FAIL_IMG).convert()
                fail_img = pygame.transform.scale(fail_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                fail_img.set_alpha(180)
                screen.blit(fail_img, (0, 0))
            except Exception:
                pass
            lose_text = self.font.render("战斗失败...", True, RED)
            screen.blit(lose_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20))

    def is_done(self):
        return self.done

    def is_win(self):
        return self.win

    def is_avoided(self):
        return self.avoided
