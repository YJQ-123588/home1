# 西游记 - 观音院

一个基于 Pygame 的 2D 像素风格角色扮演游戏，以中国古典名著《西游记》为背景。

## 功能特性

- **场景系统**：支持多场景管理和场景切换
- **地图渲染**：使用 TMX 格式地图，支持无缝滚动
- **相机控制**：支持方向键控制视角移动
- **动画系统**：精灵动画播放支持
- **资源管理**：统一的资源目录管理（图片、声音、字体、地图）

## 项目结构

```
├── core/           # 核心模块
│   ├── game.py     # 游戏主类
│   ├── scene.py    # 场景基类
│   └── settings.py # 配置文件
├── scenes/         # 游戏场景
│   └── village_scene.py  # 村庄场景
├── sprites/        # 精灵模块
│   └── animation.py      # 动画系统
├── map/            # 地图模块
│   └── tmx_map.py        # TMX 地图加载
├── resource/       # 资源文件
│   ├── font/       # 字体
│   ├── img/        # 图片
│   ├── sound/      # 声音
│   └── tmx/        # 地图文件
└── main.py         # 程序入口
```

## 环境要求

- Python 3.6+
- Pygame 2.5.0+
- pytmx 3.31+

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
python main.py
```

## 操作说明

- **方向键**：移动视角
- **ESC**：退出游戏

## 配置说明

主要配置项在 `core/settings.py`：

- `SCREEN_WIDTH`/`SCREEN_HEIGHT`：屏幕分辨率（默认 800×600）
- `FPS`：帧率（默认 60）
- `PLAYER_SPEED`：玩家移动速度
- `NPC_SPEED`：NPC 移动速度
- `MONSTER_SPEED`：怪物移动速度

## 开发计划

- [ ] 添加角色移动和碰撞检测
- [ ] 实现 NPC 交互系统
- [ ] 添加战斗系统
- [ ] 实现任务系统
- [ ] 添加音效和背景音乐
