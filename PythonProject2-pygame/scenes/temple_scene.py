import pygame
from core.scene import Scene, FadeScene, SceneStatus
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TEMPLE_MAP,
    DOWN, LEFT, UP, RIGHT
)
from map.tmx_map import TiledMap
from sprites.player import Player
from sprites.monster import Monster
from ui.dialog import Dialog


class TempleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tiled_map = TiledMap(TEMPLE_MAP)
        self.fade = FadeScene(self.tiled_map.map_surface)
        self.camera_x = 0
        self.camera_y = 0
        self.player = None
        self.monsters = []
        self.dialog = Dialog()
        self.in_battle = False

    def set_player(self, player):
        self.player = player
        positions = self.tiled_map.get_object_positions('actor')
        if positions:
            self.player.set_position(positions[0]['x'], positions[0]['y'])

    def on_enter(self):
        self.fade.set_status(SceneStatus.IN)
        if not self.player:
            positions = self.tiled_map.get_object_positions('actor')
            if positions:
                px, py = positions[0]['x'], positions[0]['y']
            else:
                px, py = 100, 100
            self.player = Player(px, py)
        self._load_monsters()

    def _load_monsters(self):
        self.monsters = []
        positions = self.tiled_map.get_object_positions('monster')
        for pos in positions:
            monster = Monster(pos['x'], pos['y'], monster_type='cattle')
            self.monsters.append(monster)

    def handle_events(self, event):
        if self.dialog.is_active():
            self.dialog.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_SPACE:
                self._check_monster_collision()

        self.player.handle_event(event)

    def _check_monster_collision(self):
        if self.in_battle:
            return
        player_pos = self.player.get_position()
        for monster in self.monsters:
            if not monster.alive:
                continue
            monster_pos = (monster.rect.centerx, monster.rect.centery)
            dist = ((player_pos[0] - monster_pos[0])**2 +
                    (player_pos[1] - monster_pos[1])**2) ** 0.5
            if dist < 80:
                self._start_battle(monster)
                break

    def _start_battle(self, monster):
        self.in_battle = True
        damage = 25
        monster.take_damage(damage)
        self.dialog.start([
            f'孙悟空发动攻击！造成 {damage} 点伤害！',
            f'怪物剩余生命值: {monster.health}' if monster.alive else '怪物已被击败！'
        ])
        self.in_battle = False

    def update(self, dt):
        if self.dialog.is_active():
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
        for monster in self.monsters:
            monster.update(dt)

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
        if px < 50:
            self.fade.set_status(SceneStatus.OUT)
            if self.fade.is_out_complete():
                self.game.set_scene('village')

    def draw(self, surface):
        scene_surface = self.fade.get_surface(self.camera_x, self.camera_y)
        surface.blit(scene_surface, (0, 0))

        for monster in self.monsters:
            if monster.alive:
                draw_x = monster.rect.x - self.camera_x
                draw_y = monster.rect.y - self.camera_y
                surface.blit(monster.image, (draw_x, draw_y))

        draw_x = self.player.rect.x - self.camera_x
        draw_y = self.player.rect.y - self.camera_y
        surface.blit(self.player.image, (draw_x, draw_y))

        self.dialog.draw(surface)
