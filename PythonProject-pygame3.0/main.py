"""
西游记 - 祸起观音院
RPG游戏主入口

操作说明：
- 方向键：控制孙悟空移动
- Shift：加速移动
- 空格/回车：关闭对话框、确认
- ESC：退出游戏

战斗操作：
- 数字键1：普通攻击
- 数字键2：技能攻击
- 鼠标点击按钮也可选择攻击方式
"""

from core.game import Game


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
