import arcade

class Labyrinth(arcade.Window):
    # __init__ wird einmal ganz zu Beginn ausgeführt
    def __init__(self):
        # Wir setzen Breite und Höhe auf 500 und den Titel auf "Labyrinth"
        super().__init__(500, 500, "Labyrinth")

        arcade.set_background_color(arcade.color.YELLOW_GREEN)

        # Wir erstellen eine neue Liste für die Spielfigur
        self.spieler_liste = arcade.SpriteList()

        # Wir erstellen die Spielfigur (sie besitzt die Grafik "spieler.png")
        self.spieler = arcade.Sprite("spieler.png", 1.7)
        # Wir positionieren die Spielfigur im Eingang des Labyrinths
        self.spieler.center_x = 75
        self.spieler.center_y = 475
        # Wir fügen die Spielfigur der dafür erstellten Liste hinzu
        self.spieler_liste.append(self.spieler)

        # Wir erstellen eine neue Sprite-Liste und speichern diese in der Variable self.lavalavablock_liste
        self.waterliste = arcade.SpriteList()
        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 125
        self.waterliste.append(water)


        self.physik_engine = arcade.PhysicsEngineSimple(self.spieler, self.waterliste)

        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 125
        self.waterliste.append(water)


        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 25
        water.center_y = 375
        self.waterliste.append(water)
#nechste
        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 125
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 375
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 75
        water.center_y = 125
        self.waterliste.append(water)
#nechste
        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 125
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 125
        water.center_y = 375
        self.waterliste.append(water)
#nechste

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 125
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 375
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 175
        water.center_y = 125
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 125
        self.waterliste.append(water)


        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 225
        water.center_y = 375
        self.waterliste.append(water)


#nechste
        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 125
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 375
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 275
        water.center_y = 125
        self.waterliste.append(water)


        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 125
        self.waterliste.append(water)

#nechste
        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 325
        water.center_y = 375
        self.waterliste.append(water)
#nechste


        water = arcade.Sprite("water.png")
        water.center_x = 375
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 375
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 375
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 375
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 375
        water.center_y = 375
        self.waterliste.append(water)
#nechste

        water = arcade.Sprite("water.png")
        water.center_x = 425
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 425
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 425
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 425
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 425
        water.center_y = 375
        self.waterliste.append(water)
#nechste
        
        water = arcade.Sprite("water.png")
        water.center_x = 475
        water.center_y = 175
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 475
        water.center_y = 225
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 475
        water.center_y = 275
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 475
        water.center_y = 325
        self.waterliste.append(water)

        water = arcade.Sprite("water.png")
        water.center_x = 475
        water.center_y = 375
        self.waterliste.append(water)


        self.zeit = 10 


        self.punkte = 0

        hebel = arcade.Sprite("hebel.png")
        hebel.center_x = 325
        hebel.center_y = 475


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
        

        if (self.spieler,self.spieler.center_y > 500):
            self.spieler_liste.update()
            self.spieler.texture = arcade.load_texture("spielar.png")




            
            
                

    # on_draw wird die gaanze Zeit während des Spiels ausgeführt und ist für das Zeichnen der im Spiel vorkommenden Dinge zusätndig
    def on_draw(self):
        self.clear()

        # Wir zeichnen alle Blöcke in der Lavalavablockliste




        self.waterliste.draw()

        # Wir zeichnen die sich in spieler_liste befindliche Spielfigur
        self.spieler_liste.draw(pixelated=True)

        arcade.draw_text(round(self.zeit), 15, 20)

        if self.zeit <= 0:
            arcade.draw_text("schlecht", 250, 250, font_size=50, font_name="Kenney Future", anchor_x="center", anchor_y="center")
        if self.spieler.center_y <= 25:
            arcade.draw_text("gut", 250, 250, font_name="Kenney Future", font_size=50, anchor_x="center", anchor_y="center")  

        arcade.draw_text(round(self.punkte), 475, 20)

Labyrinth()

arcade.run()