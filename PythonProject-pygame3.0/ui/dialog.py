import pygame
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, WHITE


class Dialog:
    """对话框类"""

    def __init__(self):
        self.visible = False
        self.text = ""
        self.font = None
        self.dialog_img = None
        self._load_resources()

    def _load_resources(self):
        """加载对话框资源"""
        try:
            self.font = pygame.font.Font(FONT_PATH, 24)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 24)

        try:
            self.dialog_img = pygame.image.load(
                r"D:\Documents\pygame.resource\resource\img\dialog\dialog.png"
            ).convert_alpha()
        except Exception:
            self.dialog_img = None

    def show(self, text):
        """显示对话框"""
        self.visible = True
        self.text = text

    def hide(self):
        """隐藏对话框"""
        self.visible = False
        self.text = ""

    def handle_event(self, event):
        """处理事件，按键关闭对话框"""
        if self.visible and event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.hide()
                return True
        return False

    def draw(self, surface):
        """绘制对话框"""
        if not self.visible:
            return

        # 对话框尺寸和位置
        dialog_w = 600
        dialog_h = 150
        dialog_x = (SCREEN_WIDTH - dialog_w) // 2
        dialog_y = SCREEN_HEIGHT - dialog_h - 20

        if self.dialog_img:
            # 缩放对话框图片
            scaled = pygame.transform.scale(self.dialog_img, (dialog_w, dialog_h))
            surface.blit(scaled, (dialog_x, dialog_y))
        else:
            # 绘制半透明背景
            dialog_surface = pygame.Surface((dialog_w, dialog_h), pygame.SRCALPHA)
            dialog_surface.fill((0, 0, 0, 180))
            pygame.draw.rect(dialog_surface, (255, 255, 255, 200),
                             (0, 0, dialog_w, dialog_h), 2)
            surface.blit(dialog_surface, (dialog_x, dialog_y))

        # 绘制文字
        if self.text and self.font:
            # 自动换行
            lines = self._wrap_text(self.text, dialog_w - 40)
            for i, line in enumerate(lines):
                text_surface = self.font.render(line, True, WHITE)
                text_x = dialog_x + 20
                text_y = dialog_y + 20 + i * 30
                surface.blit(text_surface, (text_x, text_y))

    def _wrap_text(self, text, max_width):
        """文字自动换行"""
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if self.font.size(test_line)[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        return lines
