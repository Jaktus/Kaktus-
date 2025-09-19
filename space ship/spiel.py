import random
import arcade

# --- Konstanten ---
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Space Ship"

class InstructionView(arcade.View):
    """ Startbildschirm / Menü """

    def on_show_view(self):
        self.window.set_mouse_visible(True)
        self.window.background_color = arcade.color.DARK_SLATE_BLUE
        self.window.default_camera.use()

    def on_draw(self):
        self.clear()
        arcade.draw_text("Willkommen zu meinem Spiel", self.window.width / 2, self.window.height / 2 + 50,
                         arcade.color.WHITE, font_size=40, anchor_x="center")
        arcade.draw_text("Klicke zum Starten", self.window.width / 2, self.window.height / 2 - 50,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, x, y, button, modifiers):
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class GameView(arcade.View):
    """ Das Spiel mit Spieler, Gut/Schlecht-Objekten und Punktestand """

    def __init__(self):
        super().__init__()
        self.spieler_liste = arcade.SpriteList()
        self.GoB = arcade.SpriteList()
        self.spieler = None
        self.score = 0
        self.score_text = None

    def setup(self):
        arcade.set_background_color(arcade.color.CHARCOAL)


        self.spieler = arcade.Sprite("spieler.png", 1.75)
        self.spieler.center_x = self.window.width / 2
        self.spieler.center_y = 125
        self.spieler_liste.append(self.spieler)


        self.score_text = arcade.Text(f"Punkte: {self.score}", 20, self.window.height - 40,
                                      arcade.color.WHITE, 20)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.Q:
            arcade.close_window()
        if symbol == arcade.key.D:
            self.spieler.change_x = 7
        if symbol == arcade.key.A:
            self.spieler.change_x = -7

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.A:
            self.spieler.change_x = 0
        if symbol == arcade.key.D:
            self.spieler.change_x = 0

    def on_update(self, delta_time):
        self.spieler_liste.update()
        self.GoB.update()

        if self.spieler.left < 0:
            self.spieler.left = 0
        if self.spieler.right < self.width:
            self.spieler = self.width


        if random.randint(1, 20) == 1:
            g = arcade.Sprite("Gut.png", 0.5)
            g.center_x = random.randint(50, self.window.width - 50)
            g.center_y = self.window.height + 50
            g.change_y = -2
            g.typ = "gut"  
            self.GoB.append(g)


        if random.randint(1, 20) == 1:
            s = arcade.Sprite("Schlecht.png", 0.5)
            s.center_x = random.randint(50, self.window.width - 50)
            s.center_y = self.window.height + 50
            s.change_y = -1.5
            s.typ = "schlecht"
            self.GoB.append(s)

        # Kollision prüfen
        for objekt in self.GoB:
            if arcade.check_for_collision(self.spieler, objekt):
                if getattr(objekt, "typ", "") == "gut":
                    self.score += 1
                else:
                    self.score -= 1
                objekt.remove_from_sprite_lists()

        self.score_text.text = f"Punkte: {self.score}"

    def on_draw(self):
        self.clear()
        self.spieler_liste.draw()
        self.GoB.draw()
        self.score_text.draw()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
