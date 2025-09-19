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

        self.texture_index = 0  

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.W:
            self.mensch.change_y = 1
        elif symbol == arcade.key.S:
            self.mensch.change_y = -1
        elif symbol == arcade.key.A:
            self.mensch.change_x = -1
        elif symbol == arcade.key.D:
            self.mensch.change_x = 1

    def on_key_release(self, symbol, modifiers):
        if symbol in [arcade.key.W, arcade.key.S]:
            self.mensch.change_y = 0
        elif symbol in [arcade.key.A, arcade.key.D]:
            self.mensch.change_x = 0

    def on_update(self, delta_time):
        self.spieler_list.update()
        self.spiel_physik.update()
        self.scroll_to_player()

   
        if self.mensch.change_x < 0:
            self.texture_index = (self.texture_index + 1) % len(self.v_rennen)
            self.mensch.texture = self.v_rennen[self.texture_index]
        else:
            self.mensch.texture = arcade.load_texture("fleisch-stück.png")

        if self.mensch.collides_with_list(self.scene["Tile Layer 2"]):
            self.mensch.stop()
            Shop_ansicht = Shop()
            self.window.show_view(Shop_ansicht)

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

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        self.spieler_list.draw()

class Shop(arcade.View):
    def __init__(self):
        super().__init__()

        self.shop_list = arcade.SpriteList()

        self.mensch = arcade.Sprite("shop.png", 1.2)
        self.mensch.center_x = 1150
        self.mensch.center_y = 350
        self.shop_list.append(self.mensch)  

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y, button)
        if x < 262 and x > 95 and y > 251 and y < 283:
            Shop_ansicht = Shop_con()
            self.window.show_view(Shop_ansicht)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            Shop_ansicht = Spiel()
            self.window.show_view(Shop_ansicht)

    def on_draw(self):
        self.clear()
        self.shop_list.draw()

class Shop_con(arcade.View):
    def __init__(self):
        super().__init__()

        self.shop_list = arcade.SpriteList()

        self.mensch = arcade.Sprite("con shop.png", 1.2)
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
