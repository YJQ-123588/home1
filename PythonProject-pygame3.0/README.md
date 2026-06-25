# 西游记 - 祸起观音院

一款基于Pygame开发的2D RPG冒险游戏，以中国古典名著《西游记》中"祸起观音院"为故事背景。

## 游戏特点

- 经典的2D RPG游戏玩法
- 回合制战斗系统
- 多场景探索（村庄、寺庙）
- 丰富的NPC对话和剧情
- 精美的像素风格角色动画
- 背景音乐和音效支持

## 游戏操作

### 移动控制
- **方向键**：控制孙悟空移动
- **Shift**：加速移动
- **空格/回车**：关闭对话框、确认选择
- **ESC**：退出游戏

### 战斗操作
- **数字键1**：普通攻击
- **数字键2**：技能攻击（如意金箍棒）
- **数字键3**：大招（七十二变，需解锁）
- **鼠标点击按钮**：也可选择攻击方式

## 游戏流程

1. **开始界面**：点击"开始游戏"或按回车键开始
2. **村庄场景**：与NPC对话，了解剧情，准备前往寺庙
3. **寺庙场景**：探索寺庙，与妖怪战斗
4. **战斗系统**：回合制战斗，选择攻击方式击败敌人
5. **游戏通关**：成功降服观音院妖怪

## 项目结构

```
PythonProject1-pygame1/
├── main.py              # 游戏主入口
├── core/                # 核心模块
│   ├── game.py          # 游戏主控类
│   ├── animation.py     # 动画系统
│   └── tiled_map.py     # Tiled地图加载
├── scenes/              # 场景模块
│   ├── start_scene.py   # 开始界面
│   ├── village_scene.py # 村庄场景
│   ├── temple_scene.py  # 寺庙场景
│   └── fight_scene.py   # 战斗场景
├── characters/          # 角色模块
│   ├── player.py        # 玩家角色（孙悟空）
│   └── npc.py           # NPC角色
├── ui/                  # UI模块
│   ├── dialog.py        # 对话框
│   ├── confirm_dialog.py# 确认对话框
│   ├── fade_scene.py    # 渐入渐出效果
│   └── avoid_battle_dialog.py # 避战对话框
└── config/              # 配置模块
    └── settings.py      # 游戏设置和常量
```

## 运行要求

### Python版本
- Python 3.6+

### 依赖库
- Pygame 2.0+

### 资源文件
游戏需要以下资源文件（请确保路径正确）：
- 图片资源：`D:\Documents\pygame.resource\resource\img\`
- 音频资源：`D:\Documents\pygame.resource\resource\sound\`
- 地图文件：`D:\Documents\pygame.resource\resource\tmx\`
- 字体文件：`D:\Documents\pygame.resource\resource\font\newfont.TTF`

## 安装与运行

1. 确保已安装Python 3.6+
2. 安装Pygame库：
   ```bash
   pip install pygame
   ```
3. 确保资源文件路径正确
4. 运行游戏：
   ```bash
   python main.py
   ```

## 游戏配置

游戏配置文件位于 `config/settings.py`，可调整以下参数：

- **窗口设置**：屏幕尺寸（800x600）、帧率（30FPS）
- **玩家属性**：移动速度、基础生命值（100）、基础攻击力（25）
- **战斗设置**：普通攻击伤害（25）、技能伤害（40）、大招伤害（70）
- **怪物属性**：普通怪物生命值（100）、BOSS生命值（250）

## 开发说明

### 代码风格
- 使用中文注释
- 遵循Python PEP 8编码规范
- 采用面向对象设计模式

### 扩展性
- 场景系统易于扩展新场景
- 角色系统支持添加新NPC
- 战斗系统可扩展新技能和攻击方式

## 已知问题

- 资源文件路径为绝对路径，需要用户根据实际情况修改`config/settings.py`中的路径
- 部分资源文件缺失时游戏会使用默认颜色填充

## 许可证

本项目仅供学习和研究使用。