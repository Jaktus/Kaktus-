import arcade

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()

        self.camera = arcade.Camera2D()
        self.camera.match_window()

        self.spieler_list = arcade.SpriteList()

        self.mensch = arcade.Sprite("fleisch-stück.png", 1.2)
        self.mensch.center_x = 100
        self.mensch.center_y = 125
        self.spieler_list.append(self.mensch)

        self.map = arcade.load_tilemap("levle.tmx", scaling=1, layer_options={
            "Tile Layer 1": {"use_spatial_hash": True}
        })
        self.scene = arcade.Scene.from_tilemap(self.map)

        self.spiel_physik = arcade.PhysicsEngineSimple(
            self.mensch,
            self.scene["Tile Layer 3"]
        )

        self.v_rennen = [
            arcade.load_texture("v_renen1.png"),
            arcade.load_texture("v_renen2.png"),
            arcade.load_texture("v_renen3.png"),
            arcade.load_texture("v_renen4.png"),
            arcade.load_texture("v_renen5.png")
        ]
        self.h_rennen = [
            arcade.load_texture("h_renen1.png"),
            arcade.load_texture("h_renen2.png"),
            arcade.load_texture("h_renen3.png"),
            arcade.load_texture("h_renen4.png"),
            arcade.load_texture("h_renen5.png")
        ]

        self.l_rennen = [
            arcade.load_texture("l_renen1.png"),
            arcade.load_texture("l_renen2.png"),
            arcade.load_texture("l_renen3.png"),
            arcade.load_texture("l_renen4.png"),
            arcade.load_texture("l_renen5.png")
        ]

        self.r_rennen = [
            arcade.load_texture("r_renen1.png"),
            arcade.load_texture("r_renen2.png"),
            arcade.load_texture("r_renen3.png"),
            arcade.load_texture("r_renen4.png"),
            arcade.load_texture("r_renen5.png")
        ]


        self.letzte_richtung = "idle"
        self.stop_animation_index = 0
        self.stop_animation_timer = 0
        self.stop_animation_aktiv = False
        self.animations_timer = 0
        self.texture_index = 0

    def scroll_to_player(self):
        ziel_position_x = self.mensch.center_x
        ziel_position_y = self.mensch.center_y

        if self.mensch.center_x < 450:
            ziel_position_x = 450 
        if self.mensch.center_x > 1150:
            ziel_position_x = 1150
        if self.mensch.center_y < 350:
            ziel_position_y = 350
        if self.mensch.center_y > 350:
            ziel_position_y = 350

        self.camera.position = (ziel_position_x, ziel_position_y)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.mensch.change_y = 3
        elif symbol == arcade.key.S:
            self.mensch.change_y = -3
        elif symbol == arcade.key.A:
            self.mensch.change_x = -3
        elif symbol == arcade.key.D:
            self.mensch.change_x = 3

    def on_key_release(self, symbol, modifiers):
        if symbol in [arcade.key.W, arcade.key.S]:
            self.mensch.change_y = 0
        elif symbol in [arcade.key.A, arcade.key.D]:
            self.mensch.change_x = 0

    def on_update(self, delta_time):
        self.spieler_list.update()
        self.spiel_physik.update()
        self.scroll_to_player()

        self.animations_timer += delta_time

        if self.mensch.change_x < 0:
            self.letzte_richtung = "links"
        elif self.mensch.change_x > 0:
            self.letzte_richtung = "rechts"
        elif self.mensch.change_y > 0:
            self.letzte_richtung = "oben"
        elif self.mensch.change_y < 0:
            self.letzte_richtung = "unten"

        if self.mensch.change_x != 0 or self.mensch.change_y != 0:
            self.stop_animation_aktiv = False
            if self.animations_timer > 0.10:
                self.texture_index = (self.texture_index + 1) % 5
                self.animations_timer = 0

                if self.letzte_richtung == "links":
                    self.mensch.texture = self.h_rennen[self.texture_index]
                elif self.letzte_richtung == "rechts":
                    self.mensch.texture = self.v_rennen[self.texture_index]
                elif self.letzte_richtung == "oben":
                    self.mensch.texture = self.l_rennen[self.texture_index]
                elif self.letzte_richtung == "unten":
                    self.mensch.texture = self.r_rennen[self.texture_index]

        else:
            if not self.stop_animation_aktiv:
                self.stop_animation_aktiv = True
                self.stop_animation_index = 0
                self.stop_animation_timer = 0

            self.stop_animation_timer += delta_time
            if self.stop_animation_index < 2 and self.stop_animation_timer > 0.0015:
                self.stop_animation_timer = 0
                self.stop_animation_index += 1

                if self.letzte_richtung == "links":
                    self.mensch.texture = self.h_rennen[self.stop_animation_index]
                elif self.letzte_richtung == "rechts":
                    self.mensch.texture = self.v_rennen[self.stop_animation_index]
                elif self.letzte_richtung == "oben":
                    self.mensch.texture = self.l_rennen[self.stop_animation_index]
                elif self.letzte_richtung == "unten":
                    self.mensch.texture = self.r_rennen[self.stop_animation_index]
            elif self.stop_animation_index >= 2:
                if self.letzte_richtung == "links":
                    self.mensch.texture = self.h_rennen[2]
                elif self.letzte_richtung == "rechts":
                    self.mensch.texture = self.v_rennen[2]
                elif self.letzte_richtung == "oben":
                    self.mensch.texture = self.l_rennen[2]
                elif self.letzte_richtung == "unten":
                    self.mensch.texture = self.r_rennen[2]

        if self.mensch.collides_with_list(self.scene["Tile Layer 2"]):
            target_x =  450
            target_y =  350
            self.camera.position = (target_x, target_y)
            if self.camera.position == (target_x, target_y):
                self.mensch.stop()
                Shop_ansicht = Shop()
                self.window.show_view(Shop_ansicht)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.spieler_list.draw()

class Shop(arcade.View):
    def __init__(self):
        super().__init__()

        self.sho_list = arcade.SpriteList()

        # hintergrund
        self.mensch = arcade.Sprite("shop hintergrund.png")
        self.mensch.center_x = 1150
        self.mensch.center_y = 350
        self.sho_list.append(self.mensch)

        # boton
        self.CON = arcade.Sprite("CON_shop.png", 1.8)
        self.CON.center_x = 1000
        self.CON.center_y = 325
        self.sho_list.append(self.CON)

        self.cON = arcade.Sprite("POW_up_shop.png", 2.0)
        self.cON.center_x = 1150
        self.cON.center_y = 325
        self.sho_list.append(self.cON)

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y, button)
        if 205 < x < 273 and 255 < y < 290:
            print ("con")
            Shop_ansicht = Shop_con()
            self.window.show_view(Shop_ansicht)

        if 335 < x < 468 and 255 < y < 295:
            print ("con")
            Shop_ansicht = Shop_up()
            self.window.show_view(Shop_ansicht)


    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            Shop_ansicht = Spiel()
            self.window.show_view(Shop_ansicht)

    def on_draw(self):
        self.clear()
        self.sho_list.draw(pixelated=True)

class Shop_con(arcade.View):
    def __init__(self):
        super().__init__()

        self.shop_list = arcade.SpriteList()

        self.mensch = arcade.Sprite("shop hintergrund.png")
        self.mensch.center_x = 1150
        self.mensch.center_y = 350
        self.shop_list.append(self.mensch) 

        self.lv2_con = arcade.Sprite("lv2_con..png", 1.4)
        self.lv2_con.center_x = 1250
        self.lv2_con.center_y = 350
        self.shop_list.append(self.lv2_con) 

        self.lv1_con = arcade.Sprite("lv1_con.png", 1.4)
        self.lv1_con.center_x = 1050
        self.lv1_con.center_y = 350
        self.shop_list.append(self.lv1_con) 

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y, button)
        if 250 < x < 350 and 280 < y < 315:
            print ("con")
            Shop_ansicht = Shop_con()
            self.window.show_view(Shop_ansicht)


        print(x, y, button)
        if 450 < x < 550 and 280 < y < 315:
            print ("con")
            Shop_ansicht = Shop_con()
            self.window.show_view(Shop_ansicht)


    def on_draw(self):
        self.clear()
        self.shop_list.draw(pixelated=True)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            Shop_ansicht = Shop()
            self.window.show_view(Shop_ansicht)

class Shop_up(arcade.View):
    def __init__(self):
        super().__init__()

        self.shop_list = arcade.SpriteList()

        self.mensch = arcade.Sprite("shop hintergrund.png")
        self.mensch.center_x = 1150
        self.mensch.center_y = 350
        self.shop_list.append(self.mensch) 

    def on_draw(self):
        self.clear()
        self.shop_list.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            Shop_ansicht = Shop()
            self.window.show_view(Shop_ansicht)

spiel = arcade.Window(800, 600, "Speeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeed")
spiel_ansicht = Spiel()
spiel.show_view(spiel_ansicht)
arcade.run()
