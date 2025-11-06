import arcade
from arcade.future.light import Light, LightLayer

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Labyrinth"
VIEWPORT_MARGIN = 200

# ...existing code...
import arcade

# Versuch, die Licht-API kompatibel zu importieren (verschiedene arcade-Versionen)
try:
    from arcade.experimental.light import Light, LightLayer
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
        # Sprite-Listen
        self.spieler_liste = arcade.SpriteList()
        self.lavablockliste = arcade.SpriteList()
        self.timliste = arcade.SpriteList()
        self.münzenliste = arcade.SpriteList()
        self.teleportarlist = arcade.SpriteList()

        # Spieler
        self.spieler = arcade.Sprite("ice.png")
        self.spieler.center_x = 75
        self.spieler.center_y = 475
        self.spieler_liste.append(self.spieler)

        # Lavalavablocks: Erstelle Rahmen + einige interne Blöcke programmgesteuert
        grid = range(25, 500, 50)
        # Randblöcke
        for x in grid:
            self.lavablockliste.append(self._make_block(x, 25))
            self.lavablockliste.append(self._make_block(x, 475))
        for y in grid:
            self.lavablockliste.append(self._make_block(25, y))
            self.lavablockliste.append(self._make_block(475, y))

        # Einige interne Hindernisse (Beispiel-Layout, kann angepasst werden)
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
            # Prüfe Duplikate nicht nötig, SpriteList kann doppelte Sprites enthalten, aber vermeide unnötige Verdopplung
            self.lavablockliste.append(self._make_block(x, y))

        # Tor
        self.tor = arcade.Sprite("tor.png")
        self.tor.center_x = 375
        self.tor.center_y = 25
        self.lavablockliste.append(self.tor)

        # Physik
        self.physik_engine = arcade.PhysicsEngineSimple(self.spieler, self.lavablockliste)

        # Spielzustand
        self.zeit = 10
        self.punkte = 0

        # Zeit-Powerups
        t = arcade.Sprite("time.png")
        t.center_x = 425
        t.center_y = 375
        self.timliste.append(t)

        t = arcade.Sprite("time.png")
        t.center_x = 75
        t.center_y = 225
        self.timliste.append(t)

        # Münzen
        m = arcade.Sprite("münze.png")
        m.center_x = 75
        m.center_y = 175
        self.münzenliste.append(m)

        m = arcade.Sprite("münze.png")
        m.center_x = 75
        m.center_y = 325
        self.münzenliste.append(m)

        m = arcade.Sprite("münze.png")
        m.center_x = 325
        m.center_y = 75
        self.münzenliste.append(m)

        # Teleport (ein Block-Koordinate als Trigger)
        tele = arcade.Sprite("lavablock.png")
        tele.center_x = 375
        tele.center_y = 425
        self.teleportarlist.append(tele)

        # Licht (wenn verfügbar)
        if LightLayer is not None and Light is not None:
            self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.light_layer.set_background_color(arcade.color.BLACK)
            radius = 150
            mode = 'soft'
            color = arcade.csscolor.WHITE
            self.player_light = Light(0, 0, radius, color, mode)
            # standardmäßig Licht aktiv
            self.light_layer.add(self.player_light)
        else:
            self.light_layer = None
            self.player_light = None

    def _make_block(self, x, y):
        b = arcade.Sprite("lavablock.png")
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
            # Light toggle (falls Licht verfügbar)
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
        # Spiel läuft nur, solange Zeit > 0 und Spieler nicht unten am Ausgang
        if self.zeit > 0 and self.spieler.center_y > 25:
            # Update Bewegung & Kollision
            self.spieler_liste.update()
            self.physik_engine.update()

            self.zeit -= delta_time

            # Kollisionen mit Zeit-Powerups
            hitliste = arcade.check_for_collision_with_list(self.spieler, self.timliste)
            for time in hitliste:
                self.zeit += 5
                time.kill()

            # Kollisionen mit Münzen
            hitliste = arcade.check_for_collision_with_list(self.spieler, self.münzenliste)
            for münze in hitliste:
                self.punkte += 1
                münze.kill()

            # Teleport
            hitliste = arcade.check_for_collision_with_list(self.spieler, self.teleportarlist)
            for _ in hitliste:
                self.spieler.center_x = 425
                self.spieler.center_y = 75

            # Wenn alle Münzen gesammelt sind, öffne das Tor
            if len(self.münzenliste) == 0 and self.tor in self.lavablockliste:
                self.tor.kill()

        # Lichtposition aktualisieren (falls vorhanden)
        if self.player_light is not None:
            # Light erwartet eine (x, y)-Position
            try:
                self.player_light.position = (self.spieler.center_x, self.spieler.center_y)
            except Exception:
                # ältere/neue APIs können andere Property-Namen verwenden
                pass

    def on_draw(self):
        self.clear()

        # Zuerst alle statischen Objekte ohne Licht (optional)
        self.lavablockliste.draw()
        self.timliste.draw()
        self.münzenliste.draw()
        self.teleportarlist.draw()

        # Wenn Lichtschicht vorhanden, zeichne relevante Sprites in der Licht-Schicht
        if self.light_layer is not None:
            with self.light_layer:
                # Dinge, die vom Licht beeinflusst werden sollen
                self.lavablockliste.draw()
                self.spieler.draw()
                self.timliste.draw()
                self.münzenliste.draw()
                self.teleportarlist.draw()
                # Tor wurde evtl. entfernt; draw() ist sicher
                try:
                    self.tor.draw()
                except Exception:
                    pass
            # Licht über die Szene anwenden
            self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        else:
            # Kein Licht-Modul verfügbar: Spieler normal zeichnen
            self.spieler_liste.draw(pixelated=True)

        # HUD
        arcade.draw_text(str(round(self.zeit)), 15, 20, arcade.color.WHITE, 14)
        arcade.draw_text(str(round(self.punkte)), 475, 20, arcade.color.WHITE, 14)

        if self.zeit <= 0:
            arcade.draw_text("schlecht", 250, 250, font_size=50, font_name="Kenney Future", anchor_x="center", anchor_y="center")
        if self.spieler.center_y <= 25:
            arcade.draw_text("gut", 250, 250, font_name="Kenney Future", font_size=50, anchor_x="center", anchor_y="center")
# ...existing code...
if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()