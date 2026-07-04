import arcade
import random

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH   = 4000
WORLD_HEIGHT  = 4000

WALK_SPEED   = 2
SPRINT_SPEED = 3

MINE_RANGE  = 48
MINE_TIME   = 0.6

HOTBAR_SLOTS = 9
SLOT_SIZE    = 48
SLOT_GAP     = 4

TILE_SIZE       = 32
DROP_JITTER     = 6
STONE_TO_CRAFT  = 9

# cumulative spawn chances (rarest first)
ORE_TABLE = [
    ("diamond", "diamond.png", 0.01),
    ("iron",    "iron.png",    0.06),
    ("copper",  "copper.png",  0.16),
    ("coal",    "coal.png",    0.36),
    ("stone",   "stone.png",   0.76),
]


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.keys_pressed = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
            arcade.key.LSHIFT: False,
            arcade.key.RSHIFT: False,
        }

        self.mining_target   = None
        self.mining_progress = 0.0
        self.selected_slot   = 0
        self.facing          = (0, -1)
        self.show_crafting_gui = False

        # 9 slots: {"type": str|None, "count": int}
        self.hotbar = [{"type": None, "count": 0} for _ in range(HOTBAR_SLOTS)]

        # (tile_x, tile_y) -> {"type": str, "sprites": [drop, ...]}
        self.tile_stacks = {}

        self.setup()
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.stone_list)

    def setup(self):
        self.stone_list  = arcade.SpriteList(use_spatial_hash=True)
        self.drop_list   = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()

        self.player = arcade.Sprite("player.png", 1)
        self.player.center_x = WORLD_WIDTH  / 2
        self.player.center_y = WORLD_HEIGHT / 2
        self.player_list.append(self.player)

        for x in range(0, WORLD_WIDTH, 32):
            for y in range(0, WORLD_HEIGHT, 32):
                in_spawn = (
                    WORLD_WIDTH  / 2 - 100 < x < WORLD_WIDTH  / 2 + 100 and
                    WORLD_HEIGHT / 2 - 100 < y < WORLD_HEIGHT / 2 + 100
                )
                if in_spawn:
                    continue
                stone = arcade.Sprite(random.choice(["stone_1.png", "stone_2.png"]), 1)
                stone.center_x = x
                stone.center_y = y
                stone.ore_type = None
                stone.ore_tex  = None
                r = random.random()
                for name, tex, cumulative in ORE_TABLE:
                    if r < cumulative:
                        stone.ore_type = name
                        stone.ore_tex  = tex
                        break
                self.stone_list.append(stone)

        self.camera     = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.textures = {
            "slot":           arcade.load_texture("invent_slot.png"),
            "pickaxe":        arcade.load_texture("pickaxe.png"),
            "coal":           arcade.load_texture("coal.png"),
            "copper":         arcade.load_texture("copper.png"),
            "iron":           arcade.load_texture("iron.png"),
            "diamond":        arcade.load_texture("diamond.png"),
            "stone":          arcade.load_texture("stone.png"),
            "crafting_block": arcade.load_texture("crafting_block.png"),
        }
        self.crafting_gui_texture = arcade.load_texture("crafting_gui.png")

        # pickaxe starts in slot 0
        self.hotbar[0] = {"type": "pickaxe", "count": 1}

    # ---------------------------------------------------------------- helpers
    def _pickaxe_equipped(self):
        return self.hotbar[self.selected_slot]["type"] == "pickaxe"

    def _pick_up(self, item_type):
        for slot in self.hotbar:
            if slot["type"] == item_type:
                slot["count"] += 1
                return True
        for slot in self.hotbar:
            if slot["type"] is None:
                slot["type"]  = item_type
                slot["count"] = 1
                return True
        return False

    def _front_tile(self):
        fx, fy = self.facing
        target_x = self.player.center_x + fx * TILE_SIZE
        target_y = self.player.center_y + fy * TILE_SIZE
        tile_x = round(target_x / TILE_SIZE) * TILE_SIZE
        tile_y = round(target_y / TILE_SIZE) * TILE_SIZE
        return tile_x, tile_y

    def _spawn_crafting_block(self, tile_x, tile_y):
        block = arcade.Sprite("crafting_block.png", 0.5)
        block.center_x = tile_x
        block.center_y = tile_y
        block.ore_type = "crafting_block"
        block.ore_tex  = "crafting_block.png"
        self.stone_list.append(block)

    def _register_tile_drop(self, tile_x, tile_y, item_type, drop_sprite):
        if item_type != "stone":
            return
        key = (tile_x, tile_y)
        stack = self.tile_stacks.get(key)
        if stack is None or stack["type"] != item_type:
            stack = {"type": item_type, "sprites": []}
            self.tile_stacks[key] = stack
        stack["sprites"].append(drop_sprite)

        if len(stack["sprites"]) >= STONE_TO_CRAFT:
            for sprite in stack["sprites"]:
                sprite.remove_from_sprite_lists()
            del self.tile_stacks[key]
            self._spawn_crafting_block(tile_x, tile_y)

    def _drop_selected_item(self):
        slot = self.hotbar[self.selected_slot]
        if not slot["type"] or slot["count"] <= 0:
            return

        item_type = slot["type"]
        tile_x, tile_y = self._front_tile()

        if item_type == "crafting_block":
            self._spawn_crafting_block(tile_x, tile_y)
        else:
            drop = arcade.Sprite(f"{item_type}.png", 0.6)
            drop.center_x  = tile_x + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.center_y  = tile_y + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.item_type = item_type
            self.drop_list.append(drop)
            self._register_tile_drop(tile_x, tile_y, item_type, drop)

        slot["count"] -= 1
        if slot["count"] <= 0:
            slot["type"]  = None
            slot["count"] = 0

    def _get_camera_pos(self):
        cam_x = max(SCREEN_WIDTH  / 2, min(self.player.center_x, WORLD_WIDTH  - SCREEN_WIDTH  / 2))
        cam_y = max(SCREEN_HEIGHT / 2, min(self.player.center_y, WORLD_HEIGHT - SCREEN_HEIGHT / 2))
        return cam_x, cam_y

    # ---------------------------------------------------------------- input
    def on_key_press(self, key, _modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = True
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_9:
            self.selected_slot = key - arcade.key.KEY_1
        if key == arcade.key.Q:
            self._drop_selected_item()
        if key == arcade.key.E:
            self.show_crafting_gui = not self.show_crafting_gui

    def on_key_release(self, key, _modifiers):
        if key in self.keys_pressed:
            self.keys_pressed[key] = False

    def on_mouse_scroll(self, _x, _y, _scroll_x, scroll_y):
        self.selected_slot = (self.selected_slot - int(scroll_y)) % HOTBAR_SLOTS

    def on_mouse_press(self, x, y, button, _modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT or not self._pickaxe_equipped():
            return

        cam_x, cam_y = self._get_camera_pos()
        world_x = x + cam_x - SCREEN_WIDTH  / 2
        world_y = y + cam_y - SCREEN_HEIGHT / 2

        blocks_hit = arcade.get_sprites_at_point((world_x, world_y), self.stone_list)
        if not blocks_hit:
            return

        block = blocks_hit[0]
        if arcade.get_distance_between_sprites(self.player, block) <= MINE_RANGE:
            self.mining_target   = block
            self.mining_progress = 0.0

    def on_mouse_release(self, x, y, button, _modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mining_target   = None
            self.mining_progress = 0.0

    # ---------------------------------------------------------------- update
    def on_update(self, delta_time):
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

        if move_x != 0 or move_y != 0:
            self.facing = ((move_x > 0) - (move_x < 0), (move_y > 0) - (move_y < 0))

        self.player.change_x = move_x
        self.player.change_y = move_y
        self.player_list.update()
        self.physics_engine.update()

        if self.mining_target:
            dist = arcade.get_distance_between_sprites(self.player, self.mining_target)
            if dist > MINE_RANGE:
                self.mining_target   = None
                self.mining_progress = 0.0
            else:
                self.mining_progress += delta_time
                if self.mining_progress >= MINE_TIME:
                    if self.mining_target.ore_type:
                        drop = arcade.Sprite(self.mining_target.ore_tex, 0.6)
                        drop.center_x  = self.mining_target.center_x + random.uniform(-DROP_JITTER, DROP_JITTER)
                        drop.center_y  = self.mining_target.center_y + random.uniform(-DROP_JITTER, DROP_JITTER)
                        drop.item_type = self.mining_target.ore_type
                        self.drop_list.append(drop)
                    self.mining_target.remove_from_sprite_lists()
                    self.mining_target   = None
                    self.mining_progress = 0.0

        for drop in arcade.check_for_collision_with_list(self.player, self.drop_list):
            if self._pick_up(drop.item_type):
                drop.remove_from_sprite_lists()

        cam_x, cam_y = self._get_camera_pos()
        self.camera.position = (cam_x, cam_y)

    # ---------------------------------------------------------------- draw
    def on_draw(self):
        self.clear()

        self.camera.use()
        self.stone_list.draw()
        self.drop_list.draw()
        self.player_list.draw()

        if self.mining_target:
            ratio = self.mining_progress / MINE_TIME
            bx = self.mining_target.center_x
            by = self.mining_target.center_y + 20
            arcade.draw_lrbt_rectangle_filled(bx - 16, bx - 16 + 32 * ratio, by - 3, by + 3, arcade.color.YELLOW)
            arcade.draw_lrbt_rectangle_outline(bx - 16, bx + 16, by - 3, by + 3, arcade.color.WHITE, 1)

        self.gui_camera.use()
        self._draw_hotbar()

        if self.show_crafting_gui:
            arcade.draw_texture_rect(
                self.crafting_gui_texture,
                arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            )

    def _draw_hotbar(self):
        total = HOTBAR_SLOTS * SLOT_SIZE + (HOTBAR_SLOTS - 1) * SLOT_GAP
        ox    = (SCREEN_WIDTH - total) / 2
        y     = SLOT_GAP + SLOT_SIZE / 2

        for i in range(HOTBAR_SLOTS):
            cx = ox + i * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2

            arcade.draw_texture_rect(
                self.textures["slot"],
                arcade.XYWH(cx, y, SLOT_SIZE, SLOT_SIZE),
            )

            if i == self.selected_slot:
                arcade.draw_lrbt_rectangle_outline(
                    cx - SLOT_SIZE / 2, cx + SLOT_SIZE / 2,
                    y  - SLOT_SIZE / 2, y  + SLOT_SIZE / 2,
                    arcade.color.YELLOW, 3,
                )

            slot = self.hotbar[i]
            if slot["type"] and slot["type"] in self.textures:
                arcade.draw_texture_rect(
                    self.textures[slot["type"]],
                    arcade.XYWH(cx, y, SLOT_SIZE - 8, SLOT_SIZE - 8),
                )
                arcade.draw_text(
                    str(slot["count"]),
                    cx + SLOT_SIZE / 2 - 2,
                    y  - SLOT_SIZE / 2 + 2,
                    arcade.color.WHITE,
                    font_size=10,
                    anchor_x="right",
                )


MyGame()
arcade.run()
