import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCE_DIR = os.path.join(BASE_DIR, 'resource')

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

FONT_PATH = os.path.join(RESOURCE_DIR, 'font', 'newfont.TTF')
FONT_SIZE = 20

VILLAGE_MAP = os.path.join(RESOURCE_DIR, 'tmx', 'village.tmx')
TEMPLE_MAP = os.path.join(RESOURCE_DIR, 'tmx', 'temple.tmx')

IMG_DIR = os.path.join(RESOURCE_DIR, 'img')
SOUND_DIR = os.path.join(RESOURCE_DIR, 'sound')

PLAYER_SPEED = 3
NPC_SPEED = 1
MONSTER_SPEED = 2

DOWN = 0
LEFT = 1
UP = 2
RIGHT = 3

ANIM_SPEED = 150

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
