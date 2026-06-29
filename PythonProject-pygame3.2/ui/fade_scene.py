import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_IN, SCENE_NORMAL, SCENE_OUT


class FadeScene:
    """场景渐入渐出效果类"""

    def __init__(self, back_image):
        """
        Args:
            back_image: 背景地图Surface（完整大地图）
        """
        self.back_image = back_image
        self.alpha = 0
        self.status = SCENE_IN
        self.alpha_step = 20  # 每帧alpha变化量

    def set_status(self, status):
        """设置场景状态"""
        self.status = status
        if status == SCENE_IN:
            self.alpha = 0
        elif status == SCENE_NORMAL:
            self.alpha = 255
        elif status == SCENE_OUT:
            self.alpha = 0

    def get_out(self):
        """判断渐出是否完成"""
        return self.status == SCENE_OUT and self.alpha >= 255

    def get_in(self):
        """判断渐入是否完成"""
        return self.status == SCENE_IN and self.alpha >= 255

    def get_back_image(self, x, y):
        """
        获取带alpha效果的背景画面

        Args:
            x: 视窗左上角在地图上的X坐标
            y: 视窗左上角在地图上的Y坐标

        Returns:
            处理后的Surface (800x600)
        """
        # 边界限制
        map_w = self.back_image.get_width()
        map_h = self.back_image.get_height()

        x = max(0, min(x, map_w - SCREEN_WIDTH))
        y = max(0, min(y, map_h - SCREEN_HEIGHT))

        # 截取视窗区域
        try:
            temp_surface = self.back_image.subsurface(
                (x, y, SCREEN_WIDTH, SCREEN_HEIGHT)).copy()
        except ValueError:
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            temp_surface.blit(self.back_image, (0, 0),
                              (x, y, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.status == SCENE_NORMAL:
            return temp_surface

        elif self.status == SCENE_IN:
            # 渐入：从黑屏到正常画面
            temp_surface.set_alpha(self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.fill((0, 0, 0))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += self.alpha_step
            if self.alpha >= 255:
                self.alpha = 255
                self.status = SCENE_NORMAL
            return black_surface

        elif self.status == SCENE_OUT:
            # 渐出：从正常画面到黑屏
            temp_surface.set_alpha(255 - self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.fill((0, 0, 0))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += self.alpha_step
            if self.alpha >= 255:
                self.alpha = 255
            return black_surface

        return temp_surface
