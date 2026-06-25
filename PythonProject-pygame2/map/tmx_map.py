import pygame
from pytmx import TiledTileLayer, TiledObjectGroup, TiledImageLayer
from pytmx.util_pygame import load_pygame


class TiledMap:
    def __init__(self, filename):
        self.tmx_data = load_pygame(filename)
        self.pixel_size = (
            self.tmx_data.width * self.tmx_data.tilewidth,
            self.tmx_data.height * self.tmx_data.tileheight
        )
        self.width = self.pixel_size[0]
        self.height = self.pixel_size[1]
        self.map_surface = self._render_map()

    def _render_map(self):
        surface = pygame.Surface(self.pixel_size, pygame.SRCALPHA)
        if self.tmx_data.background_color:
            surface.fill(pygame.Color(self.tmx_data.background_color))
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                self._render_tile_layer(surface, layer)
            elif isinstance(layer, TiledObjectGroup):
                pass
            elif isinstance(layer, TiledImageLayer):
                self._render_image_layer(surface, layer)
        return surface

    def _render_tile_layer(self, surface, layer):
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        for x, y, image in layer.tiles():
            if image:
                surface.blit(image, (x * tw, y * th))

    def _render_image_layer(self, surface, layer):
        if layer.image:
            surface.blit(layer.image, (0, 0))

    def render(self, surface, offset_x=0, offset_y=0):
        surface.blit(self.map_surface, (-offset_x, -offset_y))

    def get_object_positions(self, layer_name):
        positions = []
        for layer in self.tmx_data.layers:
            if isinstance(layer, TiledObjectGroup) and layer.name == layer_name:
                for obj in layer:
                    positions.append({
                        'name': obj.name,
                        'x': obj.x,
                        'y': obj.y,
                        'width': obj.width,
                        'height': obj.height,
                        'type': getattr(obj, 'type', None),
                        'gid': getattr(obj, 'gid', None)
                    })
        return positions

    def get_map_size(self):
        return self.width, self.height
