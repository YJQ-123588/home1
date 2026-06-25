import pygame
import sys
from config.settings import *
from scenes.start_scene import StartScene
from scenes.village_scene import VillageScene
from scenes.temple_scene import TempleScene


class Game:
    """游戏主控类"""

    STATE_START = -1
    STATE_VILLAGE = 0
    STATE_TEMPLE = 1
    STATE_END = 2

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = self.STATE_START
        self.start_scene = None
        self.village_scene = None
        self.temple_scene = None

        # 玩家全局状态
        self.player_hp = PLAYER_BASE_HP
        self.player_max_hp = PLAYER_BASE_HP
        self.player_atk = PLAYER_BASE_ATK
        self.ultimate_unlocked = False
        self.rescued = False  # 是否被土地公救过

        try:
            self.font = pygame.font.Font(FONT_PATH, 36)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 36)

    def run(self):
        self.start_scene = StartScene()

        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()

        pygame.quit()
        sys.exit()

    def _init_village(self):
        """初始化村庄场景"""
        self.village_scene = VillageScene(
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            ultimate_unlocked=self.ultimate_unlocked,
            rescued=self.rescued
        )
        self.state = self.STATE_VILLAGE

        # 战败救援：显示土地公对话（只触发一次）
        if self.rescued and self.village_scene.god:
            self.village_scene.god.rescued = True
            self.village_scene.god_talked = True
            self.village_scene.dialog.show(self.village_scene.god.rescue_talk())
            self.village_scene._stop_npc_for_dialog(self.village_scene.god)

    def _init_temple(self):
        """初始化寺庙场景"""
        self.temple_scene = TempleScene(
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            player_atk=self.player_atk,
            ultimate_unlocked=self.ultimate_unlocked
        )
        self.state = self.STATE_TEMPLE

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == self.STATE_START:
                        self.running = False
                        return
                    elif self.state == self.STATE_VILLAGE:
                        self.running = False
                        return
                    elif self.state == self.STATE_END:
                        self.running = False
                        return
                    elif self.state == self.STATE_TEMPLE:
                        # 寺庙场景由场景自己处理ESC
                        pass

            if self.state == self.STATE_START and self.start_scene:
                result = self.start_scene.handle_event(event)
                if result == "start":
                    self._init_village()
                elif result == "quit":
                    self.running = False
                    return

            elif self.state == self.STATE_VILLAGE and self.village_scene:
                self.village_scene.handle_event(event)
            elif self.state == self.STATE_TEMPLE and self.temple_scene:
                self.temple_scene.handle_event(event)

    def _update(self):
        if self.state == self.STATE_START:
            return

        if self.state == self.STATE_VILLAGE and self.village_scene:
            self.village_scene.update()

            # 同步玩家状态
            self._sync_player_state_from_village()

            if self.village_scene.is_done():
                self._init_temple()

        elif self.state == self.STATE_TEMPLE and self.temple_scene:
            self.temple_scene.update()

            if self.temple_scene.is_done():
                if self.temple_scene.exited:
                    # ESC退出 → 返回村庄
                    pygame.mixer.music.stop()
                    self._init_village()
                else:
                    # 通关
                    self.state = self.STATE_END

            elif self.temple_scene.is_player_lost():
                # 战败 → 土地公救援 → 回村庄
                self.rescued = True
                self.player_hp = PLAYER_BASE_HP
                pygame.mixer.music.stop()
                self._init_village()

    def _sync_player_state_from_village(self):
        """从村庄场景同步玩家状态"""
        if self.village_scene and self.village_scene.player:
            self.player_hp = self.village_scene.player.hp
            self.player_max_hp = self.village_scene.player.max_hp
            self.ultimate_unlocked = self.village_scene.ultimate_unlocked

    def _draw(self):
        self.screen.fill((0, 0, 0))

        if self.state == self.STATE_START and self.start_scene:
            self.start_scene.draw(self.screen)

        elif self.state == self.STATE_VILLAGE and self.village_scene:
            self.village_scene.draw(self.screen)

        elif self.state == self.STATE_TEMPLE and self.temple_scene:
            self.temple_scene.draw(self.screen)

        elif self.state == self.STATE_END:
            self._draw_end_screen()

        pygame.display.update()

    def _draw_end_screen(self):
        try:
            win_img = pygame.image.load(WIN_IMG).convert()
            win_img = pygame.transform.scale(win_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(win_img, (0, 0))
        except Exception:
            pass

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        texts = [
            "恭喜通关！",
            "孙悟空成功降服了观音院的妖怪！",
            "",
            "按 ESC 退出"
        ]
        for i, text in enumerate(texts):
            if text:
                color = (255, 215, 0) if i == 0 else (255, 255, 255)
                text_surface = self.font.render(text, True, color)
                x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
                y = 200 + i * 50
                self.screen.blit(text_surface, (x, y))
