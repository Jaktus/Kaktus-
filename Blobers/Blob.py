import arcade


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "TD Blobs"
VIEWPORT_MARGIN = 200

AMBIENT_COLOR = (20, 20, 20)
class Labyrinth(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False)
        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.GRAY)
        self.mouse_sprite = None
        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):
        self.mouse_sprite = arcade.Sprite("Blob Maus.png", scale=1.0)
        self.mouse_visible_in_window = False
        self.mouse_x = self.width // 2
        self.mouse_y = self.height // 2

    def on_mouse_enter(self, x, y):
        self.mouse_x = x
        self.mouse_y = y
        self.mouse_visible_in_window = True

    def on_mouse_leave(self, x, y):
        self.mouse_visible_in_window = False

    def on_update(self, delta_time):
        pass  # Keine automatische Positionsaktualisierung mehr

    def on_draw(self):
        self.clear()
        if self.mouse_sprite and self.mouse_visible_in_window:
            # Hole die aktuelle Mausposition aus Arcade
            self.mouse_x, self.mouse_y = arcade.get_mouse_position()
            # Prüfe, ob die Maus im Fenster ist (und nicht am Rand)
            if 0 < self.mouse_x < self.width - 1 and 0 < self.mouse_y < self.height - 1:
                self.mouse_sprite.center_x = self.mouse_x
                self.mouse_sprite.center_y = self.mouse_y
                self.mouse_sprite.draw()
            else:
                self.mouse_visible_in_window = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y


if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()