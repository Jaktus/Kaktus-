import arcade
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WORLD_WIDTH = 16000
WORLD_HEIGHT = 16000

WALK_SPEED = 2
SPRINT_SPEED = 3

COAL_CHANCE = 0.2

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")
        arcade.set_background_color(arcade.color.BLACK)

        self.keys_pressed = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
            arcade.key.LSHIFT: False,
            arcade.key.RSHIFT: False,
        }

        self.coal = 0

        self.setup()
        self.physiks_engine = arcade.PhysicsEngineSimple(self.player, self.stone_list)

    def setup(self):
        self.stone_list = arcade.SpriteList(use_spatial_hash=True)
        self.coal_drop_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()
        Stone = ["stone_1.png", "stone_2.png"]

        self.player = arcade.Sprite("player.png", 1)
        self.player.center_x = WORLD_WIDTH / 2
        self.player.center_y = WORLD_HEIGHT / 2
        self.player_list.append(self.player)

        for x in range(0, WORLD_WIDTH, 32):
            for y in range(0, WORLD_HEIGHT, 32):
                if (WORLD_WIDTH / 2 - 100 < x < WORLD_WIDTH / 2 + 100) and (WORLD_HEIGHT / 2 - 100 < y < WORLD_HEIGHT / 2 + 100):
                    continue
                stone_image = random.choice(Stone)
                stone = arcade.Sprite(stone_image, 1)
                stone.center_x = x
                stone.center_y = y
                stone.drops_coal = random.random() < COAL_CHANCE
                self.stone_list.append(stone)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.coal_icon = arcade.Sprite("coal.png", 0.8)
        self.coal_icon.center_x = 20
        self.coal_icon.center_y = SCREEN_HEIGHT - 20

        self.coal_text = arcade.Text(
            text="x 0",
            x=40,
            y=SCREEN_HEIGHT - 28,
            color=arcade.color.WHITE,
            font_size=14,
            bold=True,
        )

    def _get_camera_pos(self):
        cam_x = max(SCREEN_WIDTH / 2, min(self.player.center_x, WORLD_WIDTH - SCREEN_WIDTH / 2))
        cam_y = max(SCREEN_HEIGHT / 2, min(self.player.center_y, WORLD_HEIGHT - SCREEN_HEIGHT / 2))
        return cam_x, cam_y

    def on_key_press(self, key, _modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = True

    def on_key_release(self, key, _modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = False

    def on_mouse_press(self, x, y, button, _modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            cam_x, cam_y = self._get_camera_pos()
            world_x = x + cam_x - SCREEN_WIDTH / 2
            world_y = y + cam_y - SCREEN_HEIGHT / 2
            blocks_hit = arcade.get_sprites_at_point((world_x, world_y), self.stone_list)
            if blocks_hit:
                block = blocks_hit[0]
                if block.drops_coal:
                    drop = arcade.Sprite("coal.png", 0.6)
                    drop.center_x = block.center_x
                    drop.center_y = block.center_y
                    self.coal_drop_list.append(drop)
                block.remove_from_sprite_lists()

    def on_update(self, _delta_time):
        sprinting = self.keys_pressed[arcade.key.LSHIFT] or self.keys_pressed[arcade.key.RSHIFT]
        speed = SPRINT_SPEED if sprinting else WALK_SPEED

        move_x = 0
        move_y = 0
        if self.keys_pressed[arcade.key.A] and not self.keys_pressed[arcade.key.D]:
            move_x = -speed
        elif self.keys_pressed[arcade.key.D] and not self.keys_pressed[arcade.key.A]:
            move_x = speed
        if self.keys_pressed[arcade.key.W] and not self.keys_pressed[arcade.key.S]:
            move_y = speed
        elif self.keys_pressed[arcade.key.S] and not self.keys_pressed[arcade.key.W]:
            move_y = -speed

        self.player.change_x = move_x
        self.player.change_y = move_y

        self.player_list.update()
        self.physiks_engine.update()

        collected = arcade.check_for_collision_with_list(self.player, self.coal_drop_list)
        for drop in collected:
            drop.remove_from_sprite_lists()
            self.coal += 1
            self.coal_text.text = f"x {self.coal}"

        cam_x, cam_y = self._get_camera_pos()
        self.camera.position = (cam_x, cam_y)

    def on_draw(self):
        self.clear()

        self.camera.use()
        self.stone_list.draw()
        self.coal_drop_list.draw()
        self.player_list.draw()

        self.gui_camera.use()
        arcade.draw_sprite(self.coal_icon)
        self.coal_text.draw()

MyGame()
arcade.run()
