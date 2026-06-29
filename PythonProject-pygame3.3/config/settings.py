import os

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
TITLE = "西游记 - 祸起观音院"

# 资源路径（使用相对路径）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCE_PATH = os.path.join(BASE_DIR, "resources")
IMG_PATH = os.path.join(RESOURCE_PATH, "img")
SOUND_PATH = os.path.join(RESOURCE_PATH, "sound")
TMX_PATH = os.path.join(RESOURCE_PATH, "tmx")
FONT_PATH = os.path.join(RESOURCE_PATH, "font", "newfont.TTF")

# 图片路径
VILLAGE_IMG = os.path.join(IMG_PATH, "village.jpg")
TEMPLE_IMG = os.path.join(IMG_PATH, "temple.jpg")
DIALOG_IMG = os.path.join(IMG_PATH, "dialog", "dialog.png")
WIN_IMG = os.path.join(IMG_PATH, "win.jpg")
FAIL_IMG = os.path.join(IMG_PATH, "fail.jpg")

# 地图路径
VILLAGE_TMX = os.path.join(TMX_PATH, "village1.tmx")
TEMPLE_TMX = os.path.join(TMX_PATH, "temple1.tmx")

# 音频路径
BGM_VILLAGE = os.path.join(SOUND_PATH, "nmw.mp3")
BGM_TEMPLE = os.path.join(SOUND_PATH, "aigei.mp3")
SOUND_SWK = os.path.join(SOUND_PATH, "swk.wav")

# 玩家设置
PLAYER_SPEED = 6
PLAYER_ANIM_SPEED = 8
PLAYER_BASE_HP = 100
PLAYER_BASE_ATK = 25

# NPC设置
NPC_SPEED = 1
NPC_ANIM_SPEED = 10
NPC_WALK_STEPS = 60

# 战斗设置
NORMAL_ATK_DAMAGE = 25       # 普攻伤害
SKILL_ATK_DAMAGE = 60        # 技能伤害
ULTIMATE_ATK_DAMAGE = 100    # 大招伤害

MONSTER_HP = 100
MONSTER_ATK = 15
BOSS_HP = 250
BOSS_ATK = 30

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (160, 32, 240)
GOLD = (255, 215, 0)

# 场景状态
SCENE_IN = 1
SCENE_NORMAL = 2
SCENE_OUT = 3

# 小地图设置
MINIMAP_WIDTH = 180               # 小地图内框宽度（固定）
MINIMAP_HEIGHT = 140              # 小地图内框高度（固定）
MINIMAP_MARGIN = 10               # 距屏幕边缘的间距
MINIMAP_BASE_COLOR = (30, 30, 30)  # 底板填充色（背景图未覆盖区域）
MINIMAP_BORDER_COLOR = (200, 200, 200)  # 边框颜色
MINIMAP_BORDER_WIDTH = 2          # 边框宽度（像素）

# 小地图阴影
MINIMAP_SHADOW_COLOR = (0, 0, 0)        # 阴影颜色
MINIMAP_SHADOW_OFFSET = 3               # 阴影偏移量
MINIMAP_SHADOW_BLUR = 6                 # 阴影模糊层数

# 视窗指示器
MINIMAP_VIEW_COLOR = (255, 255, 255)  # 视窗范围框颜色
MINIMAP_VIEW_ALPHA = 80               # 视窗范围框透明度

# 玩家标记（黄色）
MINIMAP_PLAYER_COLOR = (255, 220, 50)  # 玩家标记颜色
MINIMAP_PLAYER_SIZE = 6               # 玩家标记半径（原3 * 2）

# 怪物标记（红色）
MINIMAP_MONSTER_COLOR = (230, 60, 60)  # 怪物标记颜色
MINIMAP_MONSTER_SIZE = 5               # 普通怪物半径（原3 * 1.5）
MINIMAP_BOSS_SIZE = 6                  # BOSS标记半径（原3 * 2）

# NPC标记（绿色）
MINIMAP_NPC_COLOR = (50, 200, 50)    # NPC标记颜色
MINIMAP_NPC_SIZE = 5                  # NPC标记半径（原3 * 1.5）
