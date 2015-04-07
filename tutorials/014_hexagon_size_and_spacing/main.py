# -*- coding:utf8 -*-
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse, Line, Mesh
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from math import pi, cos, sin, sqrt

class Position(object):
    def __init__(self, *args, **kwargs):
        if args:
            if type(args[0]) is Position:
                src = args[0]
                self.x = src.x
                self.y = src.y
            else:
                self.x, self.y = args[:2]
        else:
            self.x = kwargs['x']
            self.y = kwargs['y']

    def __repr__(self):
        return 'Position(x={0:.2f}, y={1:.2f})'.format(self.x, self.y)        

    def to_tuple(self):
        return (self.x, self.y)

class Vertex(object):
    def __init__(self, *args, **kwargs):
        if args:
            self.x, self.y, self.u, self.v = args[:4]
        else:
            self.x = kwargs['x']
            self.y = kwargs['y']
            self.u = kwargs['u']
            self.v = kwargs['v']

    def __repr__(self):
        return 'Vertex(x={0:.2f}, y={1:.2f}, u={2:.2f}, v={3:.2f})'.format(self.x, self.y, self.u, self.v)        


class Hexagon(object):
    WEDGE_ANGLE_DEG = 60

    _base_angle_deg = 30

    @classmethod
    def get_hexagon_corner_angle_deg(cls, i):
        return cls._base_angle_deg + cls.WEDGE_ANGLE_DEG * i

    @classmethod
    def get_hexagon_corner_angle_rad(cls, i):
        return pi / 180 * cls.get_hexagon_corner_angle_deg(i)
        
    @classmethod
    def create_hexagon_corner_position(cls, center, size, i):
        angle_rad = cls.get_hexagon_corner_angle_rad(i)
        return Position(
                center.x + size * cos(angle_rad), 
                center.y + size * sin(angle_rad))

    @classmethod
    def create_hexagon_corner_vertex(cls, center, size, i):
        angle_rad = cls.get_hexagon_corner_angle_rad(i)
        cos_angle_rad = cos(angle_rad)
        sin_angle_rad = sin(angle_rad)
        return Vertex(
                center.x + size * cos_angle_rad, 
                center.y + size * sin_angle_rad,
                cos_angle_rad, 
                sin_angle_rad)

    @classmethod
    def create_hexagon_corner_angles(cls):
        return [cls.get_hexagon_corner_angle_deg(i) for i in xrange(6)]

    @classmethod
    def create_hexagon_corner_positions(cls, center, edge_len):
        return [cls.create_hexagon_corner_position(center, edge_len, i) for i in xrange(6)]

    @classmethod
    def create_hexagon_corner_vertices(cls, center, edge_len):
        return [cls.create_hexagon_corner_vertex(center, edge_len, i) for i in xrange(6)]

    @classmethod
    def get_hexagon_height(cls, edge_len):
        return 2 * edge_len

    @classmethod
    def get_hexagon_vert(cls, edge_len):
        return cls.get_hexagon_height(edge_len) / 4.0 * 3.0

    @classmethod
    def get_hexagon_width(cls, edge_len):
        return sqrt(3.0) / 2.0 * cls.get_hexagon_height(edge_len) 

    @classmethod
    def get_hexagon_horiz(cls, edge_len):
        return cls.get_hexagon_width(edge_len)



class KivyHexagon(Hexagon):
    @classmethod
    def gen_position_sequences(cls, positions):
        for position in positions:
            yield position.x
            yield position.y
        
    @classmethod
    def gen_closed_position_sequences(cls, positions):
        for position in positions:
            yield position.x
            yield position.y
       
        yield positions[0].x
        yield positions[0].y

    @classmethod
    def gen_vertex_sequences(cls, vertexs):
        for vertex in vertexs:
            yield vertex.x
            yield vertex.y
            yield vertex.u
            yield vertex.v
        
    @classmethod
    def convert_line_points(cls, positions):
        return [e for e in cls.gen_position_sequences(positions)]

    @classmethod
    def convert_closed_line_points(cls, positions):
        return [e for e in cls.gen_closed_position_sequences(positions)]

    @classmethod
    def convert_mesh_vertices(cls, vertices):
        return [e for e in cls.gen_vertex_sequences(vertices)]

    @classmethod
    def make_hexagon_mesh(cls, center_position, edge_len):
        corner_vertices = cls.create_hexagon_corner_vertices(center_position, edge_len) 
        return Mesh(vertices=cls.convert_mesh_vertices(corner_vertices), indices=xrange(len(corner_vertices)), mode='triangle_fan')

    @classmethod
    def make_hexagon_outline(cls, center_position, edge_len, width=1):
        corner_positions = cls.create_hexagon_corner_positions(center_position, edge_len) 
        return Line(points=cls.convert_closed_line_points(corner_positions), width=width)

    @classmethod
    def make_circle(self, center_position, radius):
        return Ellipse(pos=(center_position.x - radius, center_position.y - radius), size=(radius * 2, radius * 2))


class HexagonRoot(FloatLayout):
    X_AXIS_LEN = 700
    Y_AXIS_LEN = 400

    EDGE_LEN = 100
    EDGE_WIDTH = 2
    CENTER_RADIUS = 4
    CORNER_RADIUS = 4
    CENTER_COLOR = (0.5, 0.1, 0.1)
    CORNER_COLOR = (0.5, 0.1, 0.1)
    EDGE_COLOR = (0.3, 0.3, 0.3)
    AXIS_COLOR = (0.3, 0.3, 0.3)
    MESH_COLOR = (0.5, 0.5, 0.5)

    def __init__(self, **kwargs):
        super(HexagonRoot, self).__init__(**kwargs)

        self.bind(pos=self.render_canvas, size=self.render_canvas)


    def render_canvas(self, *args):
        origin_position = Position(*self.center)
        origin_position.x -= self.X_AXIS_LEN / 2
        origin_position.y -= self.Y_AXIS_LEN / 2

        x_axis_position = Position(origin_position.x + self.X_AXIS_LEN, origin_position.y)
        y_axis_position = Position(origin_position.x, origin_position.y + self.Y_AXIS_LEN)

        hexagon_vert = KivyHexagon.get_hexagon_vert(self.EDGE_LEN)
        hexagon_horiz = KivyHexagon.get_hexagon_horiz(self.EDGE_LEN)
        hexagon_width = KivyHexagon.get_hexagon_width(self.EDGE_LEN)
        hexagon_height = KivyHexagon.get_hexagon_height(self.EDGE_LEN)

        self.canvas.before.clear()

        with self.canvas.before:
            Color(*self.AXIS_COLOR)
            Line(points=KivyHexagon.convert_line_points([x_axis_position, origin_position, y_axis_position]), width=self.EDGE_WIDTH)

            base_position = Position(origin_position)
            base_position.x += hexagon_horiz * 0.5
            base_position.y += hexagon_height * 0.5

            line_position = Position(base_position)
            for row in xrange(0, 2):
                each_position = Position(line_position)
                if row % 2 == 1:
                    each_position.x += hexagon_horiz * 0.5

                for col in xrange(0, 3):
                    Color(*self.MESH_COLOR)
                    KivyHexagon.make_hexagon_mesh(each_position, self.EDGE_LEN)

                    Color(*self.EDGE_COLOR)
                    KivyHexagon.make_hexagon_outline(each_position, self.EDGE_LEN)

                    Color(*self.CENTER_COLOR)
                    KivyHexagon.make_circle(each_position, self.CENTER_RADIUS)

                    each_position.x += hexagon_horiz
                line_position.y += hexagon_vert
            

            Color(*self.AXIS_COLOR)
            h_line_s_position = Position(origin_position)
            h_line_e_position = Position(h_line_s_position)
            h_line_e_position.x += self.X_AXIS_LEN

            for row in xrange(0, int(self.Y_AXIS_LEN / hexagon_height * 4)):
                Line(points=KivyHexagon.convert_line_points([h_line_s_position, h_line_e_position]))
                h_line_s_position.y += hexagon_height / 4
                h_line_e_position.y += hexagon_height / 4

            v_line_s_position = Position(origin_position)
            v_line_e_position = Position(v_line_s_position)
            v_line_e_position.y += self.Y_AXIS_LEN

            for row in xrange(0, int(self.X_AXIS_LEN / hexagon_width * 2))

                Line(points=KivyHexagon.convert_line_points([v_line_s_position, v_line_e_position]))
                v_line_s_position.x += hexagon_width / 2
                v_line_e_position.x += hexagon_width / 2


    def render_circle(self, center, radius):
        return Ellipse(pos=(center.x - radius, center.y - radius), size=(radius * 2, radius * 2))

class HexagonApp(App):
    pass

if __name__ == '__main__':
    HexagonApp().run()
