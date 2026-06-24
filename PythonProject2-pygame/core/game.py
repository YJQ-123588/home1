import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('西游记 - 观音院')
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = None
        self.scenes = {}

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def set_scene(self, name):
        if name in self.scenes:
            self.current_scene = self.scenes[name]
            if hasattr(self.current_scene, 'on_enter'):
                self.current_scene.on_enter()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.current_scene:
                    self.current_scene.handle_events(event)

            if self.current_scene:
                self.current_scene.update(dt)

            self.screen.fill((0, 0, 0))
            if self.current_scene:
                self.current_scene.draw(self.screen)
            pygame.display.update()

        pygame.quit()

    def quit(self):
        self.running = False
