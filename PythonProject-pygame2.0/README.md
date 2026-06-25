# 西游记观音院 - Pygame RPG 游戏

基于 Pygame 开发的 2D RPG 游戏，故事背景为西游记中祸起观音院，玩家扮演孙悟空找到观音院的过程。

## 运行环境

- Python 3.13+
- Pygame 2.6.1
- PyTMX 3.32

## 安装与运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行游戏
python main.py
```

## 操作说明

| 按键 | 功能 |
|------|------|
| ↑ ↓ ← → | 移动角色 |
| SPACE | 与NPC对话 / 攻击怪物 |
| ESC | 退出游戏 |

## 项目结构

```
PythonProject2-pygame/
├── main.py                 # 游戏入口
├── requirements.txt        # 依赖
├── core/                   # 核心框架
│   ├── game.py             # 游戏引擎（主循环、场景管理）
│   ├── scene.py            # 场景基类 + FadeScene渐入渐出
│   └── settings.py         # 全局配置常量
├── map/
│   └── tmx_map.py          # Tiled地图加载与渲染
├── sprites/                # 精灵模块
│   ├── animation.py        # 动画帧管理
│   ├── player.py           # 玩家类（键盘控制+行走动画）
│   ├── npc.py              # NPC类（徘徊运动+对话）
│   └── monster.py          # 怪物类（战斗系统）
├── scenes/                 # 场景模块
│   ├── village_scene.py    # 村庄场景
│   └── temple_scene.py     # 寺庙场景
├── ui/                     # UI模块
│   └── dialog.py           # 对话框系统
└── resource/               # 游戏资源
    ├── font/               # 字体
    ├── img/                # 图片（角色精灵、背景、UI）
    ├── sound/              # 音效
    └── tmx/                # Tiled地图文件
```

## 已实现功能

### 基础框架（阶段一）
- Pygame 初始化与主循环
- TiledMap 地图加载与渲染
- Animation 精灵动画系统
- FadeScene 渐入渐出场景切换

### 游戏内容（阶段二）
- 玩家键盘控制与 4 方向行走动画
- NPC 徘徊运动与对话触发
- 相机跟随系统（视窗随玩家移动）
- 村庄 ↔ 寺庙场景切换
- 怪物战斗系统（靠近攻击+伤害显示）
- 半透明对话框（自动换行+键盘推进）

## 地图信息

| 地图 | 尺寸 | 说明 |
|------|------|------|
| village.tmx | 3780×2395 | 村庄场景，含道路、土地公、长者位置 |
| temple.tmx | 1999×1495 | 寺庙场景，含道路、怪物位置 |

## 精灵资源

| 角色 | 位置 | 帧数 | 尺寸 |
|------|------|------|------|
| 孙悟空 | img/swk/ | 4方向×4帧 | 156×199 |
| 牛魔王 | img/cattle/walk1/ | 4方向×8帧 | 124×106 |
| 土地公 | img/god/ | 多组动画 | 90×111 |
| 长者 | img/elder/ | 多组动画 | 58×83 |
