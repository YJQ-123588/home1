import pygame
from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,
                             BLACK, WHITE, RED, YELLOW, GREEN, PURPLE)


class StatusBar:
    """游戏界面左上角状态栏"""

    def __init__(self):
        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.small_font = pygame.font.Font(FONT_PATH, 14)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 18)
            self.small_font = pygame.font.SysFont('simhei', 14)

        self.bar_width = 200
        self.bar_height = 12
        self.padding = 5
        self.bg_color = (0, 0, 0, 180)

    def draw(self, screen, player_hp, player_max_hp, player_atk, ultimate_unlocked):
        """绘制状态栏"""
        x, y = 10, 10

        # 背景框
        bg_width = 180
        bg_height = 95
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, (x, y))

        # 标题
        title = self.font.render("孙悟空", True, YELLOW)
        screen.blit(title, (x + 5, y + 3))

        # 血条
        hp_label = self.small_font.render("HP:", True, WHITE)
        screen.blit(hp_label, (x + 5, y + 25))

        bar_x = x + 30
        bar_y = y + 25
        bar_width = 120
        bar_height = 10
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        ratio = max(0, player_hp / player_max_hp) if player_max_hp > 0 else 0
        fill_w = int(bar_width * ratio)
        if ratio > 0.5:
            bar_color = GREEN
        elif ratio > 0.25:
            bar_color = YELLOW
        else:
            bar_color = RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        hp_text = self.small_font.render(f"{player_hp}/{player_max_hp}", True, WHITE)
        screen.blit(hp_text, (bar_x + bar_width + 3, bar_y - 2))

        # 技能信息
        skill_y = y + 45
        skills = [
            ("普攻", player_atk, GREEN),
            ("金箍棒", player_atk + 35, YELLOW),
        ]
        if ultimate_unlocked:
            skills.append(("七十二变", player_atk + 75, PURPLE))

        for i, (name, damage, color) in enumerate(skills):
            skill_text = self.small_font.render(f"{name}: {damage}", True, color)
            screen.blit(skill_text, (x + 8, skill_y + i * 16))
