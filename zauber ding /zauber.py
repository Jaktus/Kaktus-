import arcade
import math

def clamp_angle(angle, center, half_range_rad):
    diff = (angle - center + math.pi) % (2 * math.pi) - math.pi
    if diff > half_range_rad:
        diff = half_range_rad
    if diff < -half_range_rad:
        diff = -half_range_rad
    return center + diff

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.Camera2D()
        self.camera.match_window()

        self.spieler_list = arcade.SpriteList()

        self.arm_h = arcade.Sprite("hände und beine.png", 2.2)
        self.arm_h.center_x = 408
        self.arm_h.center_y = 350
        self.spieler_list.append(self.arm_h)

        self.arm_v = arcade.Sprite("hände und beine.png", 2.0)
        self.arm_v.center_x = 400
        self.arm_v.center_y = 350
        self.spieler_list.append(self.arm_v)

        self.fuss_h = arcade.Sprite("hände und beine.png", 2.5)
        self.fuss_h.center_x = 400
        self.fuss_h.center_y = 175
        self.spieler_list.append(self.fuss_h)

        self.fuss_v = arcade.Sprite("hände und beine.png", 2.5)
        self.fuss_v.center_x = 395
        self.fuss_v.center_y = 175
        self.spieler_list.append(self.fuss_v)

        self.kopf_tex_r = arcade.load_texture("kopf.r.png")
        self.kopf_tex_l = arcade.load_texture("kopf.l.png")
        self.kopf = arcade.Sprite("kopf.png", 2.5)
        self.kopf.center_x = 395
        self.kopf.center_y = 340
        self.kopf.texture = self.kopf_tex_r
        self.spieler_list.append(self.kopf)

        self.body = arcade.Sprite("body.png", 2.0)
        self.body_pos_x = 400
        self.body_pos_y = 300
        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30
        self.spieler_list.append(self.body)

        self.mouse_x = 0
        self.mouse_y = 0

        self.speed = 0
        self.circle_offset_y = 18

        self.arm_radius = 35
        self.foot_radius = 30
        self.foot_center_offset_y = -100

        circle_cx = self.body_pos_x
        circle_cy = self.body_pos_y + self.circle_offset_y
        foot_circle_cy = circle_cy + self.foot_center_offset_y

        self.fuss_h_init_angle = math.atan2(self.fuss_h.center_y - foot_circle_cy,
                                            self.fuss_h.center_x - circle_cx)
        self.fuss_v_init_angle = math.atan2(self.fuss_v.center_y - foot_circle_cy,
                                            self.fuss_v.center_x - circle_cx)

        self.foot_half_range = math.radians(60)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, delta_time: float):
        self.spieler_list.update()

        x_diff = self.mouse_x - self.body_pos_x
        y_diff = self.mouse_y - self.body_pos_y

        angle_rad = math.atan2(y_diff, x_diff)
        angle_deg = math.degrees(angle_rad)

        distance = math.hypot(x_diff, y_diff)
        if distance > 5:
            dir_x = x_diff / distance
            dir_y = y_diff / distance
            self.body_pos_x += dir_x * self.speed * delta_time
            self.body_pos_y += dir_y * self.speed * delta_time

        circle_center_x = self.body_pos_x
        circle_center_y = self.body_pos_y + self.circle_offset_y
        foot_circle_y = circle_center_y + self.foot_center_offset_y

        arm_x = circle_center_x + self.arm_radius * math.cos(angle_rad)
        arm_y = circle_center_y + self.arm_radius * math.sin(angle_rad)
        self.arm_h.center_x = arm_x
        self.arm_h.center_y = arm_y
        self.arm_v.center_x = arm_x
        self.arm_v.center_y = arm_y
        sprite_angle = -math.degrees(angle_rad) + 90
        self.arm_h.angle = sprite_angle
        self.arm_v.angle = sprite_angle

        clamped_h_angle = clamp_angle(angle_rad, self.fuss_h_init_angle, self.foot_half_range)
        clamped_v_angle = clamp_angle(angle_rad, self.fuss_v_init_angle, self.foot_half_range)

        self.fuss_h.center_x = circle_center_x + self.foot_radius * math.cos(clamped_h_angle)
        self.fuss_h.center_y = foot_circle_y + self.foot_radius * math.sin(clamped_h_angle)
        self.fuss_v.center_x = circle_center_x + self.foot_radius * math.cos(clamped_v_angle)
        self.fuss_v.center_y = foot_circle_y + self.foot_radius * math.sin(clamped_v_angle)

        self.fuss_h.angle = -math.degrees(clamped_h_angle) + 90
        self.fuss_v.angle = -math.degrees(clamped_v_angle) + 90

        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30

        self.kopf.center_x = self.body_pos_x - 5
        self.kopf.center_y = self.body_pos_y + 50

        if self.mouse_x > self.body_pos_x:
            self.fuss_h.center_x = self.fuss_h.center_x and - 20
            self.fuss_v.center_x = self.fuss_v.center_x and - 20
            self.kopf.texture = self.kopf_tex_l

        else:
            self.fuss_h.center_x = self.fuss_h.center_x and + 10
            self.fuss_v.center_x = self.fuss_v.center_x and + 10
            self.kopf.texture = self.kopf_tex_r

    def on_draw(self):
        self.clear()
        self.spieler_list.draw(pixelated=True)

spiel = arcade.Window(800, 600, "Speeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed")
spiel_ansicht = Spiel()
spiel.show_view(spiel_ansicht)
arcade.run()