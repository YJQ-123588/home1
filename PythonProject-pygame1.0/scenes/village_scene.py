import pygame
from core.scene import Scene, FadeScene, SceneStatus
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, VILLAGE_MAP
from map.tmx_map import TiledMap


class TestScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tiled_map = TiledMap(VILLAGE_MAP)
        self.fade = FadeScene(self.tiled_map.map_surface)
        self.camera_x = 0
        self.camera_y = 0

    def on_enter(self):
        self.fade.set_status(SceneStatus.IN)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.quit()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        speed = 3
        if keys[pygame.K_LEFT]:
            self.camera_x -= speed
        if keys[pygame.K_RIGHT]:
            self.camera_x += speed
        if keys[pygame.K_UP]:
            self.camera_y -= speed
        if keys[pygame.K_DOWN]:
            self.camera_y += speed

        map_w, map_h = self.tiled_map.get_map_size()
        self.camera_x = max(0, min(self.camera_x, map_w - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, map_h - SCREEN_HEIGHT))

        self.fade.update(dt)

    def draw(self, surface):
        scene_surface = self.fade.get_surface(self.camera_x, self.camera_y)
        surface.blit(scene_surface, (0, 0))
