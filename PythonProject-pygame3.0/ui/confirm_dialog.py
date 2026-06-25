import pygame
from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,
                             BLACK, WHITE, GREEN, RED)


class ConfirmDialog:
    """通用确认对话框"""

    def __init__(self):
        self.visible = False
        self.message = ""
        self.choice = None

        try:
            self.font = pygame.font.Font(FONT_PATH, 24)
            self.small_font = pygame.font.Font(FONT_PATH, 20)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 24)
            self.small_font = pygame.font.SysFont('simhei', 20)

        dialog_w, dialog_h = 400, 200
        dialog_x = (SCREEN_WIDTH - dialog_w) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_h) // 2
        self.dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        btn_w, btn_h = 120, 45
        btn_y = dialog_y + 130
        self.btn_yes = pygame.Rect(dialog_x + 50, btn_y, btn_w, btn_h)
        self.btn_no = pygame.Rect(dialog_x + 230, btn_y, btn_w, btn_h)

    def show(self, message):
        self.visible = True
        self.message = message
        self.choice = None

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.btn_yes.collidepoint(mx, my):
                self.choice = "yes"
                self.hide()
                return True
            elif self.btn_no.collidepoint(mx, my):
                self.choice = "no"
                self.hide()
                return True

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_y, pygame.K_RETURN, pygame.K_SPACE):
                self.choice = "yes"
                self.hide()
                return True
            elif event.key in (pygame.K_2, pygame.K_n, pygame.K_ESCAPE):
                self.choice = "no"
                self.hide()
                return True

        return False

    def draw(self, screen):
        if not self.visible:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, (30, 30, 50), self.dialog_rect)
        pygame.draw.rect(screen, WHITE, self.dialog_rect, 3)

        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            text = self.font.render(line, True, WHITE)
            text_x = self.dialog_rect.centerx - text.get_width() // 2
            text_y = self.dialog_rect.y + 30 + i * 35
            screen.blit(text, (text_x, text_y))

        pygame.draw.rect(screen, GREEN, self.btn_yes)
        pygame.draw.rect(screen, WHITE, self.btn_yes, 2)
        yes_text = self.small_font.render("1.确定", True, BLACK)
        screen.blit(yes_text, (self.btn_yes.centerx - yes_text.get_width() // 2,
                               self.btn_yes.centery - yes_text.get_height() // 2))

        pygame.draw.rect(screen, RED, self.btn_no)
        pygame.draw.rect(screen, WHITE, self.btn_no, 2)
        no_text = self.small_font.render("2.取消", True, BLACK)
        screen.blit(no_text, (self.btn_no.centerx - no_text.get_width() // 2,
                              self.btn_no.centery - no_text.get_height() // 2))
