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

        # body coordinates must exist before other parts reference them
        self.body_pos_x = 400
        self.body_pos_y = 300

        self.arm_h = arcade.Sprite("hände und beine.png", 2.2)
        self.arm_h.center_x = self.body_pos_x
        self.arm_h.center_y = self.body_pos_y
        self.spieler_list.append(self.arm_h)




        self.fuss_h = arcade.Sprite("hände und beine.png", 2.5)
        self.fuss_h.center_x = self.body_pos_x
        self.fuss_h.center_y = self.body_pos_y - 125
        self.spieler_list.append(self.fuss_h)



        self.kopf_tex_r = arcade.load_texture("kopf.r.png")
        self.kopf_tex_l = arcade.load_texture("kopf.l.png")
        self.kopf = arcade.Sprite("kopf.png", 2.5)
        self.kopf.center_x = self.body_pos_x - 5
        self.kopf.center_y = self.body_pos_y + 50
        self.kopf.texture = self.kopf_tex_r
        self.spieler_list.append(self.kopf)

        self.body = arcade.Sprite("body.png", 2.0)
        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30
        self.spieler_list.append(self.body)

        self.fuss_v = arcade.Sprite("hände und beine.png", 2.5)
        self.fuss_v.center_x = self.body_pos_x
        self.fuss_v.center_y = self.body_pos_y - 125
        self.spieler_list.append(self.fuss_v)

        self.arm_v = arcade.Sprite("hände und beine.png", 2.0)
        self.arm_v.center_x = self.body_pos_x
        self.arm_v.center_y = self.body_pos_y
        self.spieler_list.append(self.arm_v)

        self.mouse_x = 0
        self.mouse_y = 0

        self.speed = 0
        self.circle_offset_y = 18

        self.duck_mode = False

        self.arm_radius = 35
        self.arm_half_range = math.radians(90)

        self.foot_radius = 35
        self.foot_half_range = math.radians(60)
        self.foot_swing_amp = math.radians(30)
        self.foot_lift_amp = 8.0
        self.foot_center_offset_y = -100

        self.body_range_deg = 150
        self.body_half_range = math.radians(self.body_range_deg / 2)

        circle_cx = self.body_pos_x
        circle_cy = self.body_pos_y + self.circle_offset_y
        foot_circle_cy = circle_cy + self.foot_center_offset_y

        self.fuss_h_init_angle = math.atan2(self.fuss_h.center_y - foot_circle_cy,
                                            self.fuss_h.center_x - circle_cx)
        self.fuss_v_init_angle = math.atan2(self.fuss_v.center_y - foot_circle_cy,
                                            self.fuss_v.center_x - circle_cx)

        self.v_foot_left = False
        self.v_foot_right = False
        self.v_foot_step = 20
        self.v_foot_walking = False
        self.v_foot_dir = 0
        self.v_step_phase = 0.0
        self.v_step_speed = 8.0

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            self.v_foot_left = True
            self.v_foot_dir = 1
            self.v_foot_walking = True
        elif key == arcade.key.D:
            self.v_foot_right = True
            self.v_foot_dir = -1
            self.v_foot_walking = True
        elif key == arcade.key.C:
            # toggle duck/lock mode and fix body to feet
            self.duck_mode = not self.duck_mode
            if self.duck_mode:
                self.v_foot_walking = False
                self.v_foot_dir = 0
                # remember current body position so it stays fixed
                self._duck_body_x = self.body_pos_x
                self._duck_body_y = self.body_pos_y
            else:
                self.v_step_phase = 0.0
                self._duck_body_x = None
                self._duck_body_y = None

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A:
            self.v_foot_left = False
        elif key == arcade.key.D:
            self.v_foot_right = False


        if not self.v_foot_left and not self.v_foot_right:
            self.v_foot_walking = False
            self.v_foot_dir = 0
            self.v_step_phase = 0.0
        else:

            if self.v_foot_left:
                self.v_foot_dir = -1
            elif self.v_foot_right:
                self.v_foot_dir = 1

    def on_update(self, delta_time: float):
        self.spieler_list.update()

        x_diff = self.mouse_x - self.body_pos_x
        y_diff = self.mouse_y - self.body_pos_y

        angle_rad = math.atan2(y_diff, x_diff)
        angle_deg = math.degrees(angle_rad)

        distance = math.hypot(x_diff, y_diff)
        if not self.duck_mode and distance > 5:
            dir_x = x_diff / distance
            dir_y = y_diff / distance
            self.body_pos_x += dir_x * self.speed * delta_time
            self.body_pos_y += dir_y * self.speed * delta_time

        # if duck_mode is active, force the body back to the stored duck position
        if self.duck_mode and hasattr(self, '_duck_body_x') and self._duck_body_x is not None:
            self.body_pos_x = self._duck_body_x
            self.body_pos_y = self._duck_body_y

        circle_center_x = self.body_pos_x
        circle_center_y = self.body_pos_y + self.circle_offset_y
        foot_circle_y = circle_center_y + self.foot_center_offset_y

        clamped_arm = clamp_angle(angle_rad, 0, self.arm_half_range)
        arm_x = circle_center_x + self.arm_radius * math.cos(clamped_arm)
        arm_y = circle_center_y + self.arm_radius * math.sin(clamped_arm)
        self.arm_h.center_x = arm_x
        self.arm_h.center_y = arm_y
        self.arm_v.center_x = arm_x
        self.arm_v.center_y = arm_y
        sprite_angle = -math.degrees(clamped_arm) + 90
        self.arm_h.angle = sprite_angle
        self.arm_v.angle = sprite_angle

        if not self.duck_mode:
            clamped_h_angle = clamp_angle(angle_rad, self.fuss_h_init_angle, self.foot_half_range)
            clamped_v_angle = clamp_angle(angle_rad, self.fuss_v_init_angle, self.foot_half_range)

            if self.v_foot_walking and self.v_foot_dir != 0:
                self.v_step_phase += self.v_step_speed * delta_time * self.v_foot_dir

            phase_h = self.v_step_phase
            phase_v = self.v_step_phase + math.pi

            swing_h = math.sin(phase_h) * self.foot_swing_amp
            swing_v = math.sin(phase_v) * self.foot_swing_amp

            angle_h = clamp_angle(self.fuss_h_init_angle + swing_h, self.fuss_h_init_angle, self.foot_half_range)
            angle_v = clamp_angle(self.fuss_v_init_angle + swing_v, self.fuss_v_init_angle, self.foot_half_range)

            lift_h = max(0.0, math.cos(phase_h)) * self.foot_lift_amp
            lift_v = max(0.0, math.cos(phase_v)) * self.foot_lift_amp

            foot_x_h = circle_center_x + self.foot_radius * math.cos(angle_h)
            foot_y_h = foot_circle_y + self.foot_radius * math.sin(angle_h) - lift_h
            self.fuss_h.center_x = foot_x_h
            self.fuss_h.center_y = foot_y_h

            foot_x_v = circle_center_x + self.foot_radius * math.cos(angle_v)
            foot_y_v = foot_circle_y + self.foot_radius * math.sin(angle_v) - lift_v
            self.fuss_v.center_x = foot_x_v
            self.fuss_v.center_y = foot_y_v

            self.fuss_h.angle = -math.degrees(angle_h) + 90
            self.fuss_v.angle = -math.degrees(angle_v) + 90

        self.body.center_x = self.body_pos_x
        self.body.center_y = self.body_pos_y - 30
        if self.duck_mode:
            clamped_body = clamp_angle(angle_rad, 0, self.body_half_range)
            self.body.angle = -math.degrees(clamped_body) + 90
        else:
            self.body.angle = 0

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