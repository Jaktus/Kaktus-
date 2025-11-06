# ...existing code...
import arcade
import pymunk
import math
from typing import Dict

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Ragdoll mit Physics"

COLOR_TORSO = (32, 160, 64)
COLOR_HEAD = (200, 180, 120)
COLOR_LIMB = (100, 100, 220)

class BodyPart:
    def __init__(self, name: str, pymunk_body: pymunk.Body, pymunk_shape: pymunk.Shape, sprite: arcade.Sprite):
        self.name = name
        self.body = pymunk_body
        self.shape = pymunk_shape
        self.sprite = sprite

class Ragdoll:
    def __init__(self, space: pymunk.Space, x: float, y: float):
        self.space = space
        self.parts: Dict[str, BodyPart] = {}
        self.joints = []
        self._create_parts(x, y)
        self._create_joints()

    def _make_box_part(self, name, x, y, w, h, mass, color):
        moment = pymunk.moment_for_box(mass, (w, h))
        body = pymunk.Body(mass, moment)
        body.position = x, y
        shape = pymunk.Poly.create_box(body, (w, h))
        shape.friction = 1.0
        self.space.add(body, shape)
        sprite = arcade.SpriteSolidColor(int(w), int(h), color)
        sprite.center_x = x
        sprite.center_y = y
        part = BodyPart(name, body, shape, sprite)
        self.parts[name] = part
        return part

    def _create_parts(self, x, y):
        torso_w, torso_h = 40, 60
        head_w, head_h = 36, 36
        limb_w, limb_h = 12, 44
        torso = self._make_box_part("torso", x, y, torso_w, torso_h, mass=3.0, color=COLOR_TORSO)
        head = self._make_box_part("head", x, y + (torso_h/2 + head_h/2) + 2, head_w, head_h, mass=1.0, color=COLOR_HEAD)
        left_arm = self._make_box_part("left_arm", x - (torso_w/2 + limb_w/2), y + 8, limb_w, limb_h, mass=0.6, color=COLOR_LIMB)
        right_arm = self._make_box_part("right_arm", x + (torso_w/2 + limb_w/2), y + 8, limb_w, limb_h, mass=0.6, color=COLOR_LIMB)
        left_leg = self._make_box_part("left_leg", x - 10, y - (torso_h/2 + limb_h/2), limb_w, limb_h, mass=1.0, color=COLOR_LIMB)
        right_leg = self._make_box_part("right_leg", x + 10, y - (torso_h/2 + limb_h/2), limb_w, limb_h, mass=1.0, color=COLOR_LIMB)

    def _create_joints(self):
        torso = self.parts["torso"].body
        torso_w, torso_h = 40, 60
        def connect(a_body, b_body, anchor_a, anchor_b, min_angle=-math.pi/2, max_angle=math.pi/2, spring=None):
            pj = pymunk.PinJoint(a_body, b_body, anchor_a, anchor_b)
            self.space.add(pj)
            self.joints.append(pj)
            rl = pymunk.RotaryLimitJoint(a_body, b_body, min_angle, max_angle)
            self.space.add(rl)
            self.joints.append(rl)
            if spring:
                ds = pymunk.DampedSpring(a_body, b_body, anchor_a, anchor_b, rest_length=spring[0], stiffness=spring[1], damping=spring[2])
                self.space.add(ds)
                self.joints.append(ds)
        head = self.parts["head"].body
        connect(torso, head, (0, torso_h/2), (0, -18), min_angle=-0.6, max_angle=0.6, spring=(5, 400, 20))
        left_arm = self.parts["left_arm"].body
        right_arm = self.parts["right_arm"].body
        connect(torso, left_arm, (-torso_w/2, 10), (0, 18), min_angle=-2.2, max_angle=0.2)
        connect(torso, right_arm, (torso_w/2, 10), (0, 18), min_angle=-0.2, max_angle=2.2)
        left_leg = self.parts["left_leg"].body
        right_leg = self.parts["right_leg"].body
        connect(torso, left_leg, (-10, -torso_h/2), (0, 18), min_angle=-1.5, max_angle=1.0)
        connect(torso, right_leg, (10, -torso_h/2), (0, 18), min_angle=-1.0, max_angle=1.5)

    def draw(self):
        for p in self.parts.values():
            p.sprite.center_x = p.body.position.x
            p.sprite.center_y = p.body.position.y
            p.sprite.angle = -math.degrees(p.body.angle)
            p.sprite.draw()

class PhysicsWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
        arcade.set_background_color(arcade.color.ALMOND)
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, (0, 80), (SCREEN_WIDTH, 80), 1.0)
        floor_shape.friction = 1.0
        self.space.add(floor_body, floor_shape)
        self.ragdoll = Ragdoll(self.space, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)
        self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.mouse_joint = None
        self.picked_shape = None

    def on_draw(self):
        arcade.start_render()
        arcade.draw_rectangle_filled(SCREEN_WIDTH/2, 41, SCREEN_WIDTH, 82, arcade.color.DARK_SLATE_GRAY)
        self.ragdoll.draw()

    def on_update(self, delta_time: float):
        steps = 3
        for _ in range(steps):
            self.space.step(delta_time / steps)

    def on_mouse_press(self, x, y, button, modifiers):
        shapes = self.space.point_query(pymunk.Vec2d(x, y), 1, pymunk.ShapeFilter())
        if shapes:
            shape = shapes[0].shape
            body = shape.body
            self.mouse_body.position = x, y
            pj = pymunk.PinJoint(self.mouse_body, body, (0,0), body.world_to_local((x,y)))
            pj.max_force = 1e6
            self.space.add(pj)
            self.mouse_joint = pj
            self.picked_shape = shape

    def on_mouse_release(self, x, y, button, modifiers):
        if self.mouse_joint:
            self.space.remove(self.mouse_joint)
            self.mouse_joint = None
            self.picked_shape = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.mouse_joint:
            self.mouse_body.position = x, y

def main():
    window = PhysicsWindow()
    arcade.run()

if __name__ == "__main__":
    main()
# ...existing code...