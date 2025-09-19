#the undergraunders
import arcade

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Labyrinth"
VIEWPORT_MARGIN = 200

AMBIENT_COLOR = (20, 20, 20)
class Labyrinth(arcade.Window):
    # __init__ wird einmal ganz zu Beginn ausgeführt
    def __init__(self, width, height, title):
        # Wir setzen Breite und Höhe auf 500 und den Titel auf "Labyrinth"
        super().__init__(width, height, title, resizable=False)

        arcade.set_background_color(arcade.color.CHARCOAL)

    def setup(self):

        
        self.audio = arcade.load_sound("underground-eerie-club-127491.wav")
        arcade.play_sound(self.audio)


if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()