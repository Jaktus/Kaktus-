import arcade
from arcade.future.light import Light, LightLayer
from pathlib import Path

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Labyrinth"
VIEWPORT_MARGIN = 200
SCRIPT_DIR = Path(__file__).parent

import arcade

try:
    from arcade.future.light import Light, LightLayer
except ImportError:
    try:
        from arcade.future.light import Light, LightLayer
    except ImportError:
        Light = None
        LightLayer = None

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Labyrinth"
VIEWPORT_MARGIN = 200

AMBIENT_COLOR = (20, 20, 20)


class Labyrinth(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=False)
        arcade.set_background_color(arcade.color.CHARCOAL)

        self.light_layer = None

    def setup(self):
        self.spieler_liste = arcade.SpriteList()
        self.lavablockliste = arcade.SpriteList()
        self.timliste = arcade.SpriteList()
        self.münzenliste = arcade.SpriteList()
        self.teleportarlist = arcade.SpriteList()

        self.spieler = arcade.Sprite(str(SCRIPT_DIR / "ice.png"))
        self.spieler.center_x = 75
        self.spieler.center_y = 475
        self.spieler_liste.append(self.spieler)

        grid = range(25, 500, 50)
        for x in grid:
            self.lavablockliste.append(self._make_block(x, 25))
            self.lavablockliste.append(self._make_block(x, 475))
        for y in grid:
            self.lavablockliste.append(self._make_block(25, y))
            self.lavablockliste.append(self._make_block(475, y))

        interne = [
            (75, 25), (75, 75), (75, 125), (75, 275), (75, 375),
            (125, 25), (125, 225), (125, 375), (125, 475),
            (175, 25), (175, 75), (175, 175), (175, 225), (175, 325), (175, 375), (175, 475),
            (225, 25), (225, 475),
            (275, 25), (275, 75), (275, 125), (275, 225), (275, 275), (275, 375), (275, 425), (275, 475),
            (325, 25), (325, 125), (325, 175), (325, 225), (325, 375), (325, 425), (325, 475),
            (375, 125), (375, 325), (375, 475),
            (425, 25), (425, 225), (425, 425),
            (475, 25), (475, 75), (475, 125), (475, 175), (475, 225), (475, 275), (475, 325), (475, 375), (475, 425), (475, 475),
        ]
        for x, y in interne:
            self.lavablockliste.append(self._make_block(x, y))

        self.tor = arcade.Sprite(str(SCRIPT_DIR / "tor.png"))
        self.tor.center_x = 375
        self.tor.center_y = 25
        self.lavablockliste.append(self.tor)

        self.physik_engine = arcade.PhysicsEngineSimple(self.spieler, self.lavablockliste)

        self.zeit = 10
        self.punkte = 0

        t = arcade.Sprite(str(SCRIPT_DIR / "time.png"))
        t.center_x = 25
        t.center_y = 475
        self.timliste.append(t)

        t = arcade.Sprite(str(SCRIPT_DIR / "time.png"))
        t.center_x = 75
        t.center_y = 225
        self.timliste.append(t)

        m = arcade.Sprite(str(SCRIPT_DIR / "münze.png"))
        m.center_x = 100
        m.center_y = 475
        self.münzenliste.append(m)

        m = arcade.Sprite(str(SCRIPT_DIR / "münze.png"))
        m.center_x = 150
        m.center_y = 475
        self.münzenliste.append(m)

        m = arcade.Sprite(str(SCRIPT_DIR / "münze.png"))
        m.center_x = 325
        m.center_y = 75
        self.münzenliste.append(m)

        tele = arcade.Sprite(str(SCRIPT_DIR / "lavablock.png"))
        tele.center_x = 375
        tele.center_y = 425
        self.teleportarlist.append(tele)

        if LightLayer is not None and Light is not None:
            self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.light_layer.set_background_color(arcade.color.BLACK)
            radius = 150
            mode = 'soft'
            color = arcade.csscolor.WHITE
            self.player_light = Light(0, 0, radius, color, mode)
            self.light_layer.add(self.player_light)
        else:
            self.light_layer = None
            self.player_light = None

    def _make_block(self, x, y):
        b = arcade.Sprite(str(SCRIPT_DIR / "lavablock.png"))
        b.center_x = x
        b.center_y = y
        return b

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.spieler.change_y = 3
        if symbol == arcade.key.S:
            self.spieler.change_y = -3
        if symbol == arcade.key.A:
            self.spieler.change_x = -3
        if symbol == arcade.key.D:
            self.spieler.change_x = 3
        if symbol == arcade.key.SPACE:
            if self.light_layer is not None and self.player_light is not None:
                if self.player_light in self.light_layer:
                    self.light_layer.remove(self.player_light)
                else:
                    self.light_layer.add(self.player_light)

    def on_key_release(self, symbol, modifiers):
        if symbol in (arcade.key.W, arcade.key.S):
            self.spieler.change_y = 0
        if symbol in (arcade.key.A, arcade.key.D):
            self.spieler.change_x = 0

    def on_update(self, delta_time):
        if self.zeit > 0 and self.spieler.center_y > 25:
            self.spieler_liste.update()
            self.physik_engine.update()

            self.zeit -= delta_time

            hitliste = arcade.check_for_collision_with_list(self.spieler, self.timliste)
            for time in hitliste:
                self.zeit += 5
                time.kill()

            hitliste = arcade.check_for_collision_with_list(self.spieler, self.münzenliste)
            for münze in hitliste:
                self.punkte += 1
                münze.kill()

            hitliste = arcade.check_for_collision_with_list(self.spieler, self.teleportarlist)
            for _ in hitliste:
                self.spieler.center_x = 425
                self.spieler.center_y = 75

            if len(self.münzenliste) == 0 and self.tor in self.lavablockliste:
                self.tor.kill()

        if self.player_light is not None:
            try:
                self.player_light.position = (self.spieler.center_x, self.spieler.center_y)
            except Exception:
                pass

    def on_draw(self):
        self.clear()

        self.lavablockliste.draw()
        self.timliste.draw()
        self.münzenliste.draw()
        self.teleportarlist.draw()
        self.spieler_liste.draw(pixelated=True)

        if self.light_layer is not None:
            with self.light_layer:
                self.lavablockliste.draw()
                self.timliste.draw()
                self.münzenliste.draw()
                self.teleportarlist.draw()
            self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        arcade.draw_text(str(round(self.zeit)), 15, 20, arcade.color.WHITE, 14)
        arcade.draw_text(str(round(self.punkte)), 475, 20, arcade.color.WHITE, 14)

        if self.zeit <= 0:
            arcade.draw_text("schlecht", 250, 250, font_size=50, font_name="Kenney Future", anchor_x="center", anchor_y="center")
        if self.spieler.center_y <= 25:
            arcade.draw_text("gut", 250, 250, font_name="Kenney Future", font_size=50, anchor_x="center", anchor_y="center")
if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()