import os
import pygame
from core.settings import DOWN, LEFT, UP, RIGHT, ANIM_SPEED


class Animation:
    def __init__(self, frames_by_direction=None):
        self.frames_by_direction = frames_by_direction or {
            DOWN: [], LEFT: [], UP: [], RIGHT: []
        }
        self.current_direction = DOWN
        self.current_frame = 0
        self.frame_timer = 0

    @classmethod
    def from_directory(cls, directory, frames_per_direction=4, direction_order=None):
        if direction_order is None:
            direction_order = [DOWN, LEFT, UP, RIGHT]
        frames_by_direction = {}
        files = sorted([f for f in os.listdir(directory)
                        if f.endswith(('.tga', '.png', '.jpg'))])
        total_frames = len(files)
        frames_per_dir = total_frames // len(direction_order)
        for i, direction in enumerate(direction_order):
            start = i * frames_per_dir
            end = start + frames_per_dir
            direction_files = files[start:end]
            frames = []
            for f in direction_files:
                img = pygame.image.load(os.path.join(directory, f)).convert_alpha()
                frames.append(img)
            frames_by_direction[direction] = frames
        return cls(frames_by_direction)

    @classmethod
    def from_files(cls, file_list, direction):
        frames = []
        for f in file_list:
            img = pygame.image.load(f).convert_alpha()
            frames.append(img)
        frames_by_direction = {direction: frames}
        return cls(frames_by_direction)

    def set_direction(self, direction):
        if direction != self.current_direction:
            self.current_direction = direction
            self.current_frame = 0
            self.frame_timer = 0

    def update(self, dt):
        frames = self.frames_by_direction.get(self.current_direction, [])
        if not frames:
            return
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(frames)

    def get_current_frame(self):
        frames = self.frames_by_direction.get(self.current_direction, [])
        if frames:
            return frames[self.current_frame]
        return None

    def get_frame_count(self, direction=None):
        if direction is None:
            direction = self.current_direction
        return len(self.frames_by_direction.get(direction, []))
