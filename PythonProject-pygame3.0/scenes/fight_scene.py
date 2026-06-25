import pygame
import os
from config.settings import *
from core.animation import Animation, load_swk2_frames, load_cattle_frames, load_magic_frames


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

    def __init__(self, monster_name="牛妖", monster_hp=100, monster_atk=15,
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
        self.monster_max_hp = monster_hp
        self.monster_atk = monster_atk

        # 加载动画
        self.player_frames = load_swk2_frames(IMG_PATH, colorkey=(0, 0, 0))
        self.monster_frames = load_cattle_frames(IMG_PATH, 'fight', colorkey=(0, 0, 0))
        self.magic_appear = load_magic_frames(IMG_PATH, 'appear', colorkey=(0, 0, 0))
        self.magic_disappear = load_magic_frames(IMG_PATH, 'disappear', colorkey=(0, 0, 0))

        # 战斗精灵尺寸（玩家与NPC一致）
        player_size = (80, 80)
        monster_size = (400, 400) if is_boss else (100, 100)
        self.is_boss = is_boss
        self.player_frames = [pygame.transform.scale(f, player_size)
                              for f in self.player_frames[:16]]
        monster_dir0 = self.monster_frames.get(0, [])
        self.monster_frames_scaled = [pygame.transform.scale(f, monster_size)
                                      for f in monster_dir0]

        # 大招特效帧：放大2倍
        effect_normal_size = (100, 100)
        effect_ultimate_size = (200, 200)
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
        self.player_playing = False   # 是否正在播放动画
        self.monster_playing = False

        # 按钮
        self.btn_atk = None
        self.btn_skill = None
        self._load_buttons()

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

        # 当前攻击类型
        self.current_atk_type = "normal"

        # 特效
        self.effect_frames = None
        self.effect_anim = None
        self.effect_x = 0
        self.effect_y = 0

        # 角色面板
        self.player_panel = pygame.Rect(100, 200, 120, 160)
        if is_boss:
            self.monster_panel = pygame.Rect(350, 60, 380, 380)
        else:
            self.monster_panel = pygame.Rect(480, 200, 160, 200)

    def _load_buttons(self):
        try:
            self.btn_atk = pygame.image.load(
                os.path.join(IMG_PATH, "button", "ok.png")).convert_alpha()
            self.btn_atk = pygame.transform.scale(self.btn_atk, (120, 50))
        except Exception:
            self.btn_atk = None

        try:
            self.btn_skill = pygame.image.load(
                os.path.join(IMG_PATH, "button", "temple_button.png")).convert_alpha()
            self.btn_skill = pygame.transform.scale(self.btn_skill, (120, 50))
        except Exception:
            self.btn_skill = None

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

    def _draw_character_panel(self, surface, panel_rect, anim, is_hurt=False, hurt_timer=0):
        panel_surface = pygame.Surface((panel_rect.w, panel_rect.h), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 40, 150))
        surface.blit(panel_surface, panel_rect.topleft)
        pygame.draw.rect(surface, (180, 160, 100), panel_rect, 2)
        if anim:
            img = anim.get_current_frame()
            if img:
                if is_hurt and hurt_timer % 4 < 2:
                    return
                img_rect = img.get_rect(center=panel_rect.center)
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
        mc = self.monster_panel
        eff_cx = mc.centerx
        eff_bottom = mc.bottom

        if atk_type == "normal":
            damage = self.player_atk
            self.message = "孙悟空发起普通攻击！"
            self.effect_frames = self.magic_disappear_normal
            eff_size = 100

        elif atk_type == "skill":
            damage = self.player_atk + 15
            self.message = "孙悟空使用了「如意金箍棒」！"
            self.effect_frames = self.magic_appear_normal
            eff_size = 100

        elif atk_type == "ultimate":
            damage = self.player_atk + 45
            self.message = "孙悟空发动大招「七十二变」！！"
            self.effect_frames = self.magic_appear_ultimate + self.magic_disappear_ultimate
            eff_size = 200

        # 特效居中于怪物模型底部
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
                    self.state = self.STATE_WIN
                    self.message = "战斗胜利！按空格键继续"
                    self.win = True
                else:
                    self.state = self.STATE_MONSTER_HURT
                    self.state_timer = 0
                    self.message = f"{self.monster_name}受到了伤害！"

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

        # 角色面板
        player_hurt = (self.state == self.STATE_PLAYER_HURT)
        monster_hurt = (self.state == self.STATE_MONSTER_HURT)
        self._draw_character_panel(screen, self.player_panel,
                                   self.player_anim, player_hurt, self.state_timer)
        self._draw_character_panel(screen, self.monster_panel,
                                   self.monster_anim, monster_hurt, self.state_timer)

        # 特效
        if self.effect_anim and self.state == self.STATE_PLAYER_ATK:
            effect_img = self.effect_anim.get_current_frame()
            if effect_img:
                effect_img = effect_img.convert()
                effect_img.set_colorkey((0, 0, 0))
                screen.blit(effect_img, (self.effect_x, self.effect_y))

        # 血条
        self._draw_hp_bar(screen, 50, 140, self.player_hp, self.player_max_hp)
        self._draw_hp_bar(screen, 450, 140, self.monster_hp, self.monster_max_hp)

        # 名字
        name1 = self.font.render(self.player_name, True, WHITE)
        screen.blit(name1, (50, 110))
        if self.is_boss:
            name2 = self.font.render(f"BOSS - {self.monster_name}", True, RED)
        else:
            name2 = self.font.render(self.monster_name, True, WHITE)
        screen.blit(name2, (450, 110))

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

        # 按钮
        if self.state == self.STATE_READY:
            if self.btn_atk:
                screen.blit(self.btn_atk, (50, 500))
            else:
                pygame.draw.rect(screen, GREEN, (50, 500, 120, 50))
                btn_text = self.small_font.render("1.攻击", True, BLACK)
                screen.blit(btn_text, (60, 510))

            if self.btn_skill:
                screen.blit(self.btn_skill, (200, 500))
            else:
                pygame.draw.rect(screen, YELLOW, (200, 500, 120, 50))
                btn_text = self.small_font.render("2.技能", True, BLACK)
                screen.blit(btn_text, (210, 510))

            if self.ultimate_unlocked:
                pygame.draw.rect(screen, PURPLE, (350, 500, 120, 50))
                btn_text = self.small_font.render("3.大招", True, WHITE)
                screen.blit(btn_text, (360, 510))

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
