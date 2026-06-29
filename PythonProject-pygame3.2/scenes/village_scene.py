import pygame
from config.settings import *
from core.tiled_map import TiledMap
from characters.player import Player
from characters.npc import God, Elder, Farmer
from ui.dialog import Dialog
from ui.fade_scene import FadeScene
from ui.confirm_dialog import ConfirmDialog


class VillageScene:
    """村庄场景"""

    def __init__(self, player_hp=PLAYER_BASE_HP, player_max_hp=PLAYER_BASE_HP,
                 ultimate_unlocked=False, rescued=False):
        # 加载地图
        self.tmx_map = TiledMap(VILLAGE_TMX)
        self.map_surface = self.tmx_map.get_surface()
        self.map_width = self.map_surface.get_width()
        self.map_height = self.map_surface.get_height()

        # 渐入渐出
        self.fade = FadeScene(self.map_surface)
        self.fade.set_status(SCENE_IN)

        # 获取对象位置
        actor_pos = self.tmx_map.get_all_named_objects('actor')
        god_pos = self.tmx_map.get_all_named_objects('god')
        elder_pos = self.tmx_map.get_all_named_objects('elder')
        child_pos = self.tmx_map.get_all_named_objects('child')

        # 障碍物碰撞区域
        self.obstacle_rects = self.tmx_map.get_obstacle_rects()

        # 创建玩家
        sun_x, sun_y = actor_pos.get('sun', (2706, 496))
        self.player = Player(IMG_PATH, sun_x, sun_y)
        self.player.hp = player_hp
        self.player.max_hp = player_max_hp

        # 创建NPC
        self.npcs = pygame.sprite.Group()
        self.talking_npc = None

        # 土地公
        if 'god' in god_pos:
            gx, gy = god_pos['god']
            self.god = God(IMG_PATH, gx, gy)
            self.god.rescued = rescued
            self.npcs.add(self.god)
        else:
            self.god = None

        # 长老（3个功能性长老：hp_boost, ultimate, heal）
        self.elders = []
        elder_map = {'elder1': 1, 'elder2': 2, 'elder3': 3}
        elder_count = 0
        for key, eid in elder_map.items():
            if key in elder_pos:
                ex, ey = elder_pos[key]
                elder_count += 1
                elder = Elder(IMG_PATH, int(ex), int(ey), eid)
                self.elders.append(elder)
                self.npcs.add(elder)

        # 农民（取前3个child位置）
        self.farmers = []
        child_names = list(child_pos.keys())[:3]
        for i, name in enumerate(child_names):
            fx, fy = child_pos[name]
            farmer = Farmer(IMG_PATH, int(fx), int(fy), i + 1)
            self.farmers.append(farmer)
            self.npcs.add(farmer)

        # 对话框
        self.dialog = Dialog()
        self.confirm_dialog = ConfirmDialog()

        # 视窗
        self.camera_x = 0
        self.camera_y = 0

        # 状态
        self.scene_done = False
        self.god_talked = False
        self.ultimate_unlocked = ultimate_unlocked

        # 音乐
        self._play_music()

    def _play_music(self):
        try:
            pygame.mixer.music.load(BGM_VILLAGE)
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

    def _stop_npc_for_dialog(self, npc):
        npc.paused = True
        npc.face_toward(self.player.map_x, self.player.map_y)
        npc.image = npc.anim.get_current_frame()
        self.talking_npc = npc
        self._last_talked_npc = npc

    def _resume_npc(self):
        if self.talking_npc:
            self.talking_npc.paused = False
            self.talking_npc = None

    def _check_npc_collision(self):
        if self.dialog.visible:
            return

        # 土地公
        if self.god and self.god.can_talk():
            dist = ((self.player.map_x - self.god.map_x) ** 2 +
                    (self.player.map_y - self.god.map_y) ** 2) ** 0.5
            if dist < 60:
                self.dialog.show(self.god.talk())
                self.player.dx = 0
                self.player.dy = 0
                self._stop_npc_for_dialog(self.god)
                if not self.god_talked:
                    self.god_talked = True
                return

        # 长老
        for elder in self.elders:
            if not elder.can_talk():
                continue
            dist = ((self.player.map_x - elder.map_x) ** 2 +
                    (self.player.map_y - elder.map_y) ** 2) ** 0.5
            if dist < 60:
                msg = elder.talk(self.player.hp, self.player.max_hp, self.ultimate_unlocked)
                self.dialog.show(msg)
                self.player.dx = 0
                self.player.dy = 0
                self._stop_npc_for_dialog(elder)
                if elder.upgrade_given and elder.get_upgrade_type() == "hp_boost":
                    self.player.max_hp += 50
                    self.player.hp = min(self.player.hp + 50, self.player.max_hp)
                elif elder.upgrade_given and elder.get_upgrade_type() == "ultimate":
                    self.ultimate_unlocked = True
                elif elder.upgrade_given and elder.get_upgrade_type() == "heal":
                    self.player.hp = self.player.max_hp
                return

        # 农民
        for farmer in self.farmers:
            if not farmer.can_talk():
                continue
            dist = ((self.player.map_x - farmer.map_x) ** 2 +
                    (self.player.map_y - farmer.map_y) ** 2) ** 0.5
            if dist < 50:
                self.dialog.show(farmer.talk())
                self.player.dx = 0
                self.player.dy = 0
                self._stop_npc_for_dialog(farmer)
                return

    def handle_event(self, event):
        # 退出确认对话框
        if self.confirm_dialog.visible:
            if self.confirm_dialog.handle_event(event):
                if self.confirm_dialog.choice == "yes":
                    self._pending_fade = True
                    self.fade.set_status(SCENE_OUT)
                else:
                    # 拒绝后给土地公加2秒冷却（60帧）
                    if self.god:
                        self.god.talk_cooldown = 60
                self.confirm_dialog.choice = None
            return

        if self.dialog.handle_event(event):
            self._resume_npc()
            # 土地公对话关闭后，弹出确认框
            if self.god and self._last_talked_npc == self.god:
                self._last_talked_npc = None
                self.god.talk_cooldown = 60  # 2秒冷却
                self.confirm_dialog.show("是否前往寺庙？")
            return

        if not self.dialog.visible and not self.confirm_dialog.visible:
            self.player.handle_event(event)

    def update(self):
        if self.fade.get_out():
            self.scene_done = True
            return

        if self.dialog.visible or self.confirm_dialog.visible:
            self.player.dx = 0
            self.player.dy = 0
            self.player.keys_pressed.clear()

        self.player.update()
        self._move_player_with_collision()

        self.npcs.update()
        self._check_npc_collision()
        self._update_camera()

    def draw(self, screen):
        display_surface = self.fade.get_back_image(
            int(self.camera_x), int(self.camera_y))

        for npc in self.npcs:
            npc.draw(display_surface, int(self.camera_x), int(self.camera_y))

        self.player.draw(display_surface, int(self.camera_x), int(self.camera_y))
        screen.blit(display_surface, (0, 0))
        self.dialog.draw(screen)
        self.confirm_dialog.draw(screen)

    def is_done(self):
        return self.scene_done
