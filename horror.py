import arcade


class Spiel(arcade.Window):
    def __init__(self):
        super().__init__(700, 500, "Horror lauf")

        arcade.set_background_color(arcade.color.DARK_GREEN)

        self.horror = arcade.Sprite("horror.png")
        self.horror.center_x = 25
        self.horror.center_y = 25

        self.Olafholz = arcade.Sprite("Olafholz.png")
        self.Olafholz.center_x = 350
        self.Olafholz.center_y = 350

        self.lil = arcade.Sprite("lil.png")
        self.lil.center_x = 675
        self.lil.center_y = 25
        


        
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.Olafholz.change_y = 5
        if symbol == arcade.key.A:
            self.Olafholz.change_x = -5
        if symbol == arcade.key.S:
            self.Olafholz.change_y = -5
        if symbol == arcade.key.D:
            self.Olafholz.change_x = 5

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.Olafholz.change_y = 0
        if symbol == arcade.key.A:
            self.Olafholz.change_x = 0
        if symbol == arcade.key.S:
            self.Olafholz.change_y = 0
        if symbol == arcade.key.D:
            self.Olafholz.change_x = 0
    def on_update(self, delta_time):
        self.Olafholz.update()

    def on_draw(self):
        self.clear()
        self.horror.draw()
        self.Olafholz.draw()
        self.lil.draw()

Spiel()
arcade.run()