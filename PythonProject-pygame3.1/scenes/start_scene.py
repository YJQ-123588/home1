import pygame
from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,
                             VILLAGE_IMG, BLACK, WHITE, GOLD)


class StartScene:
    """游戏开始界面"""

    def __init__(self):
        self.done = False

        try:
            self.font = pygame.font.Font(FONT_PATH, 48)
            self.small_font = pygame.font.Font(FONT_PATH, 28)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 48)
            self.small_font = pygame.font.SysFont('simhei', 28)

        try:
            self.bg = pygame.image.load(VILLAGE_IMG).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 120))
            self.bg.blit(dark, (0, 0))
        except Exception:
            self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg.fill((20, 15, 10))

        self.btn_start = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 60)
        self.btn_quit = pygame.Rect(SCREEN_WIDTH // 2 - 100, 440, 200, 60)

        self.btn_start_img = None
        self.btn_quit_img = None
        try:
            self.btn_start_img = pygame.image.load(
                r"D:\Documents\pygame.resource\resource\img\village_button.png"
            ).convert_alpha()
            self.btn_start_img = pygame.transform.scale(self.btn_start_img, (200, 60))
        except Exception:
            pass

        try:
            self.btn_quit_img = pygame.image.load(
                r"D:\Documents\pygame.resource\resource\img\temple_button.png"
            ).convert_alpha()
            self.btn_quit_img = pygame.transform.scale(self.btn_quit_img, (200, 60))
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.btn_start.collidepoint(mx, my):
                self.done = True
                return "start"
            elif self.btn_quit.collidepoint(mx, my):
                return "quit"
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.done = True
                return "start"
            elif event.key == pygame.K_ESCAPE:
                return "quit"
        return None

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        title = self.font.render("西游记 - 祸起观音院", True, GOLD)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 150))

        subtitle = self.small_font.render("RPG冒险游戏", True, WHITE)
        sub_x = SCREEN_WIDTH // 2 - subtitle.get_width() // 2
        screen.blit(subtitle, (sub_x, 220))

        if self.btn_start_img:
            screen.blit(self.btn_start_img, self.btn_start.topleft)
        else:
            pygame.draw.rect(screen, (50, 150, 50), self.btn_start)
            pygame.draw.rect(screen, WHITE, self.btn_start, 2)
            btn_text = self.small_font.render("开始游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_start.centerx - btn_text.get_width() // 2,
                                   self.btn_start.centery - btn_text.get_height() // 2))

        if self.btn_quit_img:
            screen.blit(self.btn_quit_img, self.btn_quit.topleft)
        else:
            pygame.draw.rect(screen, (150, 50, 50), self.btn_quit)
            pygame.draw.rect(screen, WHITE, self.btn_quit, 2)
            btn_text = self.small_font.render("退出游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_quit.centerx - btn_text.get_width() // 2,
                                   self.btn_quit.centery - btn_text.get_height() // 2))

        hint = self.small_font.render("按回车键开始 | ESC退出", True, WHITE)
        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        screen.blit(hint, (hint_x, 530))
