import enum
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class SceneStatus(enum.IntEnum):
    IN = 1
    NORMAL = 2
    OUT = 3


class Scene:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class FadeScene:
    def __init__(self, back_image):
        self.back_image = back_image
        self.alpha = 0
        self.status = SceneStatus.IN

    def set_status(self, status):
        self.status = status
        if status == SceneStatus.IN:
            self.alpha = 0
        elif status == SceneStatus.NORMAL:
            self.alpha = 255
        elif status == SceneStatus.OUT:
            self.alpha = 0

    def is_out_complete(self):
        return self.status == SceneStatus.OUT and self.alpha >= 255

    def update(self, dt):
        pass

    def get_surface(self, x=0, y=0):
        x = max(0, min(x, self.back_image.get_width() - SCREEN_WIDTH))
        y = max(0, min(y, self.back_image.get_height() - SCREEN_HEIGHT))
        temp_surface = self.back_image.subsurface((x, y, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.status == SceneStatus.NORMAL:
            return temp_surface

        elif self.status == SceneStatus.IN:
            temp_surface.set_alpha(self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 10
            if self.alpha >= 255:
                self.alpha = 255
                self.status = SceneStatus.NORMAL
            return black_surface

        elif self.status == SceneStatus.OUT:
            temp_surface.set_alpha(255 - self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 10
            if self.alpha >= 255:
                self.alpha = 255
            return black_surface

        return temp_surface
