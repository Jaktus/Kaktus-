
import arcade


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"
GRAVITY = 0.5
BULLET_GRVITY = 0.25
CHARGE_MAX = 1.0
CHARGE_MIN_SPEED = 10
CHARGE_MAX_SPEED = 20


class GameView(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.keys_pressed = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.D: False,
            arcade.key.SPACE: False
        }

        self.physics_engine = None
        self.charging = False
        self.charge_time = 0.0
        self.mouse_x = 0
        self.mouse_y = 0

    def setup(self):

        self.player_list = arcade.SpriteList()
        self.boden_list = arcade.SpriteList()
        self.Dummy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.player = arcade.Sprite("PLayer.png")
        self.player.center_x = 64
        self.player.center_y = 128
        self.player_list.append(self.player)

        self.Dummy = arcade.Sprite("Dummy.png")
        self.Dummy.center_x = 400
        self.Dummy.center_y = 128
        self.Dummy_list.append(self.Dummy)

        for x in range(10, 1270, 32):
            self.boden = arcade.Sprite("floor.png")
            self.boden.center_x = x
            self.boden.center_y = 32
            self.boden_list.append(self.boden)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            walls=self.boden_list,
            gravity_constant=GRAVITY
        )

    def on_key_press(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = True

        if (key == arcade.key.SPACE or key == arcade.key.W):
            if self.physics_engine.can_jump():
                self.player.change_y = 15

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.charging = True
            self.charge_time = 0.0
            self.mouse_x = x
            self.mouse_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.charging:
            self.charging = False

            charge_ratio = min(self.charge_time / CHARGE_MAX, 1.0)
            speed = CHARGE_MIN_SPEED + charge_ratio * (CHARGE_MAX_SPEED - CHARGE_MIN_SPEED)

            bullet = arcade.Sprite("Bullet.png")
            bullet.center_x = self.player.center_x
            bullet.center_y = self.player.center_y

            dx = x - self.player.center_x
            dy = y - self.player.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                bullet.change_x = (dx / distance) * speed
                bullet.change_y = (dy / distance) * speed

            self.bullet_list.append(bullet)
            self.charge_time = 0.0

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = False

    def on_update(self, delta_time):
        self.player.change_x = 0

        if self.keys_pressed[arcade.key.A] and not self.keys_pressed[arcade.key.D]:
            self.player.change_x = -5
        elif self.keys_pressed[arcade.key.D] and not self.keys_pressed[arcade.key.A]:
            self.player.change_x = 5

        if self.charging:
            self.charge_time = min(self.charge_time + delta_time, CHARGE_MAX)

        self.physics_engine.update()

        for bullet in self.bullet_list:
            bullet.change_y -= BULLET_GRVITY
            bullet.center_x += bullet.change_x
            bullet.center_y += bullet.change_y
            if bullet.center_y < 0 or bullet.center_x < 0 or bullet.center_x > WINDOW_WIDTH:
                bullet.remove_from_sprite_lists()

    def on_draw(self):
        self.clear()
        self.player_list.draw()
        self.boden_list.draw()
        self.Dummy_list.draw()
        self.bullet_list.draw()

        if self.charging:
            charge_ratio = min(self.charge_time / CHARGE_MAX, 1.0)

            bar_width = 50
            bar_height = 8
            bar_x = self.player.center_x - bar_width / 2
            bar_y = self.player.center_y + self.player.height / 2 + 10


            # arcade.draw_lrbt_rectangle_filled(
            #     bar_x, bar_x + bar_width,
            #     bar_y, bar_y + bar_height,
            #     arcade.color.DARK_GRAY
            # )


            if charge_ratio < 0.5:
                r = int(255 * charge_ratio * 2)
                g = 255
            else:
                r = 255
                g = int(255 * (1 - (charge_ratio - 0.5) * 2))
            fill_color = (r, g, 0)

            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width * charge_ratio,
                bar_y, bar_y + bar_height,
                fill_color
            )


            # arcade.draw_lrbt_rectangle_outline(
            #     bar_x, bar_x + bar_width,
            #     bar_y, bar_y + bar_height,
            #     arcade.color.WHITE, 2
            # )


def main():
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
