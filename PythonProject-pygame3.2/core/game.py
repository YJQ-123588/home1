import pygame
import sys
from config.settings import *
from scenes.start_scene import StartScene
from scenes.village_scene import VillageScene
from scenes.temple_scene import TempleScene
from core.save_load import save_game, load_game


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

        self.player_hp = PLAYER_BASE_HP
        self.player_max_hp = PLAYER_BASE_HP
        self.player_atk = PLAYER_BASE_ATK
        self.ultimate_unlocked = False
        self.rescued = False

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
        self.village_scene = VillageScene(
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            ultimate_unlocked=self.ultimate_unlocked,
            rescued=self.rescued
        )
        self.state = self.STATE_VILLAGE
        if self.rescued and self.village_scene.god:
            self.village_scene.god.rescued = True
            self.village_scene.god_talked = True
            self.village_scene.dialog.show(self.village_scene.god.rescue_talk())
            self.village_scene._stop_npc_for_dialog(self.village_scene.god)

    def _init_temple(self):
        self.temple_scene = TempleScene(
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            player_atk=self.player_atk,
            ultimate_unlocked=self.ultimate_unlocked
        )
        self.state = self.STATE_TEMPLE

    def get_game_state(self):
        state = {
            "current_state": self.state,
            "player_hp": self.player_hp,
            "player_max_hp": self.player_max_hp,
            "player_atk": self.player_atk,
            "ultimate_unlocked": self.ultimate_unlocked,
            "rescued": self.rescued,
        }
        if self.state == self.STATE_VILLAGE and self.village_scene:
            state["player_x"] = self.village_scene.player.map_x
            state["player_y"] = self.village_scene.player.map_y
        elif self.state == self.STATE_TEMPLE and self.temple_scene:
            state["player_x"] = self.temple_scene.player.map_x
            state["player_y"] = self.temple_scene.player.map_y
            state["defeated_monsters"] = list(self.temple_scene.defeated_monsters)
            state["boss_appeared"] = self.temple_scene.boss_appeared
        return state

    def load_game_state(self, save_data):
        state = save_data.get("state", {})
        self.player_hp = state.get("player_hp", PLAYER_BASE_HP)
        self.player_max_hp = state.get("player_max_hp", PLAYER_BASE_HP)
        self.player_atk = state.get("player_atk", PLAYER_BASE_ATK)
        self.ultimate_unlocked = state.get("ultimate_unlocked", False)
        self.rescued = state.get("rescued", False)
        current_state = state.get("current_state", self.STATE_VILLAGE)
        player_x = state.get("player_x")
        player_y = state.get("player_y")
        if current_state == self.STATE_VILLAGE:
            self._init_village_with_pos(player_x, player_y)
        elif current_state == self.STATE_TEMPLE:
            defeated = state.get("defeated_monsters", [])
            boss_appeared = state.get("boss_appeared", False)
            self._init_temple_with_pos(player_x, player_y, defeated, boss_appeared)
        else:
            self._init_village_with_pos(player_x, player_y)

    def _init_village_with_pos(self, x=None, y=None):
        self._init_village()
        if self.village_scene and x is not None and y is not None:
            self.village_scene.player.map_x = x
            self.village_scene.player.map_y = y
            self.village_scene.player.rect.center = (int(x), int(y))

    def _init_temple_with_pos(self, x=None, y=None, defeated=None, boss_appeared=False):
        self._init_temple()
        if self.temple_scene:
            if x is not None and y is not None:
                self.temple_scene.player.map_x = x
                self.temple_scene.player.map_y = y
                self.temple_scene.player.rect.center = (int(x), int(y))
            if defeated:
                self.temple_scene.defeated_monsters = set(defeated)
            if boss_appeared and self.temple_scene.boss:
                self.temple_scene.boss_appeared = True
                self.temple_scene.boss.visible = True

    def _open_menu(self):
        """从游戏打开菜单（开始界面）"""
        pygame.mixer.music.stop()
        self.start_scene = StartScene()
        self.start_scene.can_continue = True
        self.state = self.STATE_START

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # 开始界面
            if self.state == self.STATE_START and self.start_scene:
                result = self.start_scene.handle_event(event)
                if result == "start":
                    self._init_village()
                elif result == "continue":
                    pass  # 保持当前场景，回到游戏
                elif result == "quit":
                    self.running = False
                    return
                elif isinstance(result, dict):
                    if result.get("action") == "load":
                        save_data = load_game(result["slot"])
                        if save_data:
                            self.load_game_state(save_data)
                    elif result.get("action") == "save":
                        game_state = self.get_game_state()
                        if save_game(result["slot"], game_state):
                            self.start_scene.save_msg = f"存档成功（档位{result['slot']}）"
                        else:
                            self.start_scene.save_msg = "存档失败"
                        self.start_scene.save_msg_timer = 120
                continue

            # 村庄场景
            elif self.state == self.STATE_VILLAGE and self.village_scene:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._open_menu()
                    continue
                self.village_scene.handle_event(event)

            # 寺庙场景
            elif self.state == self.STATE_TEMPLE and self.temple_scene:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._open_menu()
                    continue
                self.temple_scene.handle_event(event)

            # 通关界面
            elif self.state == self.STATE_END:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

    def _update(self):
        if self.state == self.STATE_START:
            return
        if self.state == self.STATE_VILLAGE and self.village_scene:
            self.village_scene.update()
            self._sync_player_state_from_village()
            if self.village_scene.is_done():
                self._init_temple()
        elif self.state == self.STATE_TEMPLE and self.temple_scene:
            self.temple_scene.update()
            if self.temple_scene.is_done():
                if self.temple_scene.exited:
                    pygame.mixer.music.stop()
                    self._init_village()
                else:
                    self.state = self.STATE_END
            elif self.temple_scene.is_player_lost():
                self.rescued = True
                self.player_hp = PLAYER_BASE_HP
                pygame.mixer.music.stop()
                self._init_village()

    def _sync_player_state_from_village(self):
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
        texts = ["恭喜通关！", "孙悟空成功降服了观音院的妖怪！", "", "按 ESC 退出"]
        for i, text in enumerate(texts):
            if text:
                color = (255, 215, 0) if i == 0 else (255, 255, 255)
                text_surface = self.font.render(text, True, color)
                x = SCREEN_WIDTH // 2 - text_surface.get_width() // 2
                y = 200 + i * 50
                self.screen.blit(text_surface, (x, y))
