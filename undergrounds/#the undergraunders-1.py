import arcade
import random

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "under"
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_X = SCREEN_WIDTH // 2
BUTTON_Y = SCREEN_HEIGHT // 2

ORE_TYPES = ["gold_ore.png", "silver_ore.png", "iron_ore.png"]  # Beispielhafte Erz-Bilder
ORE_COUNT = 10  # Anzahl der Erze, die gespawnt werden sollen


class Labyrinth(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False)
        arcade.set_background_color(arcade.color.CHARCOAL)
        self.button_pressed = False
        self.window_visible = True  # Variable zum Überwachen, ob das Fenster sichtbar ist
        self.audio_player = None  # Variable zum Speichern des Audio-Players
        print("Labyrinth Fenster erstellt")

    def setup(self):
        self.under = arcade.SpriteList()

        # Platzhalter für den Hintergrund
        self.under_grauds1 = arcade.Sprite("under graunds1.png", scale=1)  # Nur ein Dummy-Bild
        self.under_grauds1.center_x = 500
        self.under_grauds1.center_y = 450
        self.under.append(self.under_grauds1)

        self.under_grauds2 = arcade.Sprite("unterer_undergraund.png", scale=1)  # Nur ein Dummy-Bild
        self.under_grauds2.center_x = 500
        self.under_grauds2.center_y = 100
        self.under.append(self.under_grauds2)

        # Entfernen von Sound für den Test, um mögliche Probleme zu vermeiden
        print("Labyrinth Setup abgeschlossen")

    def on_close(self):
        """ Stoppe die Musik, wenn das Fenster geschlossen wird. """
        print("Labyrinth Fenster geschlossen")
        super().on_close()

    def on_draw(self):
        # Zeichenvorgänge nur durchführen, wenn das Fenster sichtbar ist
        if self.window_visible:
            arcade.start_render()
            self.under.draw()

            # Zeichne den Button
            arcade.draw_rectangle_filled(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, arcade.color.BLUE)
            arcade.draw_text("Start Game", BUTTON_X - 80, BUTTON_Y - 10, arcade.color.WHITE, 20)

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"Mausklick bei ({x}, {y})")
        if (BUTTON_X - BUTTON_WIDTH // 2 < x < BUTTON_X + BUTTON_WIDTH // 2 and
                BUTTON_Y - BUTTON_HEIGHT // 2 < y < BUTTON_Y + BUTTON_HEIGHT // 2):
            self.open_new_window()

    def open_new_window(self):
        # Neues Fenster öffnen und Referenz auf das Hauptfenster übergeben
        print("Neues Fenster wird geöffnet...")
        new_game = NewWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "New Game Window", self)
        new_game.setup()

        # Schließe das aktuelle Fenster, statt es unsichtbar zu machen
        self.hide()  # Schließt das Hauptfenster
        print("Labyrinth Fenster geschlossen und neues Fenster gestartet")


class NewWindow(arcade.Window):
    def __init__(self, width, height, title, main_window):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.main_window = main_window  # Referenz auf das Hauptfenster
        self.ore_list = arcade.SpriteList()  # Liste für die Erz-Sprites
        print("NewWindow Fenster erstellt")

    def setup(self):
        print("Neues Fenster Setup gestartet")
        # Erzeuge die Erze in einer Linie
        spacing = SCREEN_WIDTH // ORE_COUNT  # Abstand zwischen den Erzen
        y_position = SCREEN_HEIGHT // 2  # Y-Position für alle Erze (mittig im Bildschirm)

        for i in range(ORE_COUNT):
            ore_image = random.choice(ORE_TYPES)  # Wähle zufällig eine Erz-Art
            ore = arcade.Sprite(ore_image, 0.5)  # Erstelle das Erz-Sprite, skalierbar mit 0.5
            ore.center_x = spacing * i + spacing // 2  # Gleichmäßige X-Positionierung
            ore.center_y = y_position  # Y-Position bleibt konstant
            self.ore_list.append(ore)  # Erz-Sprite zur Liste hinzufügen
        print("Neues Fenster Setup abgeschlossen")

    def on_close(self):
        """ Stoppe die Musik, wenn dieses Fenster geschlossen wird. """
        print("NewWindow Fenster geschlossen")
        super().on_close()

    def on_draw(self):
        arcade.start_render()
        self.ore_list.draw()  # Zeichne alle Erze


if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
#get_window