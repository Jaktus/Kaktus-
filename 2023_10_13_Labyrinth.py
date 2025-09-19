import arcade
from arcade.future.light import Light, LightLayer

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

        self.light_layer = None

    def setup(self):

        # Wir erstellen eine neue Liste für die Spielfigur
        self.spieler_liste = arcade.SpriteList()

        # Wir erstellen die Spielfigur (sie besitzt die Grafik "spieler.png")
        self.spieler = arcade.Sprite("ice.png")
        # Wir positionieren die Spielfigur im Eingang des Labyrinths
        self.spieler.center_x = 75
        self.spieler.center_y = 475
        # Wir fügen die Spielfigur der dafür erstellten Liste hinzu
        self.spieler_liste.append(self.spieler)

        # Wir erstellen eine neue Sprite-Liste und speichern diese in der Variable self.lavalavablock_liste
        self.lavablockliste = arcade.SpriteList()

        # Linke Wand
        lavalavablock = arcade.Sprite("lavablock.png")
        # Wir platzieren den Lavalavablock an die Position (x=25, y=25)
        lavalavablock.center_x = 25
        lavalavablock.center_y = 25
    
        # Wir fügen den Lavalavablock der Lavalavablockliste hinzu
        self.lavablockliste.append(lavalavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 75
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 175
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 275
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 325
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 425
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 25
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 75
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 75
        lavablock.center_y = 75
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 75
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 75
        lavablock.center_y = 275
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 75
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 125
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 125
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 125
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 125
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 75
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 175
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 325
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 175
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 225
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 225
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 75
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 275
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 425
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 275
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 175
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 425
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 325
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 375
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 375
        lavablock.center_y = 325
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 375
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 425
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 425
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 425
        lavablock.center_y = 425
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 425
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 25
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 75
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 125
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 175
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 225
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 275
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 325
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 375
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 425
        self.lavablockliste.append(lavablock)

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 475
        lavablock.center_y = 475
        self.lavablockliste.append(lavablock)





        self.tor = arcade.Sprite("tor.png")
        self.tor.center_x = 375
        self.tor.center_y = 25
        self.lavablockliste.append(self.tor)

        self.physik_engine = arcade.PhysicsEngineSimple(self.spieler, self.lavablockliste)
        self.zeit = 10   

        self.punkte = 0

        self.timliste = arcade.SpriteList()

        time = arcade.Sprite("time.png")
        time.center_x = 425
        time.center_y = 375
        self.timliste.append(time)

        time = arcade.Sprite("time.png")
        time.center_x = 75
        time.center_y = 225
        self.timliste.append(time)

        self.münzenliste = arcade.SpriteList()

        self.münze = arcade.Sprite("münze.png")
        self.münze.center_x = 75
        self.münze.center_y = 175
        self.münzenliste.append(self.münze)

        self.münze = arcade.Sprite("münze.png")
        self.münze.center_x = 75
        self.münze.center_y = 325
        self.münzenliste.append(self.münze)

        self.münze = arcade.Sprite("münze.png")
        self.münze.center_x = 325
        self.münze.center_y = 75
        self.münzenliste.append(self.münze)

        self.teleportarlist = arcade.SpriteList()

        lavablock = arcade.Sprite("lavablock.png")
        lavablock.center_x = 375
        lavablock.center_y = 425
        self.teleportarlist.append(lavablock)

        




        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.light_layer.set_background_color(arcade.color.BLACK)

        radius = 150
        mode = 'soft'
        color = arcade.csscolor.WHITE
        self.player_light = Light(0, 0, radius, color, mode)

    # Die Funktion on_key_press wird automatisch immer dann ausgeführt, wernn der Spieler eine Taste drückt
    # symbol enthält die gedrückte Taste
    def on_key_press(self, symbol, modifiers):
        # Falls Pfeiltaste-Oben gedrückt wurde, bekommt der Spieler 5 Geschwindigkeit in y-Richtung (nach oben)
        if symbol == arcade.key.W:
            self.spieler.change_y = 3
        if symbol == arcade.key.S:
            self.spieler.change_y = -3
        if symbol == arcade.key.A:
            self.spieler.change_x = -3
        if symbol == arcade.key.D:
            self.spieler.change_x = 3
        elif symbol == arcade.key.SPACE:
            # --- Light related ---
            # We can add/remove lights from the light layer. If they aren't
            # in the light layer, the light is off.
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.spieler.change_y = 0
        if symbol == arcade.key.A:
            self.spieler.change_x = 0
        if symbol == arcade.key.S:  
            self.spieler.change_y = 0
        if symbol == arcade.key.D:
            self.spieler.change_x = 0

    def on_update(self, delta_time):
        
            if self.zeit > 0 and self.spieler.center_y > 25:
                self.spieler_liste.update()


                self.physik_engine.update() #######

                self.zeit = self.zeit - delta_time
            

                hitliste =  arcade.check_for_collision_with_list(self.spieler, self.timliste)
                for time in hitliste:
                    self.zeit += 5
                    time.kill()                            

                hitliste = arcade.check_for_collision_with_list(self.spieler, self.münzenliste)
                for münze in hitliste:
                    self.punkte += 1
                    münze.kill()



                hitliste = arcade.check_for_collision_with_list(self.spieler, self.teleportarlist)
                for lavablock in hitliste:
                    self.spieler.center_x = 425
                    self.spieler.center_y = 75

                if len(self.münzenliste) == 0:
                    self.tor.kill()
            self.player_light.position = self.spieler.position



          

    # on_draw wird die gaanze Zeit während des Spiels ausgeführt und ist für das Zeichnen der im Spiel vorkommenden Dinge zusätndig
    def on_draw(self):
        self.clear()

        # Wir zeichnen alle Blöcke in der Lavalavablockliste
        self.lavablockliste.draw()
        self.timliste.draw()
        self.münzenliste.draw()
        self.teleportarlist.draw()
        self.tor.draw()

        with self.light_layer:
            self.lavablockliste.draw()
            self.spieler.draw()
            self.timliste.draw()
            self.münzenliste.draw()
            self.teleportarlist.draw()
            self.tor.draw()
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)
        # Wir zeichnen die sich in spieler_liste befindliche Spielfigur
        self.spieler_liste.draw(pixelated=True)

        arcade.draw_text(round(self.zeit), 15, 20)

        if self.zeit <= 0:
            arcade.draw_text("schlecht", 250, 250, font_size=50, font_name="Kenney Future", anchor_x="center", anchor_y="center")
        if self.spieler.center_y <= 25:
            arcade.draw_text("gut", 250, 250, font_name="Kenney Future", font_size=50, anchor_x="center", anchor_y="center")  

        arcade.draw_text(round(self.punkte), 475, 20)


if __name__ == "__main__":
    window = Labyrinth(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()