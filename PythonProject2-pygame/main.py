import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from scenes.village_scene import VillageScene
from scenes.temple_scene import TempleScene


def main():
    game = Game()

    village = VillageScene(game)
    temple = TempleScene(game)

    game.add_scene('village', village)
    game.add_scene('temple', temple)

    village.fade.set_status(1)
    temple.fade.set_status(2)

    game.set_scene('village')
    game.run()


if __name__ == '__main__':
    main()
