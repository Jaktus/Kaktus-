import arcade
import time
import random

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800
SCREEN_TITLE = "td"

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, update_rate=1/260)
        self.blist = arcade.SpriteList()
        self.overlist = arcade.SpriteList()
        self.kugellist = arcade.SpriteList()
        self.warum = arcade.Sprite("btFeld.png")
        self.warum.center_x = 550
        self.warum.center_y = 400
        self.last_shot_time = 0
        self.spielgestartet = False
        self.Geld = 10000000
        self.leben = 20000000000

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.Geld >= 250:
            turm = arcade.Sprite("horror.png", 1)
            turm.center_x = x
            turm.center_y = y
            self.overlist.append(turm)
            self.Geld -= 250
            if not self.spielgestartet:
                self.spielgestartet = True

    def on_update(self, delta_time: float):
        if self.spielgestartet and random.randint(1, 1) == 1:
            ballon = arcade.Sprite("btballon.png")
            ballon.center_x = 75
            ballon.center_y = 770
            ballon.change_y = -1
            self.blist.append(ballon)

        for ballon in self.blist:
            if ballon.center_x == 75 and ballon.center_y == 675:
                ballon.change_x = 1
                ballon.change_y = 0
            elif ballon.center_x == 275 and ballon.center_y == 675:
                ballon.change_x = 0
                ballon.change_y = -1
            elif ballon.center_x == 275 and ballon.center_y == 525:
                ballon.change_x = -1
                ballon.change_y = 0
            elif ballon.center_x == 75 and ballon.center_y == 525:
                ballon.change_x = 0
                ballon.change_y = -1
            elif ballon.center_x == 75 and ballon.center_y == 375:
                ballon.change_x = 1
                ballon.change_y = 0
            elif ballon.center_x == 275 and ballon.center_y == 375:
                ballon.change_x = 0
                ballon.change_y = -1
            elif ballon.center_x == 275 and ballon.center_y == 225:
                ballon.change_x = -1
                ballon.change_y = 0
            elif ballon.center_x == 75 and ballon.center_y == 225:
                ballon.change_x = 0
                ballon.change_y = -1
            elif ballon.center_x == 75 and ballon.center_y == 75:
                ballon.change_x = 1
                ballon.change_y = 0
            elif ballon.center_x == 475 and ballon.center_y == 75:
                ballon.change_x = 0
                ballon.change_y = 1
            elif ballon.center_x == 475 and ballon.center_y == 725:
                ballon.change_x = 1
                ballon.change_y = 0
            elif ballon.center_x == 1025 and ballon.center_y == 725:
                ballon.change_x = 0
                ballon.change_y = 1

        for kugel in self.kugellist:
            treffer = arcade.check_for_collision_with_list(kugel, self.blist)
            for ballon in treffer:
                ballon.kill()
                kugel.kill()
                self.Geld += 5

        current_time = time.time()
        if current_time - self.last_shot_time >= 0.9:
            for turm in self.overlist:
                if len(self.blist) == 0:
                    continue
                ziel, _ = arcade.get_closest_sprite(turm, self.blist)
                dx = ziel.center_x - turm.center_x
                dy = ziel.center_y - turm.center_y
                distanz = (dx ** 2 + dy ** 2) ** 0.5
                if distanz == 0:
                    continue
                dx /= distanz
                dy /= distanz
                kugel = arcade.Sprite("red.png", 0.6)
                kugel.center_x = turm.center_x
                kugel.center_y = turm.center_y
                kugel.change_x = dx * 4
                kugel.change_y = dy * 4
                self.kugellist.append(kugel)
            self.last_shot_time = current_time

        self.blist.update()
        self.kugellist.update()

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.warum)
        self.blist.draw()
        self.overlist.draw()
        self.kugellist.draw()

        arcade.draw_text(f"Leben: {self.leben}", 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20, bold=True)
        arcade.draw_text(f"Geld: {self.Geld}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20, bold=True)

if __name__ == "__main__":
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
