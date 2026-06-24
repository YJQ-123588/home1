阶段一：基础框架 详细概述
1. 项目结构
├── core/           # 核心引擎
├── scenes/         # 场景管理
├── map/            # 地图系统
├── sprites/        # 精灵/动画
├── ui/             # UI组件（待扩展）
└── resource/       # 游戏资源
    ├── font/       # 字体文件
    ├── img/        # 图片资源
    ├── sound/      # 音效文件
    └── tmx/        # Tiled地图文件
2. 核心模块详解
core/game.py - 游戏主引擎
- 初始化: Pygame初始化、创建800x600窗口、60FPS时钟
- 场景管理: 字典存储多个场景，支持添加/切换场景
- 主循环: 事件处理 → 更新逻辑 → 清屏 → 绘制 → 刷新显示
core/scene.py - 场景系统
- Scene基类: 定义场景接口（事件处理、更新、绘制）
- FadeScene类: 场景切换的淡入淡出效果
- IN: 淡入（alpha从0到255）
- NORMAL: 正常显示
- OUT: 淡出（alpha从255到0）
- SceneStatus枚举: 管理场景状态
core/settings.py - 全局配置
- 屏幕: 800×600, 60FPS
- 路径: 资源目录、字体、地图文件
- 速度: 玩家3、NPC 1、怪物2
- 方向常量: DOWN=0, LEFT=1, UP=2, RIGHT=3
- 动画速度: 150ms/帧
3. 功能模块详解
map/tmx_map.py - 地图系统
- 使用pytmx库加载Tiled编辑器制作的TMX地图
- 支持三种图层:
- TiledTileLayer: 瓦片图层（地面、墙壁等）
- TiledObjectGroup: 对象图层（NPC位置、触发点）
- TiledImageLayer: 图像图层（背景图）
- 提供地图尺寸查询、对象位置获取
sprites/animation.py - 动画系统
- 四方向动画支持（下、左、上、右）
- 两种加载方式:
- from_directory(): 从目录加载，自动分割帧
- from_files(): 从文件列表加载指定方向
- 帧动画更新: 根据时间间隔切换帧
4. 当前测试场景
scenes/village_scene.py 实现:
- 加载村庄TMX地图
- 相机跟随方向键移动（边界限制）
- 场景进入时的淡入效果
- ESC键退出游戏
5. 待扩展功能
- ui/ 目录为空，待添加UI组件
- 未实现角色精灵、NPC交互、战斗系统等
