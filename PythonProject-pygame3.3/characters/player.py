import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_LSHIFT, K_RSHIFT, K_w, K_a, K_s, K_d
from config.settings import PLAYER_SPEED, PLAYER_ANIM_SPEED, PLAYER_BASE_HP
from core.animation import Animation, load_swk_frames


class Player(pygame.sprite.Sprite):
    """孙悟空玩家类"""

    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3

    def __init__(self, img_path, x, y):
        super().__init__()
        self.direction_frames = load_swk_frames(img_path)
        self.target_size = (80, 100)
        for d in self.direction_frames:
            self.direction_frames[d] = [
                pygame.transform.scale(f, self.target_size)
                for f in self.direction_frames[d]
            ]
        self.direction = self.DOWN
        self.anim = Animation(self.direction_frames[self.DOWN], PLAYER_ANIM_SPEED)

        self.image = self.anim.get_current_frame()
        self.rect = self.image.get_rect(center=(x, y))

        self.map_x = float(x)
        self.map_y = float(y)

        # 属性
        self.hp = PLAYER_BASE_HP
        self.max_hp = PLAYER_BASE_HP

        # 移动状态
        self.moving = False
        self.dx = 0
        self.dy = 0

        # 加速状态
        self.boost = False

        # 按键追踪
        self.keys_pressed = set()

    def _update_velocity(self):
        """根据按下的键重新计算速度"""
        speed = PLAYER_SPEED * 2 if self.boost else PLAYER_SPEED
        self.dx = 0
        self.dy = 0

        up_keys = {K_UP, K_w}
        down_keys = {K_DOWN, K_s}
        left_keys = {K_LEFT, K_a}
        right_keys = {K_RIGHT, K_d}

        if self.keys_pressed & up_keys:
            self.dy = -speed
            self.direction = self.UP
        elif self.keys_pressed & down_keys:
            self.dy = speed
            self.direction = self.DOWN

        if self.keys_pressed & left_keys:
            self.dx = -speed
            self.direction = self.LEFT
        elif self.keys_pressed & right_keys:
            self.dx = speed
            self.direction = self.RIGHT

    def handle_event(self, event):
        """处理键盘事件"""
        if event.type == pygame.KEYDOWN:
            if event.key in (K_LSHIFT, K_RSHIFT):
                self.boost = True
                self._update_velocity()
                return

            if event.key in (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d):
                self.keys_pressed.add(event.key)
                self._update_velocity()

        elif event.type == pygame.KEYUP:
            if event.key in (K_LSHIFT, K_RSHIFT):
                self.boost = False
                self._update_velocity()
                return

            if event.key in (K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d):
                self.keys_pressed.discard(event.key)
                self._update_velocity()

    def update(self):
        """更新玩家动画（位置由场景的碰撞检测方法处理）"""
        new_frames = self.direction_frames[self.direction]
        self.anim.set_frames(new_frames)

        self.moving = (self.dx != 0 or self.dy != 0)

        if self.moving:
            # 加速时动画更快
            self.anim.speed = max(3, PLAYER_ANIM_SPEED - 3) if self.boost else PLAYER_ANIM_SPEED
            self.anim.update()
        else:
            self.anim.reset()

        self.image = self.anim.get_current_frame()

    def check_obstacle_collision(self, obstacle_rects):
        test_rect = self.rect.copy()
        test_rect.center = (int(self.map_x), int(self.map_y))
        for obs_rect in obstacle_rects:
            if test_rect.colliderect(obs_rect):
                return True
        return False

    def move_with_collision(self, obstacle_rects, map_width, map_height):
        old_x = self.map_x
        old_y = self.map_y
        self.map_x += self.dx
        self.rect.center = (int(self.map_x), int(self.map_y))
        if self.check_obstacle_collision(obstacle_rects):
            self.map_x = old_x
        self.map_y += self.dy
        self.rect.center = (int(self.map_x), int(self.map_y))
        if self.check_obstacle_collision(obstacle_rects):
            self.map_y = old_y
        half_w = self.rect.width // 2
        half_h = self.rect.height // 2
        self.map_x = max(half_w, min(self.map_x, map_width - half_w))
        self.map_y = max(half_h, min(self.map_y, map_height - half_h))
        self.rect.center = (int(self.map_x), int(self.map_y))

    def get_direction_name(self):
        names = {0: 'down', 1: 'left', 2: 'up', 3: 'right'}
        return names.get(self.direction, 'down')

    def draw(self, surface, offset_x=0, offset_y=0):
        draw_x = self.rect.x - offset_x
        draw_y = self.rect.y - offset_y
        surface.blit(self.image, (draw_x, draw_y))
