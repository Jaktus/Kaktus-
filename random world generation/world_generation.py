import arcade
import random

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Procedural Supermarket Generation mit der deutschen sprache"
PLAYER_SPEED = 5
MIN_SHOOT_SPEED = 4
MAX_SHOOT_SPEED = 30
SHOOT_POWER_SCALE = 0.01
FRICTION = 0.9999


class SupermarketGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE_SMOKE)

        self.key_list = arcade.SpriteList()
        self.cluster_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.spieler_list = arcade.SpriteList()
        self.cluster_keys = arcade.SpriteList()

        self.input_x = 0
        self.input_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.outcome_speed = PLAYER_SPEED
        self.target_x = None
        self.target_y = None
        self.shoot_strength = 0
        self.moving = False

    def setup(self):

        self.shop = arcade.Sprite("shop.png")
        self.shop.center_x = 850
        self.shop.center_y = 350
        self.floor_list.append(self.shop)




        self.spieler = arcade.Sprite("spieler.png")
        self.spieler.center_x = 800
        self.spieler.center_y = 350
        print("Spieler erstellt")
        self.spieler_list.append(self.spieler)

    def on_mouse_motion(self, x, y, dx, dy):
        # Mausbewegung setzt kein neues Ziel, nur der Klick startet den Schuss.
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.target_x = x
            self.target_y = y
            dx = x - self.spieler.center_x
            dy = y - self.spieler.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance == 0:
                self.velocity_x = 0
                self.velocity_y = 0
                self.moving = False
                return
            direction_x = dx / distance
            direction_y = dy / distance
            self.shoot_strength = min(max(distance * SHOOT_POWER_SCALE, MIN_SHOOT_SPEED), MAX_SHOOT_SPEED)
            self.velocity_x = direction_x * self.shoot_strength
            self.velocity_y = direction_y * self.shoot_strength
            self.spieler.change_x = self.velocity_x
            self.spieler.change_y = self.velocity_y
            self.moving = True

    def on_key_press(self, symbol, modifiers):
        # Tastatursteuerung deaktiviert; Maussteuerung wird verwendet.
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def block_touches_key(self, block):
        for key in self.key_list:
            if arcade.check_for_collision(block, key):
                return True
        return False

    def generate_shelves(self):
        for i in range(10):
            key = arcade.Sprite("s..png")
            while True:
                key.center_x = random.randint(50, 700)
                key.center_y = random.randint(50, 700)
                too_close = False
                for other in self.key_list:
                    distance = arcade.get_distance_between_sprites(key, other)
                    if distance < 180:
                        too_close = True
                        break
                if arcade.check_for_collision(key, self.shop):
                    too_close = True
                if not too_close:
                    break
            self.key_list.append(key)
            print("Key erstellt")
                




        while len(self.cluster_keys) < 140:
            block = arcade.Sprite("t..png", 0.7)
            block.center_x = random.randint(50, 700)
            block.center_y = random.randint(50, 700)
            print("Block erstellt")

            touches_key = arcade.check_for_collision_with_list(block, self.key_list)
            touches_cluster = arcade.check_for_collision_with_list(block, self.cluster_keys)

            for other in self.cluster_keys:
                distance = arcade.get_distance_between_sprites(block, other)
                if distance < 10 :
                    
                    
                    block.center_x = random.randint(50, 700)
                    block.center_y = random.randint(50, 700)
                
            if arcade.check_for_collision(block, self.shop):
                continue
                
            if touches_key or touches_cluster:

                self.cluster_keys.append(block)


        

  

                



    def on_update(self, delta_time):
        if self.moving:
            prev_x = self.spieler.center_x
            prev_y = self.spieler.center_y
            self.spieler.update()

            self.velocity_x *= FRICTION
            self.velocity_y *= FRICTION
            self.spieler.change_x = self.velocity_x
            self.spieler.change_y = self.velocity_y

            if arcade.check_for_collision_with_list(self.spieler, self.cluster_keys):
                self.spieler.center_x = prev_x
                self.spieler.center_y = prev_y
                self.velocity_x *= -0.7
                self.velocity_y *= -0.7
                self.spieler.change_x = self.velocity_x
                self.spieler.change_y = self.velocity_y

            if abs(self.velocity_x) < 1 and abs(self.velocity_y) < 1:
                self.velocity_x = 0
                self.velocity_y = 0
                self.spieler.change_x = 0
                self.spieler.change_y = 0
                self.moving = False
        else:
            self.spieler.change_x = 0
            self.spieler.change_y = 0


    def on_draw(self):
        self.clear()
        self.floor_list.draw()
        self.key_list.draw()
        self.cluster_list.draw()
        self.cluster_keys.draw()
        self.spieler_list.draw()
        


def main():
    game = SupermarketGame()
    game.setup()
    game.generate_shelves()
    arcade.run()


if __name__ == "__main__":
    main()
