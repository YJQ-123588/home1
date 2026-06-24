import os
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, FONT_SIZE, BLACK, WHITE, IMG_DIR


class Dialog:
    def __init__(self):
        self.active = False
        self.texts = []
        self.current_index = 0
        self.font = None
        self.dialog_image = None
        self._load_assets()

    def _load_assets(self):
        try:
            self.font = pygame.font.Font(FONT_PATH, FONT_SIZE)
        except:
            self.font = pygame.font.SysFont('simhei', FONT_SIZE)
        try:
            dialog_path = os.path.join(IMG_DIR, 'dialog', 'dialog.png')
            if os.path.exists(dialog_path):
                self.dialog_image = pygame.image.load(dialog_path).convert_alpha()
            else:
                self.dialog_image = None
        except:
            self.dialog_image = None

    def start(self, texts):
        self.texts = texts
        self.current_index = 0
        self.active = True

    def next_text(self):
        self.current_index += 1
        if self.current_index >= len(self.texts):
            self.active = False
            return False
        return True

    def is_active(self):
        return self.active

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_text()

    def draw(self, surface):
        if not self.active:
            return
        if self.current_index >= len(self.texts):
            return

        dialog_width = 600
        dialog_height = 150
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = SCREEN_HEIGHT - dialog_height - 20

        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        dialog_surface = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        dialog_surface.fill((0, 0, 0, 200))

        border_rect = pygame.Rect(0, 0, dialog_width, dialog_height)
        pygame.draw.rect(dialog_surface, WHITE, border_rect, 2)

        current_text = self.texts[self.current_index]
        text_lines = self._wrap_text(current_text, dialog_width - 40)

        y_offset = 15
        for line in text_lines:
            text_surface = self.font.render(line, True, WHITE)
            dialog_surface.blit(text_surface, (20, y_offset))
            y_offset += 30

        hint_text = self.font.render('[SPACE] ', True, (150, 150, 150))
        dialog_surface.blit(hint_text, (dialog_width - 120, dialog_height - 30))

        surface.blit(dialog_surface, (dialog_x, dialog_y))

    def _wrap_text(self, text, max_width):
        lines = []
        current_line = ''
        for char in text:
            test_line = current_line + char
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines
