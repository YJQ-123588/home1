import pygame
from config.settings import NPC_SPEED, NPC_ANIM_SPEED, NPC_WALK_STEPS
from core.animation import (Animation, load_god_frames, load_elder_frames,
                             load_cattle_frames)


class NPC(pygame.sprite.Sprite):
    """NPC基类"""

    DOWN = 0
    LEFT = 1
    UP = 2
    RIGHT = 3

    def __init__(self, x, y, anim_frames, speed=NPC_SPEED, target_size=(80, 100)):
        super().__init__()
        self.target_size = target_size
        self.direction_frames = anim_frames
        self.direction = self.DOWN
        self.anim = Animation(self.direction_frames.get(self.DOWN, []),
                              NPC_ANIM_SPEED)

        self.image = self.anim.get_current_frame()
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x - 40, y - 50, 80, 100)

        self.map_x = float(x)
        self.map_y = float(y)
        self.speed = speed
        self.spawn_x = float(x)
        self.spawn_y = float(y)

        self.walk_timer = 0
        self.walk_steps = NPC_WALK_STEPS
        self.moving = False
        self.paused = False

    def wander(self):
        """徘徊运动"""
        if self.paused:
            self.moving = False
            return

        self.walk_timer += 1
        if self.walk_timer >= self.walk_steps:
            self.walk_timer = 0
            if self.direction in (self.DOWN, self.LEFT):
                self.direction = self.UP
            else:
                self.direction = self.DOWN

        dx, dy = 0, 0
        if self.direction == self.DOWN:
            dy = self.speed
        elif self.direction == self.UP:
            dy = -self.speed
        elif self.direction == self.LEFT:
            dx = -self.speed
        elif self.direction == self.RIGHT:
            dx = self.speed

        self.map_x += dx
        self.map_y += dy
        self.moving = True

    def update(self):
        self.wander()
        frames = self.direction_frames.get(self.direction, [])
        self.anim.set_frames(frames)
        if self.moving:
            self.anim.update()
        self.image = self.anim.get_current_frame()
        if self.image:
            self.rect.center = (int(self.map_x), int(self.map_y))

    def face_toward(self, target_x, target_y):
        dx = target_x - self.map_x
        dy = target_y - self.map_y
        if abs(dx) > abs(dy):
            self.direction = self.RIGHT if dx > 0 else self.LEFT
        else:
            self.direction = self.DOWN if dy > 0 else self.UP

    def draw(self, surface, offset_x=0, offset_y=0):
        if self.image:
            draw_x = self.rect.x - offset_x
            draw_y = self.rect.y - offset_y
            surface.blit(self.image, (draw_x, draw_y))


# ============================================================
# 土地公 — 引导NPC，带救援对话
# ============================================================
class God(NPC):
    """土地公NPC"""

    def __init__(self, img_path, x, y):
        frames = load_god_frames(img_path, colorkey=(0, 0, 0))
        target_size = (80, 100)
        for d in frames:
            frames[d] = [pygame.transform.scale(f, target_size) for f in frames[d]]
        super().__init__(x, y, frames, speed=1, target_size=target_size)
        self.name = "土地公"
        self.rescued = False
        self.talk_cooldown = 0
        self.wander_range = 80  # 小范围徘徊

    def wander(self):
        """小范围徘徊"""
        if self.paused:
            self.moving = False
            return

        self.walk_timer += 1
        if self.walk_timer >= self.walk_steps:
            self.walk_timer = 0
            if self.direction in (self.DOWN, self.LEFT):
                self.direction = self.UP
            else:
                self.direction = self.DOWN

        dx, dy = 0, 0
        if self.direction == self.DOWN:
            dy = self.speed
        elif self.direction == self.UP:
            dy = -self.speed
        elif self.direction == self.LEFT:
            dx = -self.speed
        elif self.direction == self.RIGHT:
            dx = self.speed

        # 限制在出生点附近小范围
        new_x = self.map_x + dx
        new_y = self.map_y + dy
        if abs(new_x - self.spawn_x) <= self.wander_range:
            self.map_x = new_x
        if abs(new_y - self.spawn_y) <= self.wander_range:
            self.map_y = new_y
        self.moving = True

    def update(self):
        if self.paused:
            return
        if self.talk_cooldown > 0:
            self.talk_cooldown -= 1
        self.wander()
        frames = self.direction_frames.get(self.direction, [])
        self.anim.set_frames(frames)
        if self.moving:
            self.anim.update()
        self.image = self.anim.get_current_frame()
        if self.image:
            self.rect.center = (int(self.map_x), int(self.map_y))

    def talk(self):
        if not self.rescued:
            return "大圣，前方观音院有妖怪作祟，请随我来！"
        else:
            return "大圣，妖怪法力高强，你去找村中的长老相助吧！"

    def rescue_talk(self):
        """救援后的对话（自动触发）"""
        self.rescued = True
        return "土地公将你悄悄救回了村庄...\n大圣，那妖怪厉害，快去寻村中长老帮忙！"

    def can_talk(self):
        return self.talk_cooldown <= 0


# ============================================================
# 农民 — 普通NPC，提供村庄信息
# ============================================================
class Farmer(NPC):
    """农民NPC"""

    def __init__(self, img_path, x, y, farmer_id=1):
        self.farmer_id = farmer_id
        farmer_frames = load_elder_frames(img_path, 1, colorkey=(0, 0, 0))
        target_size = (70, 90)
        farmer_frames = [pygame.transform.scale(f, target_size) for f in farmer_frames]
        frames = {0: farmer_frames, 1: farmer_frames,
                  2: farmer_frames, 3: farmer_frames}
        super().__init__(x, y, frames, speed=1, target_size=target_size)
        self.name = f"村民{farmer_id}"
        self.dialog_index = 0
        self.talk_cooldown = 0

    def _get_dialogs(self):
        dialogs = {
            1: ["村民：听说山上的寺庙里有妖怪出没...",
                "村民：大圣若能除去妖怪，我们感恩不尽！"],
            2: ["村民：近来妖怪常下山骚扰，苦不堪言。",
                "村民：村中长老或许有办法帮助大圣。"],
            3: ["村民：大圣小心，那妖怪可不是好惹的！",
                "村民：之前也有人想去，都没回来..."],
        }
        return dialogs.get(self.farmer_id, ["村民：大圣好！"])

    def update(self):
        if self.talk_cooldown > 0:
            self.talk_cooldown -= 1
        super().update()

    def talk(self):
        texts = self._get_dialogs()
        text = texts[self.dialog_index % len(texts)]
        self.dialog_index += 1
        self.talk_cooldown = 90
        return text

    def can_talk(self):
        return self.talk_cooldown <= 0


# ============================================================
# 长老 — 提供增益（生命值/大招）
# ============================================================
class Elder(NPC):
    """长老NPC — 提供增益，固定不移动"""

    def __init__(self, img_path, x, y, elder_id=1):
        self.elder_id = elder_id
        elder_frames = load_elder_frames(img_path, elder_id, colorkey=(0, 0, 0))
        target_size = (80, 100)
        elder_frames = [pygame.transform.scale(f, target_size) for f in elder_frames]
        frames = {0: elder_frames, 1: elder_frames,
                  2: elder_frames, 3: elder_frames}
        super().__init__(x, y, frames, speed=0, target_size=target_size)
        self.name = f"长老{elder_id}"
        self.talk_cooldown = 0
        self.upgrade_given = False  # 是否已给出增益

    def update(self):
        if self.talk_cooldown > 0:
            self.talk_cooldown -= 1
        if self.paused:
            return
        frames = self.direction_frames.get(self.direction, [])
        self.anim.set_frames(frames)
        self.anim.update()
        self.image = self.anim.get_current_frame()
        if self.image:
            self.rect.center = (int(self.map_x), int(self.map_y))

    def talk(self):
        """返回对话，长老1加血量，长老2放大招，长老3回血"""
        self.talk_cooldown = 90
        if self.elder_id == 1:
            if not self.upgrade_given:
                self.upgrade_given = True
                return "长老：大圣，老衲传你护体神功，可增生命之力！\n（生命值上限 +50）"
            else:
                return "长老：护体神功已传，大圣多加小心。"
        elif self.elder_id == 2:
            if not self.upgrade_given:
                self.upgrade_given = True
                return "长老：大圣，老衲教你一招「七十二变」，危急时可用！\n（已解锁大招，战斗中按3使用）"
            else:
                return "长老：七十二变已授，善用之。"
        elif self.elder_id == 3:
            self.upgrade_given = True
            return "长老：大圣，让老衲为你疗伤！\n（生命值已完全恢复）"
        return "长老：阿弥陀佛。"

    def get_upgrade_type(self):
        """获取增益类型"""
        if self.elder_id == 1:
            return "hp_boost"
        elif self.elder_id == 2:
            return "ultimate"
        elif self.elder_id == 3:
            return "heal"
        return None

    def can_talk(self):
        return self.talk_cooldown <= 0


# ============================================================
# 牛妖 — 战斗怪物
# ============================================================
class Cattle(NPC):
    """牛妖NPC，支持多动画状态"""

    def __init__(self, img_path, x, y, name="牛妖", is_boss=False):
        self.is_boss = is_boss
        npc_size = (120, 150) if is_boss else (80, 100)

        walk_frames = load_cattle_frames(img_path, 'walk1', colorkey=(0, 0, 0))
        station_frames = load_cattle_frames(img_path, 'station', colorkey=(0, 0, 0))
        fight_frames = load_cattle_frames(img_path, 'fight', colorkey=(0, 0, 0))

        for d in walk_frames:
            walk_frames[d] = [pygame.transform.scale(f, npc_size) for f in walk_frames[d]]
        for d in station_frames:
            station_frames[d] = [pygame.transform.scale(f, npc_size) for f in station_frames[d]]
        for d in fight_frames:
            fight_frames[d] = [pygame.transform.scale(f, npc_size) for f in fight_frames[d]]

        self.all_frames = {
            'walk': walk_frames,
            'station': station_frames,
            'fight': fight_frames,
        }
        self.current_state = 'walk'

        super().__init__(x, y, walk_frames, speed=NPC_SPEED, target_size=npc_size)
        self.name = name
        self.hp = 250 if is_boss else 100
        self.attack = 30 if is_boss else 15
        self.alive = True
        if is_boss:
            self.dialog_text = "吾乃此地大王，猴子休得猖狂！"
        else:
            self.dialog_text = "大胆猴子，竟敢闯入此地！"

    def set_state(self, state):
        if state in self.all_frames and state != self.current_state:
            self.current_state = state
            self.direction_frames = self.all_frames[state]
            frames = self.direction_frames.get(self.direction, [])
            self.anim.set_frames(frames)
            self.anim.reset()

    def talk(self):
        return self.dialog_text

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return self.hp
