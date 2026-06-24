import pygame
import os
from core.settings import (
    PLAYER_SPEED, DOWN, LEFT, UP, RIGHT,
    SCREEN_WIDTH, SCREEN_HEIGHT, IMG_DIR
)
from sprites.animation import Animation


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        swk_dir = os.path.join(IMG_DIR, 'swk')
        self.animation = Animation.from_directory(swk_dir)
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = PLAYER_SPEED
        self.direction = DOWN
        self.moving = False
        self.health = 100

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.direction = DOWN
                self.moving = True
            elif event.key == pygame.K_UP:
                self.direction = UP
                self.moving = True
            elif event.key == pygame.K_LEFT:
                self.direction = LEFT
                self.moving = True
            elif event.key == pygame.K_RIGHT:
                self.direction = RIGHT
                self.moving = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT):
                self.moving = False

    def update(self, dt, obstacles=None):
        if self.moving:
            self.animation.set_direction(self.direction)
            dx, dy = 0, 0
            if self.direction == DOWN:
                dy = self.speed
            elif self.direction == UP:
                dy = -self.speed
            elif self.direction == LEFT:
                dx = -self.speed
            elif self.direction == RIGHT:
                dx = self.speed

            old_rect = self.rect.copy()
            self.rect.x += dx
            self.rect.y += dy

            if obstacles:
                for obs in obstacles:
                    if self.rect.colliderect(obs):
                        self.rect = old_rect
                        break

        self.animation.update(dt)
        self.image = self.animation.get_current_frame()

    def set_position(self, x, y):
        self.rect.center = (x, y)

    def get_position(self):
        return self.rect.centerx, self.rect.centery
