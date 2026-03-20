import arcade
import math

class Frosch(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("frosch.png", 1.5)
        self.center_x = x
        self.center_y = y

        self.vx = 0
        self.vy = 0
        self.speed = 200
        self.jump_power = 500
        self.gravity = 800

        self.is_jumping = False
        self.is_grounded = False

class Zauberstab(arcade.Sprite):
    def __init__(self, frosch):
        super().__init__("zauberstab_s.png", 1.5)
        self.frosch = frosch
        self.angle_offset = 0
        self.rotation_speed = 3
        self.radius = 60

    def update(self, delta_time, mouse_x, mouse_y):
        self.angle_offset += self.rotation_speed * delta_time

        x = self.frosch.center_x + self.radius * math.cos(self.angle_offset)
        y = self.frosch.center_y + self.radius * math.sin(self.angle_offset)

        self.center_x = x
        self.center_y = y


        self.angle = -math.degrees(self.angle_offset)

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.Camera2D()
        self.camera.match_window()

        self.spieler_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()

        self.frosch = Frosch(200, 300)
        self.spieler_list.append(self.frosch)

        self.zauberstab = Zauberstab(self.frosch)
        self.spieler_list.append(self.zauberstab)

        self.create_platforms()

        self.mouse_x = 0
        self.mouse_y = 0

        self.keys_pressed = set()

    def create_platforms(self):
        ground = arcade.Sprite("body.png", 3.0)
        ground.center_x = 400
        ground.center_y = 50
        ground.is_platform = True
        self.platform_list.append(ground)
        self.spieler_list.append(ground)

        platform2 = arcade.Sprite("body.png", 2.5)
        platform2.center_x = 600
        platform2.center_y = 250
        platform2.is_platform = True
        self.platform_list.append(platform2)
        self.spieler_list.append(platform2)

        platform3 = arcade.Sprite("body.png", 2.0)
        platform3.center_x = 200
        platform3.center_y = 400
        platform3.is_platform = True
        self.platform_list.append(platform3)
        self.spieler_list.append(platform3)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)

        if key in (arcade.key.SPACE, arcade.key.W) and self.frosch.is_grounded:
            self.frosch.vy = self.frosch.jump_power
            self.frosch.is_jumping = True
            self.frosch.is_grounded = False

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def check_collisions(self):
        self.frosch.is_grounded = False

        for platform in self.platform_list:
            frosch_bottom = self.frosch.center_y - self.frosch.height / 2
            frosch_top = self.frosch.center_y + self.frosch.height / 2
            frosch_left = self.frosch.center_x - self.frosch.width / 2
            frosch_right = self.frosch.center_x + self.frosch.width / 2

            platform_bottom = platform.center_y - platform.height / 2
            platform_top = platform.center_y + platform.height / 2
            platform_left = platform.center_x - platform.width / 2
            platform_right = platform.center_x + platform.width / 2

            if (frosch_right > platform_left and frosch_left < platform_right and
                frosch_bottom <= platform_top + 5 and frosch_top >= platform_bottom):

                if self.frosch.vy <= 0 and frosch_bottom > platform_bottom:
                    self.frosch.center_y = platform_top + self.frosch.height / 2
                    self.frosch.vy = 0
                    self.frosch.is_grounded = True
                    self.frosch.is_jumping = False

    def on_update(self, delta_time: float):
        if arcade.key.A in self.keys_pressed:
            self.frosch.vx = -self.frosch.speed
        elif arcade.key.D in self.keys_pressed:
            self.frosch.vx = self.frosch.speed
        else:
            self.frosch.vx = 0

        self.frosch.vy -= self.frosch.gravity * delta_time

        self.frosch.center_x += self.frosch.vx * delta_time
        self.frosch.center_y += self.frosch.vy * delta_time

        self.check_collisions()

        self.zauberstab.update(delta_time, self.mouse_x, self.mouse_y)

        self.camera.position = (self.frosch.center_x - 200, self.frosch.center_y - 150)

    def on_draw(self):
        self.clear((20, 20, 40))

        self.camera.use()

        self.platform_list.draw(pixelated=True)
        self.spieler_list.draw(pixelated=True)

        self.camera.use_unscaled_coordinates()
        arcade.draw_text("A/D - Bewegen | SPACE/W - Springen", 10, 550, arcade.color.WHITE, 12)


window = arcade.Window(800, 600, "Frosch und Zauberstab")
spiel_view = Spiel()
window.show_view(spiel_view)
arcade.run()
