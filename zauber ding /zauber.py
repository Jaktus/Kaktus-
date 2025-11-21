import arcade
import math

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.Camera2D()
        self.camera.match_window()

        self.spieler_list = arcade.SpriteList()

        self.arm_h = arcade.Sprite("hände und beine.png",  2.2)
        self.arm_h.center_x = 408
        self.arm_h.center_y = 350
        self.spieler_list.append(self.arm_h)

        self.fuss_h = arcade.Sprite("hände und beine.png",  2.5)
        self.fuss_h.center_x = 400
        self.fuss_h.center_y = 175
        self.spieler_list.append(self.fuss_h)

        self.kopf_tex_r = arcade.load_texture("kopf.r.png")
        self.kopf_tex_l = arcade.load_texture("kopf.l.png")
        self.kopf = arcade.Sprite("kopf.png",  2.5)
        self.kopf.center_x = 395
        self.kopf.center_y = 340
        self.kopf.texture = self.kopf_tex_r
        self.spieler_list.append(self.kopf)

        self.body = arcade.Sprite("body.png",  2.0)
        self.body_pos_x = 400
        self.body_pos_y = 300
        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30
        self.spieler_list.append(self.body)

        self.fuss_v = arcade.Sprite("hände und beine.png",  2.5)
        self.fuss_v.center_x = 395
        self.fuss_v.center_y = 175
        self.spieler_list.append(self.fuss_v)

        self.arm_v = arcade.Sprite("hände und beine.png",  2.0)
        self.arm_v.center_x = 400
        self.arm_v.center_y = 350
        self.spieler_list.append(self.arm_v)

        self.mouse_x = 0
        self.mouse_y = 0

        self.arm_angle = 0.0
        self.speed = 0

        texture = arcade.load_texture("body.png")

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

        radius = 35
        circle_center_x = self.body_pos_x
        circle_center_y = self.body_pos_y + 18
        circle_x = circle_center_x + radius * math.cos(angle_rad)
        circle_y = circle_center_y + radius * math.sin(angle_rad)

        self.arm_h.center_x = circle_x
        self.arm_h.center_y = circle_y
        self.arm_v.center_x = circle_x
        self.arm_v.center_y = circle_y

        sprite_angle = -angle_deg + 90
        self.arm_h.angle = sprite_angle
        self.arm_v.angle = sprite_angle

        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30

        self.kopf.center_x = self.body_pos_x - 5
        self.kopf.center_y = self.body_pos_y + 50

        if self.mouse_x > self.body_pos_x:
            self.kopf.texture = self.kopf_tex_l
        else:
            self.kopf.texture = self.kopf_tex_r

    def on_draw(self):
        self.clear()
        self.spieler_list.draw(pixelated=True)

spiel = arcade.Window(800, 600, "Speeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed")
spiel_ansicht = Spiel()
spiel.show_view(spiel_ansicht)
arcade.run()