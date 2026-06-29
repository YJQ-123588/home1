import pygame
import os
import glob


class Animation:
    """帧动画管理类"""

    def __init__(self, frames=None, speed=8):
        """
        Args:
            frames: 帧图像列表 [Surface, ...]
            speed: 帧切换速度（每隔多少帧切换一次，越大越慢）
        """
        self.frames = frames if frames else []
        self.speed = speed
        self.index = 0
        self.timer = 0

    def update(self):
        """更新动画帧"""
        if not self.frames:
            return
        self.timer += 1
        if self.timer >= self.speed:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)

    def get_current_frame(self):
        """获取当前帧图像"""
        if not self.frames:
            return None
        return self.frames[self.index]

    def reset(self):
        """重置动画"""
        self.index = 0
        self.timer = 0

    def set_frames(self, frames):
        """设置新的帧列表"""
        if frames and (len(frames) != len(self.frames) or
                       (frames and self.frames and frames[0] is not self.frames[0])):
            self.frames = frames
            self.index = 0
            self.timer = 0
        elif frames:
            self.frames = frames


def load_frames(file_pattern, colorkey=None):
    """
    加载帧图像列表

    Args:
        file_pattern: 文件路径模式，如 'path/to/*.tga'
        colorkey: 透明色颜色键

    Returns:
        帧图像Surface列表
    """
    frames = []
    files = sorted(glob.glob(file_pattern))
    for f in files:
        try:
            img = pygame.image.load(f).convert()
            if colorkey is not None:
                img.set_colorkey(colorkey)
            frames.append(img)
        except Exception as e:
            print(f"加载图片失败: {f}, {e}")
    return frames


def load_swk_frames(img_path, colorkey=(0, 0, 0)):
    """
    加载孙悟空4方向行走动画帧

    SWK文件命名: 00=下, 01=左, 02=上, 03=右
    每方向4帧: XX000.tga ~ XX003.tga

    Returns:
        dict: {direction: [frame1, frame2, frame3, frame4]}
              direction: 0=down, 1=left, 2=up, 3=right
    """
    swk_path = os.path.join(img_path, "swk")
    directions = {0: [], 1: [], 2: [], 3: []}
    dir_map = {'00': 0, '01': 1, '02': 2, '03': 3}

    files = sorted(os.listdir(swk_path))
    for f in files:
        if f.endswith('.tga'):
            prefix = f[:2]
            if prefix in dir_map:
                d = dir_map[prefix]
                img = pygame.image.load(os.path.join(swk_path, f)).convert()
                if colorkey is not None:
                    img.set_colorkey(colorkey)
                directions[d].append(img)

    return directions


def load_cattle_frames(img_path, state='walk1', colorkey=None):
    """
    加载牛妖动画帧

    Cattle文件命名: 00=下, 01=左, 02=上, 03=右 (前两位数字为方向)

    Returns:
        dict: {direction: [frames]}
    """
    cattle_path = os.path.join(img_path, "cattle", state)
    directions = {0: [], 1: [], 2: [], 3: []}

    if not os.path.exists(cattle_path):
        return directions

    files = sorted(os.listdir(cattle_path))
    for f in files:
        if f.endswith('.tga'):
            # 文件名格式: 1252-7f2abf21-DDYYY.tga
            # DD = 方向(00-03), YYY = 帧序号
            parts = f.replace('.tga', '').split('-')
            if len(parts) >= 3:
                num_part = parts[2]
                if len(num_part) >= 5:
                    d = int(num_part[:2])
                    if d in directions:
                        img = pygame.image.load(os.path.join(cattle_path, f)).convert()
                        if colorkey is not None:
                            img.set_colorkey(colorkey)
                        directions[d].append(img)

    return directions


def load_god_frames(img_path, colorkey=None):
    """
    加载土地公动画帧

    文件命名: 前两位数字为方向 (00=下, 01=左, 02=上, 03=右)

    Returns:
        dict: {direction: [frames]}
    """
    god_path = os.path.join(img_path, "god")
    directions = {0: [], 1: [], 2: [], 3: []}

    if not os.path.exists(god_path):
        return directions

    files = sorted(os.listdir(god_path))
    for f in files:
        if f.endswith('.tga'):
            parts = f.replace('.tga', '').split('-')
            if len(parts) >= 3:
                num_part = parts[2]
                if len(num_part) >= 5:
                    d = int(num_part[:2])
                    if d in directions:
                        img = pygame.image.load(os.path.join(god_path, f)).convert()
                        if colorkey is not None:
                            img.set_colorkey(colorkey)
                        directions[d].append(img)

    return directions


def load_elder_frames(img_path, elder_id=1, colorkey=None):
    """
    加载长老动画帧

    Args:
        elder_id: 长老编号 1-4

    Returns:
        list: 帧列表
    """
    elder_path = os.path.join(img_path, "elder")
    frames = []

    if not os.path.exists(elder_path):
        return frames

    files = sorted(os.listdir(elder_path))
    for f in files:
        if f.endswith('.tga') and f.startswith(f'elder{elder_id}'):
            img = pygame.image.load(os.path.join(elder_path, f)).convert()
            if colorkey is not None:
                img.set_colorkey(colorkey)
            frames.append(img)

    return frames


def load_swk2_frames(img_path, colorkey=None):
    """
    加载孙悟空战斗动画帧 (swk2目录，128帧png)

    Returns:
        list: 帧列表
    """
    swk2_path = os.path.join(img_path, "swk2")
    pattern = os.path.join(swk2_path, "*.png")
    return load_frames(pattern, colorkey)


def load_magic_frames(img_path, state='appear', colorkey=None):
    """
    加载魔法特效帧

    Args:
        state: 'appear' 或 'disappear'

    Returns:
        list: 帧列表
    """
    magic_path = os.path.join(img_path, "magic", state)
    pattern = os.path.join(magic_path, "*.tga")
    return load_frames(pattern, colorkey)


def load_cattle_die_frames(img_path, colorkey=None):
    """
    加载牛妖死亡动画帧
    
    使用方向1（左）的帧：0762-4cbbea5a-01000.tga 到 0762-4cbbea5a-01010.tga

    Returns:
        list: 帧列表（11帧）
    """
    die_path = os.path.join(img_path, "cattle", "die")
    frames = []
    
    if not os.path.exists(die_path):
        return frames
    
    # 加载方向1（左）的帧：01000-01010
    for i in range(11):
        filename = f"0762-4cbbea5a-01{i:03d}.tga"
        filepath = os.path.join(die_path, filename)
        if os.path.exists(filepath):
            try:
                img = pygame.image.load(filepath).convert()
                if colorkey is not None:
                    img.set_colorkey(colorkey)
                frames.append(img)
            except Exception as e:
                print(f"加载死亡动画帧失败: {filepath}, {e}")
    
    return frames
