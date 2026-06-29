"""
小地图模块

在屏幕右上角显示固定尺寸的小地图，
背景图等比缩放后居中绘制在底板上，
玩家（黄色）、怪物（红色）、NPC（绿色）位置同步标记。
"""

import pygame
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    MINIMAP_WIDTH, MINIMAP_HEIGHT,
    MINIMAP_MARGIN, MINIMAP_BASE_COLOR,
    MINIMAP_VIEW_COLOR, MINIMAP_VIEW_ALPHA,
    MINIMAP_PLAYER_COLOR, MINIMAP_PLAYER_SIZE,
    MINIMAP_MONSTER_COLOR, MINIMAP_MONSTER_SIZE,
    MINIMAP_BOSS_SIZE,
    MINIMAP_NPC_COLOR, MINIMAP_NPC_SIZE,
    MINIMAP_SHADOW_COLOR, MINIMAP_SHADOW_OFFSET,
    MINIMAP_SHADOW_BLUR, MINIMAP_BORDER_COLOR,
    MINIMAP_BORDER_WIDTH
)


class MiniMap:
    """小地图显示组件

    以固定尺寸 MINIMAP_WIDTH x MINIMAP_HEIGHT 为外框，
    背景图等比缩放后居中绘制，未覆盖区域用深色底板填充。
    所有标记绘制在底板之上，超出背景图范围的部分被自动裁剪。
    """

    def __init__(self, bg_image_path, map_width, map_height,
                 player, monsters=None, npcs=None):
        """
        初始化小地图

        Args:
            bg_image_path: 背景图片路径（village.jpg 或 temple.jpg）
            map_width: 游戏地图宽度（用于坐标换算）
            map_height: 游戏地图高度（用于坐标换算）
            player: 玩家对象（需要有 map_x, map_y 属性）
            monsters: 怪物精灵组（可选），红色标记
            npcs: NPC精灵组（可选），绿色标记
        """
        self.map_width = map_width
        self.map_height = map_height
        self.player = player
        self.monsters = monsters
        self.npcs = npcs

        # 小地图外框尺寸（固定）
        self.frame_width = MINIMAP_WIDTH
        self.frame_height = MINIMAP_HEIGHT

        # 加载背景图片并等比缩放
        self.bg_image = self._load_bg_image(bg_image_path)
        self.img_draw_w, self.img_draw_h = self._calc_image_size()

        # 背景图在底板上的偏移量（居中）
        self.img_offset_x = (self.frame_width - self.img_draw_w) // 2
        self.img_offset_y = (self.frame_height - self.img_draw_h) // 2

        # 世界坐标到背景图区域的换算比例（基于背景图实际尺寸）
        self.pos_scale_x = self.img_draw_w / self.map_width
        self.pos_scale_y = self.img_draw_h / self.map_height

        # 底板Surface（固定尺寸）
        self.base_surface = self._create_base_surface()

        # 小地图在屏幕上的位置（右上角）
        self.x = SCREEN_WIDTH - self.frame_width - MINIMAP_MARGIN
        self.y = MINIMAP_MARGIN

        # 阴影Surface
        self.shadow_surface = self._create_shadow_surface()

        # 视窗范围指示器尺寸
        self.view_w = int(SCREEN_WIDTH * self.pos_scale_x)
        self.view_h = int(SCREEN_HEIGHT * self.pos_scale_y)

    def _load_bg_image(self, path):
        """加载背景图片并转换像素格式"""
        return pygame.image.load(path).convert()

    def _calc_image_size(self):
        """计算背景图在底板内的等比缩放尺寸"""
        img_w, img_h = self.bg_image.get_size()
        scale_x = self.frame_width / img_w
        scale_y = self.frame_height / img_h
        scale = min(scale_x, scale_y)
        return int(img_w * scale), int(img_h * scale)

    def _create_base_surface(self):
        """创建固定尺寸的底板Surface，背景图居中绘制"""
        base = pygame.Surface((self.frame_width, self.frame_height))
        base.fill(MINIMAP_BASE_COLOR)
        scaled_bg = pygame.transform.smoothscale(
            self.bg_image, (self.img_draw_w, self.img_draw_h)
        )
        base.blit(scaled_bg, (self.img_offset_x, self.img_offset_y))
        return base

    def _create_shadow_surface(self):
        """创建边框阴影Surface"""
        blur = MINIMAP_SHADOW_BLUR
        bw = MINIMAP_BORDER_WIDTH
        shadow_w = self.frame_width + bw * 2 + blur * 2
        shadow_h = self.frame_height + bw * 2 + blur * 2
        shadow = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        for i in range(blur, 0, -1):
            alpha = int(80 * (1 - i / blur))
            inset = bw + i
            rect = pygame.Rect(inset, inset,
                               shadow_w - inset * 2,
                               shadow_h - inset * 2)
            pygame.draw.rect(shadow, (*MINIMAP_SHADOW_COLOR, alpha),
                             rect, border_radius=4)
        return shadow

    def _world_to_local(self, world_x, world_y):
        """世界坐标转小地图底板局部坐标（原点在背景图左上角）"""
        lx = self.img_offset_x + world_x * self.pos_scale_x
        ly = self.img_offset_y + world_y * self.pos_scale_y
        return int(lx), int(ly)

    def update(self, monsters=None, npcs=None):
        """更新怪物和NPC列表"""
        if monsters is not None:
            self.monsters = monsters
        if npcs is not None:
            self.npcs = npcs

    def draw(self, screen, camera_x, camera_y):
        """在屏幕上绘制小地图

        将所有标记绘制到底板Surface上，再统一blit到屏幕，
        超出背景图范围的标记被底板覆盖，无残影。

        Args:
            screen: 屏幕Surface
            camera_x: 视窗左上角X坐标（世界坐标）
            camera_y: 视窗左上角Y坐标（世界坐标）
        """
        # 基于底板副本绘制（不修改原始底板）
        frame = self.base_surface.copy()

        # 视窗范围指示器（绘制在底板上）
        #vx, vy = self._world_to_local(camera_x, camera_y)
        #view_indicator = pygame.Surface((self.view_w, self.view_h), pygame.SRCALPHA)
        #view_indicator.fill((*MINIMAP_VIEW_COLOR, MINIMAP_VIEW_ALPHA))
        #frame.blit(view_indicator, (vx, vy))

        # 绘制怪物标记（红色）
        self._draw_markers(frame, self.monsters,
                           MINIMAP_MONSTER_COLOR, MINIMAP_MONSTER_SIZE)

        # 绘制NPC标记（绿色）
        self._draw_markers(frame, self.npcs,
                           MINIMAP_NPC_COLOR, MINIMAP_NPC_SIZE)

        # 绘制玩家标记（黄色，在最上层）
        px, py = self._world_to_local(self.player.map_x, self.player.map_y)
        pygame.draw.circle(frame, MINIMAP_PLAYER_COLOR, (px, py), MINIMAP_PLAYER_SIZE)

        # 阴影
        blur = MINIMAP_SHADOW_BLUR
        bw = MINIMAP_BORDER_WIDTH
        shadow_x = self.x - bw - blur + MINIMAP_SHADOW_OFFSET
        shadow_y = self.y - bw - blur + MINIMAP_SHADOW_OFFSET
        screen.blit(self.shadow_surface, (int(shadow_x), int(shadow_y)))

        # 边框
        border_rect = pygame.Rect(
            self.x - bw, self.y - bw,
            self.frame_width + bw * 2,
            self.frame_height + bw * 2
        )
        pygame.draw.rect(screen, MINIMAP_BORDER_COLOR, border_rect,
                         width=bw, border_radius=3)

        # 底板 + 标记
        screen.blit(frame, (self.x, self.y))

    def _draw_markers(self, surface, sprite_group, color, size):
        """绘制一组精灵标记到底板Surface上"""
        if not sprite_group:
            return
        for sprite in sprite_group:
            sx = getattr(sprite, 'map_x', None)
            sy = getattr(sprite, 'map_y', None)
            if sx is None or sy is None:
                continue
            if hasattr(sprite, 'visible') and not sprite.visible:
                continue
            # BOSS使用更大的标记
            marker_size = MINIMAP_BOSS_SIZE if getattr(sprite, 'is_boss', False) else size
            lx, ly = self._world_to_local(sx, sy)
            pygame.draw.circle(surface, color, (lx, ly), marker_size)
