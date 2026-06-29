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

        # 寺庙怪物状态持久化
        self.temple_defeated = set()
        self.temple_boss_appeared = False
        self.temple_monster_hp = {}

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
        # 恢复持久化的怪物状态
        self.temple_scene.defeated_monsters = set(self.temple_defeated)
        self.temple_scene.boss_appeared = self.temple_boss_appeared
        if self.temple_boss_appeared and self.temple_scene.boss:
            self.temple_scene.boss.visible = True
        for cattle in self.temple_scene.cattle_list:
            if cattle.name in self.temple_monster_hp:
                data = self.temple_monster_hp[cattle.name]
                cattle.hp = data["hp"]
                cattle.max_hp = data.get("max_hp", cattle.hp)
                cattle.alive = data["alive"]
                if not cattle.alive:
                    cattle.visible = False
        self.state = self.STATE_TEMPLE

    def get_game_state(self):
        # 如果在菜单中，保存实际游戏场景
        actual_state = self.state
        if self.state == self.STATE_START and hasattr(self, '_state_before_menu'):
            actual_state = self._state_before_menu

        state = {
            "current_state": actual_state,
            "player_hp": self.player_hp,
            "player_max_hp": self.player_max_hp,
            "player_atk": self.player_atk,
            "ultimate_unlocked": self.ultimate_unlocked,
            "rescued": self.rescued,
        }
        if actual_state == self.STATE_VILLAGE and self.village_scene:
            state["player_x"] = self.village_scene.player.map_x
            state["player_y"] = self.village_scene.player.map_y
            state["god_talked"] = self.village_scene.god_talked
            if self.village_scene.god:
                state["god_rescued"] = self.village_scene.god.rescued
            elder_states = []
            for elder in self.village_scene.elders:
                elder_states.append({
                    "elder_id": elder.elder_id,
                    "upgrade_given": elder.upgrade_given,
                })
            state["elder_states"] = elder_states
            farmer_states = []
            for farmer in self.village_scene.farmers:
                farmer_states.append({
                    "farmer_id": farmer.farmer_id,
                    "dialog_index": farmer.dialog_index,
                })
            state["farmer_states"] = farmer_states
        # 始终保存寺庙怪物状态
        if actual_state == self.STATE_TEMPLE and self.temple_scene:
            state["player_x"] = self.temple_scene.player.map_x
            state["player_y"] = self.temple_scene.player.map_y
        if self.temple_defeated or self.temple_monster_hp:
            state["defeated_monsters"] = list(self.temple_defeated)
            state["boss_appeared"] = self.temple_boss_appeared
            state["monster_hp_list"] = [
                {"name": name, "hp": data["hp"], "max_hp": data["max_hp"], "alive": data["alive"]}
                for name, data in self.temple_monster_hp.items()
            ]
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
        # 恢复寺庙怪物状态（无论当前场景是什么）
        defeated = state.get("defeated_monsters", [])
        boss_appeared = state.get("boss_appeared", False)
        monster_hp_list = state.get("monster_hp_list", [])
        self.temple_defeated = set(defeated)
        self.temple_boss_appeared = boss_appeared
        self.temple_monster_hp = {
            m["name"]: {"hp": m["hp"], "max_hp": m.get("max_hp", m["hp"]), "alive": m["alive"]}
            for m in monster_hp_list
        }
        if current_state == self.STATE_VILLAGE:
            self._init_village_with_pos(player_x, player_y, state)
        elif current_state == self.STATE_TEMPLE:
            self._init_temple_with_pos(player_x, player_y)
        else:
            self._init_village_with_pos(player_x, player_y, state)

    def _init_village_with_pos(self, x=None, y=None, state=None):
        self._init_village()
        if self.village_scene:
            if x is not None and y is not None:
                self.village_scene.player.map_x = x
                self.village_scene.player.map_y = y
                self.village_scene.player.rect.center = (int(x), int(y))
            if state:
                self.village_scene.god_talked = state.get("god_talked", False)
                if self.village_scene.god:
                    self.village_scene.god.rescued = state.get("god_rescued", False)
                elder_states = state.get("elder_states", [])
                for es in elder_states:
                    for elder in self.village_scene.elders:
                        if elder.elder_id == es.get("elder_id"):
                            elder.upgrade_given = es.get("upgrade_given", False)
                farmer_states = state.get("farmer_states", [])
                for fs in farmer_states:
                    for farmer in self.village_scene.farmers:
                        if farmer.farmer_id == fs.get("farmer_id"):
                            farmer.dialog_index = fs.get("dialog_index", 0)

    def _init_temple_with_pos(self, x=None, y=None):
        self._init_temple()
        if self.temple_scene and x is not None and y is not None:
            self.temple_scene.player.map_x = x
            self.temple_scene.player.map_y = y
            self.temple_scene.player.rect.center = (int(x), int(y))

    def _open_menu(self):
        """从游戏打开菜单（开始界面）"""
        pygame.mixer.music.stop()
        # 仅在寺庙场景时显示"返回村庄"按钮
        show_return = (self.state == self.STATE_TEMPLE)
        self._state_before_menu = self.state
        self.start_scene = StartScene(show_return_village=show_return)
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
                    self.state = getattr(self, '_state_before_menu', self.STATE_VILLAGE)
                elif result == "return_village":
                    pygame.mixer.music.stop()
                    self._init_village()
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
            # 同步玩家状态
            self.player_hp = self.temple_scene.player_hp
            self.player_max_hp = self.temple_scene.player_max_hp
            # 同步怪物状态
            self.temple_defeated = set(self.temple_scene.defeated_monsters)
            self.temple_boss_appeared = self.temple_scene.boss_appeared
            for cattle in self.temple_scene.cattle_list:
                self.temple_monster_hp[cattle.name] = {
                    "hp": cattle.hp,
                    "max_hp": cattle.max_hp,
                    "alive": cattle.alive,
                }
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
