import pyglet
import arcade
import random
from arcade.future.light import Light, LightLayer

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Undergrounds Game"

ORE_TYPES = ["Stone1.png", "Stone2.png"]

WORLD_WIDTH = 10000
WORLD_HEIGHT = 10000
WORLD_DEPTH = 10000

AMBIENT_COLOR = (10, 10, 10)

class Labyrinth(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)

        self.background_sprite_list = None
        self.player_list = None
        self.wall_list = None
        self.player_sprite = None

        self.physik_engine = None

        self.light_layer = None
        self.player_light = None
        self.light_on = False

        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False
        self.camera = None

        self.ghost_list = None
        self.GH = None

    def setup(self):
        self.background_sprite_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        self.player_sprite = arcade.Sprite("spieler 98*98.png", 0.6)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player_sprite)

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.DIM_GRAY)

        radius = 300
        color = arcade.csscolor.WHITE
        mode = 'soft'
        self.player_light = Light(self.player_sprite.center_x, self.player_sprite.center_y, radius, color, mode)
        self.light_layer.add(self.player_light)

        self.under = arcade.SpriteList()
        for _ in range(2200):
            ore_image = random.choice(ORE_TYPES)
            ore = arcade.Sprite(ore_image, 1.5)
            ore.center_x = random.randint(50, WORLD_WIDTH - 50)
            ore.center_y = random.randint(50, WORLD_HEIGHT - 50)
            self.under.append(ore)

        self.physik_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.under)

        self.camera = arcade.Camera2D()

        self.ghost_list = arcade.SpriteList()
        self.GH = arcade.Sprite("Ghost.png", 0.6)
        self.GH.center_x = self.player_sprite.center_x
        self.GH.center_y = self.player_sprite.center_y
        self.ghost_list.append(self.GH)

    def on_draw(self):
        self.clear()
        self.camera.use()
        with self.light_layer:
            self.under.draw()
            self.player_list.draw()
            self.ghost_list.draw()
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

    def on_update(self, delta_time):
        if self.move_up:
            self.player_sprite.change_y = 4
        elif self.move_down:
            self.player_sprite.change_y = -4
        else:
            self.player_sprite.change_y = 0

        if self.move_left:
            self.player_sprite.change_x = -4
        elif self.move_right:
            self.player_sprite.change_x = 4
        else:
            self.player_sprite.change_x = 0

        self.player_light.position = self.player_sprite.position
        self.physik_engine.update()
        self.camera.position = self.player_sprite.position

        if self.GH:
            speed = 2.5
            dx = self.player_sprite.center_x - self.GH.center_x
            dy = self.player_sprite.center_y - self.GH.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 1:
                self.GH.center_x += dx / distance * speed
                self.GH.center_y += dy / distance * speed

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.move_up = True
        elif symbol == arcade.key.S:
            self.move_down = True
        elif symbol == arcade.key.A:
            self.move_left = True
        elif symbol == arcade.key.D:
            self.move_right = True

        if symbol == arcade.key.SPACE:
            if self.light_on:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)
            self.light_on = not self.light_on

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.move_up = False
        elif symbol == arcade.key.S:
            self.move_down = False
        elif symbol == arcade.key.A:
            self.move_left = False
        elif symbol == arcade.key.D:
            self.move_right = False

def main():
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
