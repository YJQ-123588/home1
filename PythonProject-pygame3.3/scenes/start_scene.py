import pygame
from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH,
                             VILLAGE_IMG, BLACK, WHITE, GOLD, YELLOW, GREEN)
from core.save_load import get_all_saves, delete_game, save_game


class StartScene:
    """游戏开始界面"""

    def __init__(self, show_return_village=False):
        self.done = False
        self.show_help = False
        self.show_load = False
        self.show_save = False
        self.scroll_offset = 0
        self.can_continue = False  # 是否可以从游戏返回
        self.show_return_village = show_return_village  # 是否显示返回村庄按钮

        try:
            self.font = pygame.font.Font(FONT_PATH, 48)
            self.small_font = pygame.font.Font(FONT_PATH, 28)
            self.help_font = pygame.font.Font(FONT_PATH, 22)
        except Exception:
            self.font = pygame.font.SysFont('simhei', 48)
            self.small_font = pygame.font.SysFont('simhei', 28)
            self.help_font = pygame.font.SysFont('simhei', 22)

        try:
            self.bg = pygame.image.load(VILLAGE_IMG).convert()
            self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 120))
            self.bg.blit(dark, (0, 0))
        except Exception:
            self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.bg.fill((20, 15, 10))

        self._init_buttons()

    def _init_buttons(self):
        """初始化按钮位置"""
        btn_x = SCREEN_WIDTH // 2 - 100
        btn_w = 200
        btn_h = 50
        gap = 10

        # 开始界面按钮（未进入游戏）
        self.btn_start = pygame.Rect(btn_x, 290, btn_w, btn_h)
        self.btn_load_start = pygame.Rect(btn_x, 290 + btn_h + gap, btn_w, btn_h)
        self.btn_help_start = pygame.Rect(btn_x, 290 + (btn_h + gap) * 2, btn_w, btn_h)
        self.btn_quit_start = pygame.Rect(btn_x, 290 + (btn_h + gap) * 3, btn_w, btn_h)

        # 游戏中菜单按钮（按ESC打开）
        y = 290
        self.btn_continue = pygame.Rect(btn_x, y, btn_w, btn_h)
        y += btn_h + gap
        self.btn_return_village = pygame.Rect(btn_x, y, btn_w, btn_h)
        if self.show_return_village:
            y += btn_h + gap
        self.btn_load = pygame.Rect(btn_x, y, btn_w, btn_h)
        y += btn_h + gap
        self.btn_help = pygame.Rect(btn_x, y, btn_w, btn_h)
        y += btn_h + gap
        self.btn_quit = pygame.Rect(btn_x, y, btn_w, btn_h)

        # 存档/读档槽按钮
        self.slots = []
        for i in range(3):
            y = 180 + i * 120
            self.slots.append({
                "action": pygame.Rect(SCREEN_WIDTH // 2 - 150, y, 130, 50),
                "delete": pygame.Rect(SCREEN_WIDTH // 2 + 20, y, 130, 50),
            })

        self.confirm_delete = None
        self.btn_confirm_yes = pygame.Rect(SCREEN_WIDTH // 2 - 110, 400, 100, 40)
        self.btn_confirm_no = pygame.Rect(SCREEN_WIDTH // 2 + 10, 400, 100, 40)

        # 返回按钮（用于帮助、存档、读档界面）
        self.btn_back = pygame.Rect(btn_x, 350 + (btn_h + gap) * 5, btn_w, btn_h)

        self.save_msg = ""
        self.save_msg_timer = 0

    def _calc_help_content_height(self):
        """计算游戏介绍界面的总内容高度"""
        y = 100
        # intro lines
        y += 2 * 30
        y += 20
        # 操作说明 title
        y += 40
        # controls sections
        controls = [
            ("移动控制", ["方向键 或 W/A/S/D：控制角色移动", "Shift键：加速移动"]),
            ("交互操作", ["空格/回车键：关闭对话框、确认选择", "ESC键：打开菜单（存档/读档/继续）"]),
            ("战斗操作", [
                "点击「普攻」按钮：普通攻击",
                "点击「金箍棒」按钮：技能攻击",
                "点击「七十二变」按钮：大招攻击（需解锁）",
                "数字键 1/2/3：对应三种攻击方式",
            ]),
        ]
        for section, items in controls:
            y += 28
            y += len(items) * 25
            y += 10
        y += 5
        # 游戏流程 title
        y += 40
        # flow items
        y += 4 * 25
        return y

    def handle_event(self, event):
        if self.show_help:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * 30
                max_scroll = self._calc_help_content_height() - (SCREEN_HEIGHT - 160)
                max_scroll = max(0, max_scroll)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    return None
                mx, my = event.pos
                if self.btn_back.collidepoint(mx, my):
                    self.show_help = False
                    self.scroll_offset = 0
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                    self.show_help = False
                    self.scroll_offset = 0
            return None

        if self.show_save:
            return self._handle_save_event(event)

        if self.show_load:
            return self._handle_load_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                return None
            mx, my = event.pos
            if self.can_continue:
                # 游戏中菜单
                if self.btn_continue.collidepoint(mx, my):
                    return "continue"
                if self.show_return_village and self.btn_return_village.collidepoint(mx, my):
                    return "return_village"
                if self.btn_load.collidepoint(mx, my):
                    self.show_load = True
                    return None
                if self.btn_help.collidepoint(mx, my):
                    self.show_help = True
                    return None
                if self.btn_quit.collidepoint(mx, my):
                    return "quit"
            else:
                # 启动界面
                if self.btn_start.collidepoint(mx, my):
                    self.done = True
                    return "start"
                if self.btn_load_start.collidepoint(mx, my):
                    self.show_load = True
                    return None
                if self.btn_help_start.collidepoint(mx, my):
                    self.show_help = True
                    return None
                if self.btn_quit_start.collidepoint(mx, my):
                    return "quit"
        elif event.type == pygame.KEYDOWN:
            if self.can_continue:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
            else:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
        return None

    def _handle_save_event(self, event):
        """处理存档界面事件"""
        if self.confirm_delete is not None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    return None
                mx, my = event.pos
                if self.btn_confirm_yes.collidepoint(mx, my):
                    delete_game(self.confirm_delete)
                    self.confirm_delete = None
                elif self.btn_confirm_no.collidepoint(mx, my):
                    self.confirm_delete = None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN, pygame.K_SPACE):
                    delete_game(self.confirm_delete)
                    self.confirm_delete = None
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.confirm_delete = None
            return None

        saves = get_all_saves()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                return None
            mx, my = event.pos
            for i in range(3):
                slot = i + 1
                if self.slots[i]["action"].collidepoint(mx, my):
                    if slot in saves:
                        self.confirm_delete = slot
                    else:
                        # 保存到此槽位
                        return {"action": "save", "slot": slot}
                elif slot in saves and self.slots[i]["delete"].collidepoint(mx, my):
                    self.confirm_delete = slot
            if self.btn_back.collidepoint(mx, my):
                self.show_save = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_save = False
            elif event.key in (pygame.K_1, pygame.K_KP1):
                if 1 not in saves:
                    return {"action": "save", "slot": 1}
            elif event.key in (pygame.K_2, pygame.K_KP2):
                if 2 not in saves:
                    return {"action": "save", "slot": 2}
            elif event.key in (pygame.K_3, pygame.K_KP3):
                if 3 not in saves:
                    return {"action": "save", "slot": 3}

        return None

    def _handle_load_event(self, event):
        """处理读档界面事件"""
        if self.confirm_delete is not None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (4, 5):
                    return None
                mx, my = event.pos
                if self.btn_confirm_yes.collidepoint(mx, my):
                    delete_game(self.confirm_delete)
                    self.confirm_delete = None
                elif self.btn_confirm_no.collidepoint(mx, my):
                    self.confirm_delete = None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN, pygame.K_SPACE):
                    delete_game(self.confirm_delete)
                    self.confirm_delete = None
                elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.confirm_delete = None
            return None

        saves = get_all_saves()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                return None
            mx, my = event.pos
            for i in range(3):
                slot = i + 1
                if slot in saves:
                    if self.slots[i]["action"].collidepoint(mx, my):
                        self.done = True
                        return {"action": "load", "slot": slot}
                    elif self.slots[i]["delete"].collidepoint(mx, my):
                        self.confirm_delete = slot
                else:
                    if self.slots[i]["action"].collidepoint(mx, my):
                        return {"action": "save", "slot": slot}
            if self.btn_back.collidepoint(mx, my):
                self.show_load = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_load = False
            elif event.key in (pygame.K_1, pygame.K_KP1):
                if 1 in saves:
                    self.done = True
                    return {"action": "load", "slot": 1}
                else:
                    return {"action": "save", "slot": 1}
            elif event.key in (pygame.K_2, pygame.K_KP2):
                if 2 in saves:
                    self.done = True
                    return {"action": "load", "slot": 2}
                else:
                    return {"action": "save", "slot": 2}
            elif event.key in (pygame.K_3, pygame.K_KP3):
                if 3 in saves:
                    self.done = True
                    return {"action": "load", "slot": 3}
                else:
                    return {"action": "save", "slot": 3}

        return None

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        if self.show_help:
            self._draw_help(screen)
            return

        if self.show_save:
            self._draw_save(screen)
            return

        if self.show_load:
            self._draw_load(screen)
            return

        title = self.font.render("西游记 - 祸起观音院", True, GOLD)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 150))

        subtitle = self.small_font.render("RPG冒险游戏", True, WHITE)
        sub_x = SCREEN_WIDTH // 2 - subtitle.get_width() // 2
        screen.blit(subtitle, (sub_x, 220))

        if self.can_continue:
            # 游戏中菜单
            # 继续游戏
            pygame.draw.rect(screen, (50, 150, 50), self.btn_continue)
            pygame.draw.rect(screen, WHITE, self.btn_continue, 2)
            btn_text = self.small_font.render("继续游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_continue.centerx - btn_text.get_width() // 2,
                                   self.btn_continue.centery - btn_text.get_height() // 2))

            # 返回村庄（仅在寺庙场景时显示）
            if self.show_return_village:
                pygame.draw.rect(screen, (150, 120, 50), self.btn_return_village)
                pygame.draw.rect(screen, WHITE, self.btn_return_village, 2)
                btn_text = self.small_font.render("返回村庄", True, WHITE)
                screen.blit(btn_text, (self.btn_return_village.centerx - btn_text.get_width() // 2,
                                       self.btn_return_village.centery - btn_text.get_height() // 2))

            # 读取存档
            pygame.draw.rect(screen, (80, 80, 130), self.btn_load)
            pygame.draw.rect(screen, WHITE, self.btn_load, 2)
            btn_text = self.small_font.render("读取存档", True, WHITE)
            screen.blit(btn_text, (self.btn_load.centerx - btn_text.get_width() // 2,
                                   self.btn_load.centery - btn_text.get_height() // 2))

            # 游戏介绍
            pygame.draw.rect(screen, (100, 80, 120), self.btn_help)
            pygame.draw.rect(screen, WHITE, self.btn_help, 2)
            btn_text = self.small_font.render("游戏介绍", True, WHITE)
            screen.blit(btn_text, (self.btn_help.centerx - btn_text.get_width() // 2,
                                   self.btn_help.centery - btn_text.get_height() // 2))

            # 退出游戏
            pygame.draw.rect(screen, (150, 50, 50), self.btn_quit)
            pygame.draw.rect(screen, WHITE, self.btn_quit, 2)
            btn_text = self.small_font.render("退出游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_quit.centerx - btn_text.get_width() // 2,
                                   self.btn_quit.centery - btn_text.get_height() // 2))

            hint = self.small_font.render("ESC 继续游戏", True, WHITE)
        else:
            # 启动界面
            # 开始游戏
            pygame.draw.rect(screen, (50, 150, 50), self.btn_start)
            pygame.draw.rect(screen, WHITE, self.btn_start, 2)
            btn_text = self.small_font.render("开始游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_start.centerx - btn_text.get_width() // 2,
                                   self.btn_start.centery - btn_text.get_height() // 2))

            # 读取存档
            pygame.draw.rect(screen, (50, 100, 150), self.btn_load_start)
            pygame.draw.rect(screen, WHITE, self.btn_load_start, 2)
            btn_text = self.small_font.render("读取存档", True, WHITE)
            screen.blit(btn_text, (self.btn_load_start.centerx - btn_text.get_width() // 2,
                                   self.btn_load_start.centery - btn_text.get_height() // 2))

            # 游戏介绍
            pygame.draw.rect(screen, (100, 80, 120), self.btn_help_start)
            pygame.draw.rect(screen, WHITE, self.btn_help_start, 2)
            btn_text = self.small_font.render("游戏介绍", True, WHITE)
            screen.blit(btn_text, (self.btn_help_start.centerx - btn_text.get_width() // 2,
                                   self.btn_help_start.centery - btn_text.get_height() // 2))

            # 退出游戏
            pygame.draw.rect(screen, (150, 50, 50), self.btn_quit_start)
            pygame.draw.rect(screen, WHITE, self.btn_quit_start, 2)
            btn_text = self.small_font.render("退出游戏", True, WHITE)
            screen.blit(btn_text, (self.btn_quit_start.centerx - btn_text.get_width() // 2,
                                   self.btn_quit_start.centery - btn_text.get_height() // 2))

            hint = self.small_font.render("ESC退出", True, WHITE)

        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        screen.blit(hint, (hint_x, 10))

        # 存档提示
        if self.save_msg_timer > 0:
            self.save_msg_timer -= 1
            msg_surface = self.help_font.render(self.save_msg, True, (255, 255, 255))
            msg_x = SCREEN_WIDTH // 2 - msg_surface.get_width() // 2
            msg_y = 50
            bg_surface = pygame.Surface((msg_surface.get_width() + 20, msg_surface.get_height() + 10), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))
            screen.blit(bg_surface, (msg_x - 10, msg_y - 5))
            screen.blit(msg_surface, (msg_x, msg_y))

    def _draw_save(self, screen):
        """绘制存档界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = self.font.render("存档", True, GOLD)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 50))

        hint = self.help_font.render("按数字键1/2/3快速存档 | 点击空槽位保存 | 已有存档点击可覆盖（先删后存）", True, (180, 180, 180))
        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        screen.blit(hint, (hint_x, 110))

        saves = get_all_saves()

        for i in range(3):
            slot = i + 1
            y = 180 + i * 120

            slot_text = self.small_font.render(f"存档 {slot}", True, YELLOW)
            screen.blit(slot_text, (50, y))

            if slot in saves:
                data = saves[slot]
                state = data.get("state", {})
                timestamp = data.get("timestamp", "未知")
                scene_name = "村庄" if state.get("current_state") == 0 else "寺庙"
                hp = state.get("player_hp", 0)
                max_hp = state.get("player_max_hp", 0)

                info_text = self.help_font.render(
                    f"{timestamp} | {scene_name} | HP:{hp}/{max_hp}", True, WHITE)
                screen.blit(info_text, (50, y + 35))

                # 覆盖按钮
                pygame.draw.rect(screen, (50, 150, 50), self.slots[i]["action"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["action"], 2)
                btn_text = self.help_font.render("覆盖存档", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["action"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["action"].centery - btn_text.get_height() // 2))

                # 删档按钮
                pygame.draw.rect(screen, (150, 50, 50), self.slots[i]["delete"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["delete"], 2)
                btn_text = self.help_font.render("删档", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["delete"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["delete"].centery - btn_text.get_height() // 2))
            else:
                empty_text = self.help_font.render("—— 空 ——", True, (120, 120, 120))
                screen.blit(empty_text, (50, y + 35))

                # 保存按钮
                pygame.draw.rect(screen, (50, 150, 50), self.slots[i]["action"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["action"], 2)
                btn_text = self.help_font.render("保存到此", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["action"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["action"].centery - btn_text.get_height() // 2))

        # 返回按钮
        pygame.draw.rect(screen, (100, 100, 100), self.btn_back)
        pygame.draw.rect(screen, WHITE, self.btn_back, 2)
        btn_text = self.small_font.render("返回", True, WHITE)
        screen.blit(btn_text, (self.btn_back.centerx - btn_text.get_width() // 2,
                               self.btn_back.centery - btn_text.get_height() // 2))

        # 删除确认对话框
        if self.confirm_delete is not None:
            confirm_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            confirm_overlay.fill((0, 0, 0, 150))
            screen.blit(confirm_overlay, (0, 0))

            box = pygame.Rect(SCREEN_WIDTH // 2 - 160, 320, 320, 140)
            pygame.draw.rect(screen, (40, 40, 40), box)
            pygame.draw.rect(screen, WHITE, box, 2)

            confirm_text = self.small_font.render(f"确认删除存档 {self.confirm_delete}？", True, WHITE)
            screen.blit(confirm_text, (SCREEN_WIDTH // 2 - confirm_text.get_width() // 2, 340))

            pygame.draw.rect(screen, (50, 150, 50), self.btn_confirm_yes)
            pygame.draw.rect(screen, WHITE, self.btn_confirm_yes, 2)
            yes_text = self.help_font.render("是(Y)", True, WHITE)
            screen.blit(yes_text, (self.btn_confirm_yes.centerx - yes_text.get_width() // 2,
                                   self.btn_confirm_yes.centery - yes_text.get_height() // 2))

            pygame.draw.rect(screen, (150, 50, 50), self.btn_confirm_no)
            pygame.draw.rect(screen, WHITE, self.btn_confirm_no, 2)
            no_text = self.help_font.render("否(N)", True, WHITE)
            screen.blit(no_text, (self.btn_confirm_no.centerx - no_text.get_width() // 2,
                                  self.btn_confirm_no.centery - no_text.get_height() // 2))

    def _draw_load(self, screen):
        """绘制读档界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = self.font.render("读取存档", True, GOLD)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 50))

        hint = self.help_font.render("点击空槽位可保存 | 点击「进入游戏」读取 | 点击「删档」后按Y确认", True, (180, 180, 180))
        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        screen.blit(hint, (hint_x, 110))

        saves = get_all_saves()

        for i in range(3):
            slot = i + 1
            y = 180 + i * 120

            slot_text = self.small_font.render(f"存档 {slot}", True, YELLOW)
            screen.blit(slot_text, (50, y))

            if slot in saves:
                data = saves[slot]
                state = data.get("state", {})
                timestamp = data.get("timestamp", "未知")
                scene_name = "村庄" if state.get("current_state") == 0 else "寺庙"
                hp = state.get("player_hp", 0)
                max_hp = state.get("player_max_hp", 0)

                info_text = self.help_font.render(
                    f"{timestamp} | {scene_name} | HP:{hp}/{max_hp}", True, WHITE)
                screen.blit(info_text, (50, y + 35))

                # 加载按钮
                pygame.draw.rect(screen, (50, 150, 50), self.slots[i]["action"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["action"], 2)
                btn_text = self.help_font.render("进入游戏", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["action"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["action"].centery - btn_text.get_height() // 2))

                # 删档按钮
                pygame.draw.rect(screen, (150, 50, 50), self.slots[i]["delete"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["delete"], 2)
                btn_text = self.help_font.render("删档", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["delete"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["delete"].centery - btn_text.get_height() // 2))
            else:
                empty_text = self.help_font.render("—— 空 ——", True, (120, 120, 120))
                screen.blit(empty_text, (50, y + 35))

                # 保存按钮
                pygame.draw.rect(screen, (50, 150, 50), self.slots[i]["action"])
                pygame.draw.rect(screen, WHITE, self.slots[i]["action"], 2)
                btn_text = self.help_font.render("保存到此", True, WHITE)
                screen.blit(btn_text, (self.slots[i]["action"].centerx - btn_text.get_width() // 2,
                                       self.slots[i]["action"].centery - btn_text.get_height() // 2))

        # 返回按钮
        pygame.draw.rect(screen, (100, 100, 100), self.btn_back)
        pygame.draw.rect(screen, WHITE, self.btn_back, 2)
        btn_text = self.small_font.render("返回", True, WHITE)
        screen.blit(btn_text, (self.btn_back.centerx - btn_text.get_width() // 2,
                               self.btn_back.centery - btn_text.get_height() // 2))

        # 删除确认对话框
        if self.confirm_delete is not None:
            confirm_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            confirm_overlay.fill((0, 0, 0, 150))
            screen.blit(confirm_overlay, (0, 0))

            box = pygame.Rect(SCREEN_WIDTH // 2 - 160, 320, 320, 140)
            pygame.draw.rect(screen, (40, 40, 40), box)
            pygame.draw.rect(screen, WHITE, box, 2)

            confirm_text = self.small_font.render(f"确认删除存档 {self.confirm_delete}？", True, WHITE)
            screen.blit(confirm_text, (SCREEN_WIDTH // 2 - confirm_text.get_width() // 2, 340))

            pygame.draw.rect(screen, (50, 150, 50), self.btn_confirm_yes)
            pygame.draw.rect(screen, WHITE, self.btn_confirm_yes, 2)
            yes_text = self.help_font.render("是(Y)", True, WHITE)
            screen.blit(yes_text, (self.btn_confirm_yes.centerx - yes_text.get_width() // 2,
                                   self.btn_confirm_yes.centery - yes_text.get_height() // 2))

            pygame.draw.rect(screen, (150, 50, 50), self.btn_confirm_no)
            pygame.draw.rect(screen, WHITE, self.btn_confirm_no, 2)
            no_text = self.help_font.render("否(N)", True, WHITE)
            screen.blit(no_text, (self.btn_confirm_no.centerx - no_text.get_width() // 2,
                                  self.btn_confirm_no.centery - no_text.get_height() // 2))

    def _draw_help(self, screen):
        """绘制游戏介绍界面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = self.font.render("游戏介绍", True, GOLD)
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        screen.blit(title, (title_x, 30))

        y = 100 - self.scroll_offset
        intro_lines = [
            "《西游记：祸起观音院》是一款基于Pygame开发的2D RPG游戏",
            "以中国古典名著《西游记》为背景，扮演孙悟空降妖除魔",
        ]
        for line in intro_lines:
            if 80 < y < SCREEN_HEIGHT - 80:
                text = self.help_font.render(line, True, WHITE)
                screen.blit(text, (50, y))
            y += 30

        y += 20
        if 80 < y < SCREEN_HEIGHT - 80:
            section_title = self.small_font.render("操作说明", True, YELLOW)
            screen.blit(section_title, (50, y))
        y += 40

        controls = [
            ("移动控制", [
                "方向键 或 W/A/S/D：控制角色移动",
                "Shift键：加速移动",
            ]),
            ("交互操作", [
                "空格/回车键：关闭对话框、确认选择",
                "ESC键：打开菜单（存档/读档/继续）",
            ]),
            ("战斗操作", [
                "点击「普攻」按钮：普通攻击",
                "点击「金箍棒」按钮：技能攻击",
                "点击「七十二变」按钮：大招攻击（需解锁）",
                "数字键 1/2/3：对应三种攻击方式",
            ]),
        ]

        for section, items in controls:
            if 80 < y < SCREEN_HEIGHT - 80:
                section_text = self.help_font.render(f"【{section}】", True, GREEN)
                screen.blit(section_text, (50, y))
            y += 28
            for item in items:
                if 80 < y < SCREEN_HEIGHT - 80:
                    item_text = self.help_font.render(f"  · {item}", True, WHITE)
                    screen.blit(item_text, (50, y))
                y += 25
            y += 10

        y += 5
        if 80 < y < SCREEN_HEIGHT - 80:
            section_title = self.small_font.render("游戏流程", True, YELLOW)
            screen.blit(section_title, (50, y))
        y += 40

        flow = [
            "1. 在村庄与NPC对话，了解剧情",
            "2. 前往寺庙，击败三只小怪（M1-M3）",
            "3. 击败所有小怪后，BOSS牛魔王才会出现",
            "4. 击败牛魔王即可通关",
        ]
        for item in flow:
            if 80 < y < SCREEN_HEIGHT - 80:
                item_text = self.help_font.render(f"  · {item}", True, WHITE)
                screen.blit(item_text, (50, y))
            y += 25

        pygame.draw.rect(screen, (100, 100, 100), self.btn_back)
        pygame.draw.rect(screen, WHITE, self.btn_back, 2)
        btn_text = self.small_font.render("返回", True, WHITE)
        screen.blit(btn_text, (self.btn_back.centerx - btn_text.get_width() // 2,
                               self.btn_back.centery - btn_text.get_height() // 2))
