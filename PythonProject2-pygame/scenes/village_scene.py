import pygame
import os
from core.scene import Scene, FadeScene, SceneStatus
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, VILLAGE_MAP, IMG_DIR,
    DOWN, LEFT, UP, RIGHT
)
from map.tmx_map import TiledMap
from sprites.player import Player
from sprites.npc import NPC
from ui.dialog import Dialog


class VillageScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tiled_map = TiledMap(VILLAGE_MAP)
        self.fade = FadeScene(self.tiled_map.map_surface)
        self.camera_x = 0
        self.camera_y = 0

        positions = self.tiled_map.get_object_positions('actor')
        if positions:
            px, py = positions[0]['x'], positions[0]['y']
        else:
            px, py = 400, 400
        self.player = Player(px, py)

        self.npcs = []
        god_positions = self.tiled_map.get_object_positions('god')
        for pos in god_positions:
            npc = NPC(
                pos['x'], pos['y'],
                npc_type='god',
                dialogue=['土地公：大圣，您终于来了！', '观音院就在前方，请随我来。']
            )
            self.npcs.append(npc)

        elder_positions = self.tiled_map.get_object_positions('elder')
        for pos in elder_positions:
            npc = NPC(
                pos['x'], pos['y'],
                npc_type='elder',
                dialogue=['长者：欢迎来到观音院。']
            )
            self.npcs.append(npc)

        self.dialog = Dialog()
        self.talking_to = None
        self.transitioning = False

    def on_enter(self):
        self.fade.set_status(SceneStatus.IN)

    def handle_events(self, event):
        if self.dialog.is_active():
            self.dialog.handle_event(event)
            if not self.dialog.is_active():
                if self.talking_to:
                    self.talking_to.stop_talk()
                    self.talking_to = None
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_SPACE:
                self._check_npc_collision()

        self.player.handle_event(event)

    def _check_npc_collision(self):
        player_pos = self.player.get_position()
        for npc in self.npcs:
            npc_pos = (npc.rect.centerx, npc.rect.centery)
            dist = ((player_pos[0] - npc_pos[0])**2 +
                    (player_pos[1] - npc_pos[1])**2) ** 0.5
            if dist < 80:
                dialogue = npc.get_dialogue()
                if dialogue:
                    self.dialog.start(dialogue)
                    npc.start_talk()
                    self.talking_to = npc
                break

    def update(self, dt):
        if self.dialog.is_active():
            return

        if self.transitioning:
            if self.fade.is_out_complete():
                self.transitioning = False
                self.game.set_scene('temple')
            return

        keys = pygame.key.get_pressed()
        speed = 3
        if keys[pygame.K_LEFT]:
            self.player.direction = LEFT
            self.player.moving = True
        elif keys[pygame.K_RIGHT]:
            self.player.direction = RIGHT
            self.player.moving = True
        elif keys[pygame.K_UP]:
            self.player.direction = UP
            self.player.moving = True
        elif keys[pygame.K_DOWN]:
            self.player.direction = DOWN
            self.player.moving = True

        self.player.update(dt)
        for npc in self.npcs:
            npc.update(dt)

        self._update_camera()
        self.fade.update(dt)

        self._check_scene_transition()

    def _update_camera(self):
        px, py = self.player.get_position()
        self.camera_x = px - SCREEN_WIDTH // 2
        self.camera_y = py - SCREEN_HEIGHT // 2

        map_w, map_h = self.tiled_map.get_map_size()
        self.camera_x = max(0, min(self.camera_x, map_w - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, map_h - SCREEN_HEIGHT))

    def _check_scene_transition(self):
        px, py = self.player.get_position()
        map_w, map_h = self.tiled_map.get_map_size()
        if px > map_w - 100:
            self.transitioning = True
            self.fade.set_status(SceneStatus.OUT)

    def draw(self, surface):
        scene_surface = self.fade.get_surface(self.camera_x, self.camera_y)
        surface.blit(scene_surface, (0, 0))

        for npc in self.npcs:
            draw_x = npc.rect.x - self.camera_x
            draw_y = npc.rect.y - self.camera_y
            surface.blit(npc.image, (draw_x, draw_y))

        draw_x = self.player.rect.x - self.camera_x
        draw_y = self.player.rect.y - self.camera_y
        surface.blit(self.player.image, (draw_x, draw_y))

        self.dialog.draw(surface)
