import arcade
import math

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.Camera2D()
        self.camera.match_window()

        self.spieler_list = arcade.SpriteList()

        self.arm_h = arcade.Sprite("hände und beine.png",  2.0)
        self.arm_h.center_x = 404
        self.arm_h.center_y = 315
        self.spieler_list.append(self.arm_h)

        self.body = arcade.Sprite("body.png",  2.0)
        self.body.center_x = 400
        self.body.center_y = 300
        self.spieler_list.append(self.body)

        self.arm_v = arcade.Sprite("hände und beine.png",  2.0)
        self.arm_v.center_x = 400
        self.arm_v.center_y = 315
        self.spieler_list.append(self.arm_v)

        self.mouse_x = 0
        self.mouse_y = 0

        self.arm_angle = 0.0
        self.speed = 3

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y

    def on_update(self, delta_time: float):
        self.spieler_list.update()

        x_diff = self.mouse_x - self.body.center_x
        y_diff = self.mouse_y - self.body.center_y
        

        angle = math.degrees(math.atan2(y_diff, x_diff))
        self.arm_angle = angle + 90


        distance = math.sqrt(x_diff * x_diff + y_diff * y_diff)
        if distance > 5:
            direction_x = x_diff / distance
            direction_y = y_diff / distance
            

            self.body.center_x += direction_x * self.speed * delta_time
            self.body.center_y += direction_y * self.speed * delta_time
            

            radius = 35  
            circle_x = self.body.center_x + radius * math.cos(math.radians(self.arm_angle))
            circle_y = (self.body.center_y + 35) + radius * math.sin(math.radians(self.arm_angle))
            

            self.arm_h.center_x = circle_x
            self.arm_h.center_y = circle_y
            self.arm_v.center_x = circle_x
            self.arm_v.center_y = circle_y

        self.speed = 3  
    def on_draw(self):
        self.clear()

        

        self.spieler_list.draw(pixelated=True)



spiel = arcade.Window(800, 600, "Speeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed")
spiel_ansicht = Spiel()
spiel.show_view(spiel_ansicht)
arcade.run()
