import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from scenes.village_scene import TestScene


def main():
    game = Game()
    test_scene = TestScene(game)
    game.add_scene('village', test_scene)
    game.set_scene('village')
    game.run()


if __name__ == '__main__':
    main()
