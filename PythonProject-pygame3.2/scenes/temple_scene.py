import pygame
from config.settings import *
from core.tiled_map import TiledMap
from characters.player import Player
from characters.npc import Cattle
from ui.dialog import Dialog
from ui.fade_scene import FadeScene
from ui.avoid_battle_dialog import AvoidBattleDialog
from ui.confirm_dialog import ConfirmDialog
from scenes.fight_scene import FightScene


class TempleScene:
    """寺庙场景"""

    def __init__(self, player_hp=PLAYER_BASE_HP, player_max_hp=PLAYER_BASE_HP,
                 player_atk=PLAYER_BASE_ATK, ultimate_unlocked=False):
        self.tmx_map = TiledMap(TEMPLE_TMX)
        self.map_surface = self.tmx_map.get_surface()
        self.map_width = self.map_surface.get_width()
        self.map_height = self.map_surface.get_height()

        self.fade = FadeScene(self.map_surface)
        self.fade.set_status(SCENE_IN)

        actor_pos = self.tmx_map.get_all_named_objects('actor')
        monster_pos = self.tmx_map.get_all_named_objects('monster')

        # 障碍物碰撞区域
        self.obstacle_rects = self.tmx_map.get_obstacle_rects()

        sun_x, sun_y = actor_pos.get('sun', (686, 1100))
        self.player = Player(IMG_PATH, sun_x, sun_y)
        self.player_hp = player_hp
        self.player_max_hp = player_max_hp
        self.player_atk = player_atk
        self.ultimate_unlocked = ultimate_unlocked

        # 创建怪物（M4为BOSS，M1-M3为小怪）
        self.monsters = pygame.sprite.Group()
        self.cattle_list = []
        self.minions = []  # 小怪列表
        self.boss = None   # BOSS
        for name, (mx, my) in monster_pos.items():
            is_boss = (name == "M4")
            boss_name = "牛魔王" if is_boss else name
            cattle = Cattle(IMG_PATH, int(mx), int(my), boss_name, is_boss=is_boss)
            self.cattle_list.append(cattle)
            self.monsters.add(cattle)
            if is_boss:
                self.boss = cattle
                cattle.visible = False  # BOSS初始不可见
            else:
                self.minions.append(cattle)
        self.boss_appeared = False  # BOSS是否已出现

        self.dialog = Dialog()
        self.avoid_dialog = AvoidBattleDialog()
        self.confirm_dialog = ConfirmDialog()
        self.camera_x = 0
        self.camera_y = 0

        # 状态
        self.scene_done = False
        self.exited = False
        self.player_lost = False
        self.fighting = False
        self.current_fight = None
        self.current_cattle = None
        self.defeated_monsters = set()
        self.avoid_cooldown = 0

        self._play_music()

    def _play_music(self):
        try:
            pygame.mixer.music.load(BGM_TEMPLE)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"音乐加载失败: {e}")

    def _update_camera(self):
        self.camera_x = self.player.map_x - SCREEN_WIDTH // 2
        self.camera_y = self.player.map_y - SCREEN_HEIGHT // 2
        self.camera_x = max(0, min(self.camera_x, self.map_width - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_height - SCREEN_HEIGHT))

    def _check_player_obstacle_collision(self):
        """检测玩家中心点是否在障碍物内"""
        px, py = int(self.player.map_x), int(self.player.map_y)
        for obs_rect in self.obstacle_rects:
            if obs_rect.collidepoint(px, py):
                return True
        return False

    def _move_player_with_collision(self):
        """带碰撞检测的玩家移动"""
        old_x = self.player.map_x
        old_y = self.player.map_y

        self.player.map_x += self.player.dx
        if self._check_player_obstacle_collision():
            self.player.map_x = old_x

        self.player.map_y += self.player.dy
        if self._check_player_obstacle_collision():
            self.player.map_y = old_y

        half_w = self.player.rect.width // 2
        half_h = self.player.rect.height // 2
        self.player.map_x = max(half_w, min(self.player.map_x, self.map_width - half_w))
        self.player.map_y = max(half_h, min(self.player.map_y, self.map_height - half_h))
        self.player.rect.center = (int(self.player.map_x), int(self.player.map_y))

    def _check_monster_collision(self):
        if self.dialog.visible or self.fighting or self.avoid_dialog.visible:
            return
        if self.avoid_cooldown > 0:
            return

        for cattle in self.cattle_list:
            if cattle.name in self.defeated_monsters:
                continue
            # BOSS未出现时不检测碰撞
            if cattle.is_boss and not self.boss_appeared:
                continue
            dist = ((self.player.map_x - cattle.map_x) ** 2 +
                    (self.player.map_y - cattle.map_y) ** 2) ** 0.5
            if dist < 60:
                cattle.paused = True
                cattle.face_toward(self.player.map_x, self.player.map_y)
                self.player.dx = 0
                self.player.dy = 0
                self.current_cattle = cattle
                self.avoid_dialog.show(cattle.name)
                break

    def _start_battle(self, cattle):
        """开始战斗"""
        self.fighting = True
        self.current_fight = FightScene(
            monster_name=cattle.name,
            monster_hp=cattle.hp,
            monster_atk=cattle.attack,
            is_boss=cattle.is_boss,
            intro_text=cattle.talk(),
            player_hp=self.player_hp,
            player_max_hp=self.player_max_hp,
            player_atk=self.player_atk,
            ultimate_unlocked=self.ultimate_unlocked
        )
        pygame.mixer.music.stop()

    def handle_event(self, event):
        # 退出确认对话框
        if self.confirm_dialog.visible:
            if self.confirm_dialog.handle_event(event):
                if self.confirm_dialog.choice == "yes":
                    self.exited = True
                    self.scene_done = True
                self.confirm_dialog.choice = None
            return

        if self.fighting and self.current_fight:
            self.current_fight.handle_event(event)
            return

        if self.avoid_dialog.visible:
            if self.avoid_dialog.handle_event(event):
                if self.avoid_dialog.choice == "fight":
                    if self.current_cattle:
                        self._start_battle(self.current_cattle)
                elif self.avoid_dialog.choice == "avoid":
                    self.player_hp = max(1, self.player_hp - self.avoid_dialog.cost_hp)
                    if self.current_cattle:
                        self.current_cattle.paused = False
                    self.current_cattle = None
                    self.avoid_cooldown = 60
                self.avoid_dialog.choice = None
            return

        if self.dialog.handle_event(event):
            return

        # ESC键退出战斗地图
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.confirm_dialog.show("确定要离开寺庙吗？")
                return

        if not self.dialog.visible and not self.avoid_dialog.visible:
            self.player.handle_event(event)

    def update(self):
        # 战斗中
        if self.fighting and self.current_fight:
            self.current_fight.update()
            if self.current_fight.is_done():
                if self.current_fight.is_win():
                    if self.current_cattle:
                        self.defeated_monsters.add(self.current_cattle.name)
                    self.player_hp = self.current_fight.player_hp
                else:
                    self.player_lost = True
                self.fighting = False
                self.current_fight = None
                self.current_cattle = None
                self._play_music()

                # 检查是否所有小怪都被击败，如果是则让BOSS出现
                if not self.boss_appeared:
                    all_minions_defeated = all(m.name in self.defeated_monsters for m in self.minions)
                    if all_minions_defeated and self.boss:
                        self.boss.visible = True
                        self.boss_appeared = True
                        print("所有小怪已被击败，牛魔王出现了！")

                # 检查是否击败所有怪物（包括BOSS）
                if len(self.defeated_monsters) >= len(self.cattle_list):
                    self.scene_done = True
            return

        if self.fade.get_out():
            self.scene_done = True
            return

        if self.avoid_cooldown > 0:
            self.avoid_cooldown -= 1

        if self.dialog.visible or self.avoid_dialog.visible or self.confirm_dialog.visible:
            self.player.dx = 0
            self.player.dy = 0
            self.player.keys_pressed.clear()

        self.player.update()
        self._move_player_with_collision()

        self.monsters.update()
        self._check_monster_collision()
        self._update_camera()

    def draw(self, screen):
        if self.fighting and self.current_fight:
            self.current_fight.draw(screen)
            return

        display_surface = self.fade.get_back_image(
            int(self.camera_x), int(self.camera_y))

        for cattle in self.cattle_list:
            if cattle.name not in self.defeated_monsters:
                # BOSS未出现时不绘制
                if cattle.is_boss and not self.boss_appeared:
                    continue
                cattle.draw(display_surface, int(self.camera_x), int(self.camera_y))

        self.player.draw(display_surface, int(self.camera_x), int(self.camera_y))
        screen.blit(display_surface, (0, 0))
        self.dialog.draw(screen)
        self.avoid_dialog.draw(screen)
        self.confirm_dialog.draw(screen)

    def is_done(self):
        return self.scene_done

    def is_player_lost(self):
        return self.player_lost
