import pygame
from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,
                             BLACK, WHITE, RED, YELLOW, GREEN)


class AvoidBattleDialog:
    """避战选择对话框"""

    def __init__(self):
        self.visible = False
        self.monster_name = ""
        self.choice = None
        self.cost_hp = 20

        try:
            self.font = pygame.font.Font(FONT_PATH, 24)
            self.small_font = pygame.font.Font(FONT_PATH, 20)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 24)
            self.small_font = pygame.font.SysFont('simhei', 20)

        dialog_w, dialog_h = 500, 250
        dialog_x = (SCREEN_WIDTH - dialog_w) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_h) // 2
        self.dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)

        btn_w, btn_h = 140, 50
        btn_y = dialog_y + 170
        self.btn_fight = pygame.Rect(dialog_x + 60, btn_y, btn_w, btn_h)
        self.btn_avoid = pygame.Rect(dialog_x + 300, btn_y, btn_w, btn_h)

    def show(self, monster_name):
        self.visible = True
        self.monster_name = monster_name
        self.choice = None

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.btn_fight.collidepoint(mx, my):
                self.choice = "fight"
                self.hide()
                return True
            elif self.btn_avoid.collidepoint(mx, my):
                self.choice = "avoid"
                self.hide()
                return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.choice = "fight"
                self.hide()
                return True
            elif event.key == pygame.K_2:
                self.choice = "avoid"
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

        title = self.font.render(f"遭遇 {self.monster_name}！", True, RED)
        title_x = self.dialog_rect.centerx - title.get_width() // 2
        screen.blit(title, (title_x, self.dialog_rect.y + 20))

        msg1 = self.small_font.render(f"是否花费 {self.cost_hp} 点生命值避开战斗？", True, WHITE)
        msg1_x = self.dialog_rect.centerx - msg1.get_width() // 2
        screen.blit(msg1, (msg1_x, self.dialog_rect.y + 70))

        msg2 = self.small_font.render("（避战后怪物仍会阻挡去路）", True, YELLOW)
        msg2_x = self.dialog_rect.centerx - msg2.get_width() // 2
        screen.blit(msg2, (msg2_x, self.dialog_rect.y + 100))

        pygame.draw.rect(screen, GREEN, self.btn_fight)
        pygame.draw.rect(screen, WHITE, self.btn_fight, 2)
        fight_text = self.small_font.render("1.战斗", True, BLACK)
        screen.blit(fight_text, (self.btn_fight.centerx - fight_text.get_width() // 2,
                                 self.btn_fight.centery - fight_text.get_height() // 2))

        pygame.draw.rect(screen, RED, self.btn_avoid)
        pygame.draw.rect(screen, WHITE, self.btn_avoid, 2)
        avoid_text = self.small_font.render("2.避战(-20HP)", True, BLACK)
        screen.blit(avoid_text, (self.btn_avoid.centerx - avoid_text.get_width() // 2,
                                 self.btn_avoid.centery - avoid_text.get_height() // 2))
