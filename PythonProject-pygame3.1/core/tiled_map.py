import pygame
from pytmx import load_pygame


class TiledMap:
    """TMX地图加载与渲染类"""

    def __init__(self, tmx_path):
        self.tmx_data = load_pygame(tmx_path)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.surface = None
        self._render()

    def _render(self):
        """渲染地图到Surface"""
        self.surface = pygame.Surface((self.width, self.height))
        # 渲染所有可见图层
        for layer in self.tmx_data.visible_layers:
            # 图像图层（pytmx已将image加载为Surface）
            if hasattr(layer, 'image') and layer.image:
                self.surface.blit(layer.image, (0, 0))
            # 瓦片图层
            elif hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.surface.blit(tile, (x * self.tmx_data.tilewidth,
                                                  y * self.tmx_data.tileheight))

    def get_surface(self):
        """获取渲染好的地图Surface"""
        return self.surface

    def get_objects_by_group(self, group_name):
        """获取指定对象组中的所有对象"""
        results = []
        try:
            group = self.tmx_data.get_layer_by_name(group_name)
            if group:
                for obj in group:
                    results.append(obj)
        except Exception:
            pass
        return results

    def get_road_polygons(self):
        """获取道路层中的所有多边形碰撞区域"""
        polygons = []
        try:
            road_layer = self.tmx_data.get_layer_by_name('road')
            if road_layer:
                for obj in road_layer:
                    if hasattr(obj, 'points') and obj.points:
                        # 将相对坐标转为绝对坐标
                        abs_points = []
                        for px, py in obj.points:
                            abs_points.append((obj.x + px, obj.y + py))
                        polygons.append(abs_points)
        except Exception:
            pass
        return polygons

    def get_object_position(self, group_name, obj_name):
        """获取指定对象的位置"""
        try:
            group = self.tmx_data.get_layer_by_name(group_name)
            if group:
                for obj in group:
                    if obj.name == obj_name:
                        return (obj.x, obj.y)
        except Exception:
            pass
        return None

    def get_all_named_objects(self, group_name):
        """获取对象组中所有有名称的对象"""
        results = {}
        try:
            group = self.tmx_data.get_layer_by_name(group_name)
            if group:
                for obj in group:
                    if obj.name:
                        results[obj.name] = (obj.x, obj.y)
        except Exception:
            pass
        return results

    def get_obstacle_rects(self, min_width=20, min_height=20):
        """获取障碍物图层中的所有矩形碰撞区域
        Args:
            min_width: 最小宽度，小于此值的忽略
            min_height: 最小高度，小于此值的忽略
        """
        rects = []
        try:
            obstacle_layer = self.tmx_data.get_layer_by_name('obstacle')
            if obstacle_layer:
                for obj in obstacle_layer:
                    if hasattr(obj, 'width') and hasattr(obj, 'height'):
                        if obj.width >= min_width and obj.height >= min_height:
                            rects.append(pygame.Rect(
                                int(obj.x), int(obj.y),
                                int(obj.width), int(obj.height)
                            ))
        except Exception:
            pass
        return rects
