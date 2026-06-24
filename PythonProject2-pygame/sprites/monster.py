import pygame
import os
from core.settings import MONSTER_SPEED, DOWN, LEFT, UP, RIGHT, IMG_DIR
from sprites.animation import Animation


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, monster_type='cattle'):
        super().__init__()
        self.monster_type = monster_type
        self.load_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = MONSTER_SPEED
        self.direction = DOWN
        self.moving = True
        self.step_count = 0
        self.step_limit = 80
        self.health = 50
        self.alive = True

    def load_sprite(self):
        if self.monster_type == 'cattle':
            sprite_dir = os.path.join(IMG_DIR, 'cattle', 'walk1')
            self.animation = Animation.from_directory(sprite_dir)
        else:
            sprite_dir = os.path.join(IMG_DIR, 'cattle', 'walk1')
            self.animation = Animation.from_directory(sprite_dir)
        self.image = self.animation.get_current_frame()

    def update(self, dt, obstacles=None):
        if not self.alive:
            return

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
                        self.change_direction()
                        break

            self.step_count += 1
            if self.step_count >= self.step_limit:
                self.step_count = 0
                self.change_direction()

        self.animation.update(dt)
        self.image = self.animation.get_current_frame()

    def change_direction(self):
        if self.direction == DOWN:
            self.direction = UP
        elif self.direction == UP:
            self.direction = DOWN
        elif self.direction == LEFT:
            self.direction = RIGHT
        elif self.direction == RIGHT:
            self.direction = LEFT

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.kill()
