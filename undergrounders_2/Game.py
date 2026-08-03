import arcade
from arcade.future.light import Light, LightLayer
import random



SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH   = 4000
WORLD_HEIGHT  = 4000


WALK_SPEED   = 2
SPRINT_SPEED = 3

MINE_RANGE = 48

PLAYER_FRAME_TIME = 0.18
PLAYER_SCALE      = 1

AMBIENT_COLOR      = (10, 10, 60)
PLAYER_LIGHT_SIZE  = 100
TORCH_LIGHT_SIZE   = 280
TORCH_LIGHT_COLOR  = (235, 245, 255)

GENERATOR_BURN_TIME   = 30
GENERATOR_LIGHT_SIZE  = 200
GENERATOR_LIGHT_COLOR = (255, 220, 140)
WIRE_LIGHT_SIZE       = 40
WIRE_LIGHT_COLOR      = (255, 220, 140)

CHARGING_DOC_LIGHT_SIZE  = 180
CHARGING_DOC_LIGHT_COLOR = (140, 255, 170)

DRILL_CHARGE_TIME = 30
DRILL_POWER_TIME  = 120

DRILL_FARM_TIME = 5

MINE_TIME = {
    "hand":            1.0,
    "pickaxe":         0.6,
    "pickaxe_iron":    0.4,
    "pickaxe_diamond": 0.15,
    "iron_drill":      0.05,
}

HOTBAR_SLOTS = 9
SLOT_SIZE    = 48
SLOT_GAP     = 4

TILE_SIZE       = 32
DROP_JITTER     = 6
STONES_TO_BLOCK = 4

GRID_ROWS  = 5
GRID_COLS  = 5
DRAG_SCALE = 1.5

CHEST_ROWS = 3
CHEST_COLS = 5

ORE_TABLE_HAND = [
    ("iron",     8),
    ("copper",  10),
    ("coal",    20),
    ("stone",   50),
]
ORE_TABLE_PICKAXE = [
    ("diamond",  1),
    ("iron",    15),
    ("copper",  12),
    ("coal",    22),
    ("stone",   50),
]
ORE_TABLE_IRON_PICKAXE = [
    ("diamond",  3),
    ("iron",    20),
    ("copper",  15),
    ("coal",    22),
    ("stone",   38),
]
ORE_TABLE_DIAMOND_PICKAXE = [
    ("diamond",  6),
    ("iron",    25),
    ("copper",  15),
    ("coal",    25),
    ("stone",   27),
]


def make_pool(table):
    pool = []
    for name, percent in table:
        for i in range(percent):
            pool.append(name)
    while len(pool) < 100:
        pool.append(None)
    return pool


ORE_POOLS = {
    "hand":            make_pool(ORE_TABLE_HAND),
    "pickaxe":         make_pool(ORE_TABLE_PICKAXE),
    "pickaxe_iron":    make_pool(ORE_TABLE_IRON_PICKAXE),
    "pickaxe_diamond": make_pool(ORE_TABLE_DIAMOND_PICKAXE),
    "iron_drill":      make_pool(ORE_TABLE_DIAMOND_PICKAXE),
}

LETTERS = {
    
    "stone":                "s",
    "iron_drill_base":      "b",
    "iron_drill_drill":     "R",
    "generator":            "g",
    "wire":                 "w",
    "copper_stick":         "k",
    "coal":                 "o",
    "copper":               "c",
    "iron":                 "i",
    "diamond":              "d",
    "pickaxe_handle":       "h",
    "pickaxe_head":         "S",
    "pickaxe_iron_head":    "I",
    "pickaxe_diamond_head": "D",
    "battery":              "B",
}

RECIPES = [
    ("pickaxe_handle",       ["sss"]),
    ("battery",              ["ioi",]),
    ("charging_doc",         ["iii",
                              "igi",
                              "iii",
                              ".w."]),
    ("copper_stick",         ["c",
                              "c"]),
    ("torch",                ["o",
                              "k"]),
    ("wire",                 ["c",
                              "c",
                              "c"]),
    ("generator",            ["iii",
                              "ici",
                              "iii"]),  
    ("drill",                ["iiiii",
                              "idddi",
                              "idkdi",
                              "idddi",
                              "iiiii"]),
    ("iron_drill_base",      ["iii",
                              "iBi",
                              "iii",
                              "iii"]),
    ("iron_drill_drill",     [".c.",
                              "cic"]),
    ("iron_drill",           ["R",
                              "b"]),
    ("pickaxe_handle",       ["s..",
                              ".s.",
                              "..s"]),
    ("pickaxe_handle",       ["..s",
                              ".s.",
                              "s.."]),
    ("hammer",               ["iii",
                              "sss",
                              ".h."]),
    ("crafting_block",       ["ss",
                              "ss"]),
    ("chest",                ["sss",
                              "s.s",
                              "sss"]),
    ("pickaxe_head",         ["sss",
                              "s.s"]),
    ("pickaxe_iron_head",    ["iii",
                              "i.i"]),
    ("pickaxe_diamond_head", ["ddd",
                              "d.d"]),
    ("pickaxe",              ["S",
                              "h"]),
    ("pickaxe_iron",         ["I",
                              "h"]),
    ("pickaxe_diamond",      ["D",
                              "h"]),
]

COAL_COST = {
    "copper_stick":         1,
    "charging_doc":         10,
    "torch":                1,
    "generator":            3,
    "iron_drill":           5,
    "drill":                10,
    "iron_drill_base":      5,
    "iron_drill_drill":     5,
    "pickaxe_handle":       1,
    "crafting_block":       1,
    "chest":                1,
    "pickaxe_head":         1,
    "pickaxe_iron_head":    1,
    "pickaxe_diamond_head": 1,
    "wire":                 1,
    "hammer":               3,
    "pickaxe":              5,
    "pickaxe_iron":         5,
    "pickaxe_diamond":      5,
    "battery":              2,
}

NEEDS_HAMMER = ["pickaxe_iron", "pickaxe_diamond", "charging_doc", "iron_drill"]

NEEDS_POWER = ["energy_station"]

CRAFT_TABLE_RANGE = 64

RECIPE_ICON_SIZE = 36
RECIPE_ICON_GAP  = 4
RECIPE_COLS      = 4


class Inventory:
    def __init__(self):
        self.selected_slot = 0
        self.crafting_open = False
        self.in_hand       = None
        self.mouse_pos     = (0, 0)
        self.craft_hint    = ""
        self.chest         = None
        self.generator     = None
        self.drag_slots    = []
        self.drag_source   = None

        self.images = {
            "charging_doc":    arcade.load_texture("charging_doc.png"),
            "slot":            arcade.load_texture("invent_slot.png"),
            "pickaxe":         arcade.load_texture("pickaxe.png"),
            "coal":            arcade.load_texture("coal.png"),
            "copper":          arcade.load_texture("copper.png"),
            "iron":            arcade.load_texture("iron.png"),
            "diamond":         arcade.load_texture("diamond.png"),
            "stone":           arcade.load_texture("stone.png"),
            "crafting_block":  arcade.load_texture("crafting_block.png"),
            "chest":           arcade.load_texture("chest.png"),
            "pickaxe_handle":  arcade.load_texture("pickaxe_handle.png"),
            "pickaxe_head":    arcade.load_texture("pickaxe_head.png"),
            "hammer":          arcade.load_texture("hammer.png"),
            "wire":            arcade.load_texture("wire.png"),
            "copper_stick":    arcade.load_texture("copper_stick.png"),
            "torch":           arcade.load_texture("torch.png"),
            "generator":       arcade.load_texture("generator.png"),
            "energy":          arcade.load_texture("energy_gui.png"),
            "iron_drill":      arcade.load_texture("iron_drill.png"),
            "drill":           arcade.load_texture("drill.png"),
            "iron_drill_base": arcade.load_texture("iron_drill_base.png"),
            "iron_drill_drill": arcade.load_texture("iron_drill_drill.png"),
            "battery":           arcade.load_texture("battery.png"),

            "pickaxe_iron":         arcade.load_texture("pickaxe_iron.png"),
            "pickaxe_iron_head":    arcade.load_texture("pickaxe_iron_head.png"),
            "pickaxe_diamond":      arcade.load_texture("pickaxe_diamond.png"),
            "pickaxe_diamond_head": arcade.load_texture("pickaxe_diamond_head.png"),
        }
        self.crafting_image = arcade.load_texture("crafting_gui.png")

        self.build_slots()

    def new_slot(self, kind, x, y):
        slot = {"kind": kind, "x": x, "y": y, "type": None, "count": 0}
        self.slots.append(slot)
        return slot

    def build_slots(self):
        self.slots = []

        total = HOTBAR_SLOTS * SLOT_SIZE + (HOTBAR_SLOTS - 1) * SLOT_GAP
        left = (SCREEN_WIDTH - total) / 2
        self.hotbar = []
        for i in range(HOTBAR_SLOTS):
            x = left + i * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2
            y = SLOT_GAP + SLOT_SIZE / 2
            self.hotbar.append(self.new_slot("hotbar", x, y))

        grid_width = GRID_COLS * SLOT_SIZE + (GRID_COLS - 1) * SLOT_GAP
        left = (SCREEN_WIDTH - grid_width) / 2
        top = SCREEN_HEIGHT / 2 + 100
        self.grid = []
        for row in range(GRID_ROWS):
            line = []
            for col in range(GRID_COLS):
                x = left + col * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2
                y = top - row * (SLOT_SIZE + SLOT_GAP)
                line.append(self.new_slot("grid", x, y))
            self.grid.append(line)

        x = left + grid_width + 40 + SLOT_SIZE / 2
        y = top - 2 * (SLOT_SIZE + SLOT_GAP)
        self.output = self.new_slot("output", x, y)

        x = SCREEN_WIDTH / 2
        y = top - GRID_ROWS * (SLOT_SIZE + SLOT_GAP) - 10
        self.fuel = self.new_slot("fuel", x, y)

        self.energy = self.new_slot("energy", SCREEN_WIDTH / 2 + 30, SCREEN_HEIGHT / 2 + 60)

        self.chest_slots = []
        for row in range(CHEST_ROWS):
            for col in range(CHEST_COLS):
                x = left + col * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2
                y = top - row * (SLOT_SIZE + SLOT_GAP)
                self.chest_slots.append(self.new_slot("chest", x, y))

        self.recipe_slots = []
        recipe_start_x = 20 + RECIPE_ICON_SIZE / 2
        for i, (result, _pattern) in enumerate(RECIPES):
            col = i % RECIPE_COLS
            row = i // RECIPE_COLS
            x = recipe_start_x + col * (RECIPE_ICON_SIZE + RECIPE_ICON_GAP)
            y = top - row * (RECIPE_ICON_SIZE + RECIPE_ICON_GAP)
            self.recipe_slots.append({"index": i, "result": result, "x": x, "y": y})

    def clear_slot(self, slot):
        slot["type"] = None
        slot["count"] = 0

    def current_tool(self):
        item = self.hotbar[self.selected_slot]["type"]
        if item in MINE_TIME:
            return item
        return "hand"

    def has_hammer(self):
        for slot in self.hotbar:
            if slot["type"] == "hammer":
                return True
        return False

    def drop_one(self):
        slot = self.hotbar[self.selected_slot]
        if slot["type"] is None:
            return None
        item_type = slot["type"]
        slot["count"] = slot["count"] - 1
        if slot["count"] <= 0:
            self.clear_slot(slot)
        return item_type

    def add_to_hotbar(self, item_type, count):
        for slot in self.hotbar:
            if slot["type"] == item_type:
                slot["count"] = slot["count"] + count
                return True
        for slot in self.hotbar:
            if slot["type"] is None:
                slot["type"] = item_type
                slot["count"] = count
                return True
        return False

    def take_from_hotbar(self, item_type, max_count=None):
        for slot in self.hotbar:
            if slot["type"] == item_type:
                take = slot["count"] if max_count is None else min(max_count, slot["count"])
                slot["count"] = slot["count"] - take
                if slot["count"] <= 0:
                    self.clear_slot(slot)
                return take
        return 0


    def mouse_in_slot(self, x, y, slot):
        links  = slot["x"] - SLOT_SIZE / 2
        rechts = slot["x"] + SLOT_SIZE / 2
        unten  = slot["y"] - SLOT_SIZE / 2
        oben   = slot["y"] + SLOT_SIZE / 2
        return links <= x <= rechts and unten <= y <= oben

    def slot_visible(self, slot):
        if slot["kind"] == "hotbar":
            return True
        if slot["kind"] == "chest":
            return self.chest is not None
        if slot["kind"] == "energy":
            return self.generator is not None
        return self.crafting_open

    def slot_at(self, x, y):
        for slot in self.slots:
            if not self.slot_visible(slot):
                continue
            if self.mouse_in_slot(x, y, slot):
                return slot
        return None

    def recipe_index_at(self, x, y):
        if not self.crafting_open:
            return None
        for slot in self.recipe_slots:
            links  = slot["x"] - RECIPE_ICON_SIZE / 2
            rechts = slot["x"] + RECIPE_ICON_SIZE / 2
            unten  = slot["y"] - RECIPE_ICON_SIZE / 2
            oben   = slot["y"] + RECIPE_ICON_SIZE / 2
            if links <= x <= rechts and unten <= y <= oben:
                return slot["index"]
        return None

    def fill_recipe(self, index):
        result, pattern = RECIPES[index]

        for row in self.grid:
            for slot in row:
                if slot["type"] is not None:
                    self.add_to_hotbar(slot["type"], slot["count"])
                    self.clear_slot(slot)

        letter_to_item = {letter: item for item, letter in LETTERS.items()}

        for r, line in enumerate(pattern):
            for c, letter in enumerate(line):
                if letter == "." or r >= GRID_ROWS or c >= GRID_COLS:
                    continue
                item = letter_to_item.get(letter)
                if item is None:
                    continue
                got = self.take_from_hotbar(item, 1)
                if got > 0:
                    slot = self.grid[r][c]
                    slot["type"]  = item
                    slot["count"] = got

        needed = COAL_COST.get(result, 0)
        have = self.fuel["count"] if self.fuel["type"] == "coal" else 0
        if have < needed:
            got = self.take_from_hotbar("coal", needed - have)
            if got > 0:
                self.fuel["type"]  = "coal"
                self.fuel["count"] = have + got

        self.check_recipe()

    def start_drag(self, x, y, only_one=False):
        slot = self.slot_at(x, y)
        if slot is None or slot["type"] is None:
            return
        self.drag_slots  = []
        self.drag_source = None

        if slot["kind"] == "output":
            n = 1 if only_one else self.max_crafts(slot["type"])
            self.in_hand = {"type": slot["type"], "count": n}
            self.pay_recipe(slot["type"], n)
            self.clear_slot(slot)
            self.check_recipe()
            return

        self.in_hand = {"type": slot["type"], "count": slot["count"]}
        self.clear_slot(slot)
        if only_one:
            self.drag_source = slot
            self.drag_slots  = [slot]

        self.check_recipe()

    def track_drag(self, x, y):
        if self.in_hand is None or self.drag_source is None:
            return
        if self.in_hand["count"] <= 0:
            return
        slot = self.slot_at(x, y)
        if slot is None:
            return
        for done in self.drag_slots:
            if done is slot:
                return
        if slot["kind"] == "output":
            return
        if slot["kind"] in ("fuel", "energy") and self.in_hand["type"] != "coal":
            return
        if slot["type"] is not None and slot["type"] != self.in_hand["type"]:
            return

        slot["type"]  = self.in_hand["type"]
        slot["count"] = slot["count"] + 1
        self.in_hand["count"] = self.in_hand["count"] - 1
        self.drag_slots.append(slot)
        self.check_recipe()

    def end_drag(self, x, y):
        if self.in_hand is None:
            return

        if self.drag_source is not None:
            self.track_drag(x, y)
            if self.in_hand["count"] > 0:
                source = self.drag_source
                if source["type"] is None or source["type"] == self.in_hand["type"]:
                    source["type"]  = self.in_hand["type"]
                    source["count"] = source["count"] + self.in_hand["count"]
                else:
                    self.add_to_hotbar(self.in_hand["type"], self.in_hand["count"])
            self.in_hand     = None
            self.drag_source = None
            self.drag_slots  = []
            self.check_recipe()
            return

        slot = self.slot_at(x, y)

        ok = slot is not None
        if ok and slot["kind"] == "output":
            ok = False
        if ok and slot["kind"] in ("fuel", "energy") and self.in_hand["type"] != "coal":
            ok = False
        if ok and slot["type"] is not None and slot["type"] != self.in_hand["type"]:
            ok = False

        if ok:
            slot["type"] = self.in_hand["type"]
            slot["count"] = slot["count"] + self.in_hand["count"]
        else:
            self.add_to_hotbar(self.in_hand["type"], self.in_hand["count"])

        self.in_hand = None
        self.check_recipe()


    def grid_as_text(self):
        lines = []
        for row in self.grid:
            line = ""
            for slot in row:
                if slot["type"] is None:
                    line = line + "."
                elif slot["type"] in LETTERS:
                    line = line + LETTERS[slot["type"]]
                else:
                    line = line + "?"
            lines.append(line)

        empty_row = "." * GRID_COLS
        while len(lines) > 0 and lines[0] == empty_row:
            lines.pop(0)
        while len(lines) > 0 and lines[-1] == empty_row:
            lines.pop()

        while len(lines) > 0 and self.column_empty(lines, 0):
            for i in range(len(lines)):
                lines[i] = lines[i][1:]
        while len(lines) > 0 and self.column_empty(lines, -1):
            for i in range(len(lines)):
                lines[i] = lines[i][:-1]

        return lines

    def column_empty(self, lines, col):
        for line in lines:
            if line[col] != ".":
                return False
        return True

    def check_recipe(self):
        self.clear_slot(self.output)
        self.craft_hint = ""
        in_grid = self.grid_as_text()

        for result, pattern in RECIPES:
            if in_grid != pattern:
                continue

            if result in NEEDS_HAMMER and not self.has_hammer():
                self.craft_hint = "Du brauchst einen Hammer!"
                return
            if self.fuel["count"] < COAL_COST[result]:
                self.craft_hint = "Braucht " + str(COAL_COST[result]) + " Kohle!"
                return

            self.output["type"] = result
            self.output["count"] = 1
            return

    def max_crafts(self, item):
        n = None
        for row in self.grid:
            for slot in row:
                if slot["type"] is not None:
                    if n is None or slot["count"] < n:
                        n = slot["count"]
        if n is None:
            return 0
        return min(n, self.fuel["count"] // COAL_COST[item])

    def pay_recipe(self, item, n=1):
        self.fuel["count"] = self.fuel["count"] - COAL_COST[item] * n
        if self.fuel["count"] <= 0:
            self.clear_slot(self.fuel)
        for row in self.grid:
            for slot in row:
                if slot["type"] is None:
                    continue
                slot["count"] = slot["count"] - n
                if slot["count"] <= 0:
                    self.clear_slot(slot)


    def open_chest(self, chest):
        self.chest = chest
        for i in range(len(self.chest_slots)):
            self.chest_slots[i]["type"] = chest.items[i]["type"]
            self.chest_slots[i]["count"] = chest.items[i]["count"]

    def close_chest(self):
        for i in range(len(self.chest_slots)):
            self.chest.items[i]["type"] = self.chest_slots[i]["type"]
            self.chest.items[i]["count"] = self.chest_slots[i]["count"]
        self.chest = None


    def open_generator(self, gen):
        self.generator = gen
        self.energy["type"]  = gen.fuel["type"]
        self.energy["count"] = gen.fuel["count"]

    def close_generator(self):
        self.generator.fuel["type"]  = self.energy["type"]
        self.generator.fuel["count"] = self.energy["count"]
        self.generator = None
        self.clear_slot(self.energy)


    def draw_slot(self, slot):
        x = slot["x"]
        y = slot["y"]
        arcade.draw_texture_rect(self.images["slot"], arcade.XYWH(x, y, SLOT_SIZE, SLOT_SIZE))
        if slot["type"] is not None:
            arcade.draw_texture_rect(self.images[slot["type"]], arcade.XYWH(x, y, SLOT_SIZE - 8, SLOT_SIZE - 8))
            arcade.draw_text(
                str(slot["count"]),
                x + SLOT_SIZE / 2 - 2,
                y - SLOT_SIZE / 2 + 2,
                arcade.color.WHITE,
                font_size=10,
                anchor_x="right",
            )

    def draw(self):
        if self.crafting_open:
            arcade.draw_texture_rect(
                self.crafting_image,
                arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            )
            arcade.draw_text(
                "Linksklick: Stapel bewegen",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 40,
                arcade.color.WHITE, font_size=14, anchor_x="center",
            )
            arcade.draw_text(
                "Rechtsklick: 1 Item teilen",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 62,
                arcade.color.LIGHT_GRAY, font_size=12, anchor_x="center",
            )
            arcade.draw_text(
                "Kohle:",
                self.fuel["x"] - SLOT_SIZE / 2 - 8, self.fuel["y"] - 6,
                arcade.color.WHITE, font_size=12, anchor_x="right",
            )
            if self.craft_hint != "":
                arcade.draw_text(
                    self.craft_hint,
                    self.output["x"], self.output["y"] - SLOT_SIZE,
                    arcade.color.ORANGE, font_size=12, anchor_x="center",
                )

            for slot in self.recipe_slots:
                arcade.draw_texture_rect(
                    self.images["slot"],
                    arcade.XYWH(slot["x"], slot["y"], RECIPE_ICON_SIZE, RECIPE_ICON_SIZE),
                )
                arcade.draw_texture_rect(
                    self.images[slot["result"]],
                    arcade.XYWH(slot["x"], slot["y"], RECIPE_ICON_SIZE - 6, RECIPE_ICON_SIZE - 6),
                )

        if self.chest is not None:
            first = self.chest_slots[0]
            last = self.chest_slots[-1]
            arcade.draw_lrbt_rectangle_filled(
                first["x"] - SLOT_SIZE, last["x"] + SLOT_SIZE,
                last["y"] - SLOT_SIZE, first["y"] + SLOT_SIZE,
                (40, 40, 40, 230),
            )
            titel = "Drill" if self.chest.ore_type == "drill" else "Kiste"
            arcade.draw_text(
                titel,
                SCREEN_WIDTH / 2, first["y"] + SLOT_SIZE / 2 + 6,
                arcade.color.WHITE, font_size=14, anchor_x="center",
            )

        if self.generator is not None:
            x = self.energy["x"]
            y = self.energy["y"]
            arcade.draw_lrbt_rectangle_filled(
                x - SLOT_SIZE * 2.5, x + SLOT_SIZE * 1.5,
                y - SLOT_SIZE * 1.5, y + SLOT_SIZE * 1.5,
                (40, 40, 40, 230),
            )
            arcade.draw_text(
                "Generator",
                x - SLOT_SIZE / 2, y + SLOT_SIZE / 2 + 12,
                arcade.color.WHITE, font_size=14, anchor_x="center",
            )
            arcade.draw_texture_rect(
                self.images["energy"],
                arcade.XYWH(x - SLOT_SIZE - 10, y, SLOT_SIZE - 8, SLOT_SIZE - 8),
            )
            if self.generator.burn_timer > 0:
                arcade.draw_text(
                    "brennt noch " + str(int(self.generator.burn_timer) + 1) + "s",
                    x - SLOT_SIZE / 2, y - SLOT_SIZE,
                    arcade.color.YELLOW, font_size=12, anchor_x="center",
                )

        for slot in self.slots:
            if self.slot_visible(slot):
                self.draw_slot(slot)

        chosen = self.hotbar[self.selected_slot]
        arcade.draw_lrbt_rectangle_outline(
            chosen["x"] - SLOT_SIZE / 2, chosen["x"] + SLOT_SIZE / 2,
            chosen["y"] - SLOT_SIZE / 2, chosen["y"] + SLOT_SIZE / 2,
            arcade.color.YELLOW, 3,
        )

        if self.in_hand:
            size = (SLOT_SIZE - 8) * DRAG_SCALE
            mx, my = self.mouse_pos
            arcade.draw_texture_rect(self.images[self.in_hand["type"]], arcade.XYWH(mx, my, size, size))


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
            arcade.key.LSHIFT: False,
            arcade.key.RSHIFT: False,
            arcade.key.E: False,
            arcade.key.C: False,
        }
        self.e_mining = False
        self.mouse_mining = False

        self.mine_target   = None
        self.mine_progress = 0.0
        self.facing        = (0, -1)
        self.inventory     = Inventory()
        self.mouse_pos     = (0, 0)

        self.build_world()
        self.physics = arcade.PhysicsEngineSimple(self.player_hitbox, self.stone_list)

    def build_world(self):
        self.stone_list  = arcade.SpriteList(use_spatial_hash=True)
        self.drop_list   = arcade.SpriteList(use_spatial_hash=True)
        self.walk_through_list   = arcade.SpriteList(use_spatial_hash=True)

        self.wire_textures = {
            "gerade": arcade.load_texture("wire.png"),
            "kurve":  arcade.load_texture("wire_curve.png"),
            "t":      arcade.load_texture("3_way wire.png"),
            "kreuz":  arcade.load_texture("4_way wire.png"),
        }
        self.table_list  = arcade.SpriteList()
        self.chest_list  = arcade.SpriteList()
        self.generator_list = arcade.SpriteList()
        self.charging_doc_list = arcade.SpriteList()
        self.drill_list = arcade.SpriteList()

        self.drill_charge = 0.0
        self.charging_doc_textures = {
            "leer":  arcade.load_texture("charging_doc.png"),
            "laedt": arcade.load_texture("charging_doc_id.png"),
        }
        self.powered_wires  = []
        self.player_list = arcade.SpriteList()

        vorne  = [arcade.load_texture("player1.png"), arcade.load_texture("player2.png")]
        seite  = [arcade.load_texture("player3.png"), arcade.load_texture("player4.png")]
        hinten = [arcade.load_texture("player5.png"), arcade.load_texture("player6.png")]
        self.player_textures = {
            (0, -1): vorne,
            (0, 1):  hinten,
            (1, 0):  seite,
            (-1, 0): [seite[0].flip_left_right(), seite[1].flip_left_right()],
        }
        self.walk_frame = 0
        self.walk_timer = 0.0

        self.player = arcade.Sprite(vorne[0], PLAYER_SCALE)
        self.player.center_x = WORLD_WIDTH / 2
        self.player.center_y = WORLD_HEIGHT / 2
        self.player_list.append(self.player)

        self.player_hitbox = arcade.Sprite("player_hitbox.png", 1)
        self.player_hitbox.center_x = self.player.center_x
        self.player_hitbox.center_y = self.player.center_y

        for x in range(0, WORLD_WIDTH, TILE_SIZE):
            for y in range(0, WORLD_HEIGHT, TILE_SIZE):
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
                self.stone_list.append(stone)

        self.camera     = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.player_light = Light(
            self.player.center_x, self.player.center_y,
            PLAYER_LIGHT_SIZE, arcade.csscolor.WHITE, "soft")
        self.light_layer.add(self.player_light)

    def current_tool(self):
        tool = self.inventory.current_tool()
        if tool == "iron_drill" and self.drill_charge <= 0:
            return "hand"
        return tool

    def mine_time(self):
        return MINE_TIME[self.current_tool()]

    def tile_in_front(self):
        fx, fy = self.facing
        tile_x = round((self.player_hitbox.center_x + fx * TILE_SIZE) / TILE_SIZE) * TILE_SIZE
        tile_y = round((self.player_hitbox.center_y + fy * TILE_SIZE) / TILE_SIZE) * TILE_SIZE
        return tile_x, tile_y

    def place_crafting_block(self, tile_x, tile_y):
        block = arcade.Sprite("crafting_block.png", 0.5)
        block.center_x = tile_x
        block.center_y = tile_y
        block.ore_type = "crafting_block"
        self.stone_list.append(block)
        self.table_list.append(block)

    def near_crafting_table(self):
        for table in self.table_list:
            if arcade.get_distance_between_sprites(self.player_hitbox, table) <= CRAFT_TABLE_RANGE:
                return True
        return False

    def place_chest(self, tile_x, tile_y):
        chest = arcade.Sprite("chest.png", 1)
        chest.center_x = tile_x
        chest.center_y = tile_y
        chest.ore_type = "chest"
        chest.items = []
        for i in range(CHEST_ROWS * CHEST_COLS):
            chest.items.append({"type": None, "count": 0})
        self.stone_list.append(chest)
        self.chest_list.append(chest)
        
    def place_doc(self, tile_x, tile_y):
        doc = arcade.Sprite("charging_doc.png", 1)
        doc.center_x = tile_x
        doc.center_y = tile_y
        doc.ore_type = "charging_doc"
        self.stone_list.append(doc)
        
             
        
    

    def generator_nearby(self):
        for gen in self.generator_list:
            if arcade.get_distance_between_sprites(self.player_hitbox, gen) <= CRAFT_TABLE_RANGE:
                return gen
        return None

    def generator_fuel_slot(self, gen):
        if self.inventory.generator is gen:
            return self.inventory.energy
        return gen.fuel

    def update_generators(self, delta_time):
        for gen in self.generator_list:
            if gen.burn_timer > 0:
                gen.burn_timer -= delta_time
            if gen.burn_timer <= 0:
                gen.burn_timer = 0.0
                fuel = self.generator_fuel_slot(gen)
                if fuel["type"] == "coal" and fuel["count"] > 0:
                    fuel["count"] -= 1
                    if fuel["count"] <= 0:
                        fuel["type"] = None
                        fuel["count"] = 0
                    gen.burn_timer = GENERATOR_BURN_TIME

    def set_light(self, sprite, an, size, color):
        if an and sprite.light is None:
            sprite.light = Light(sprite.center_x, sprite.center_y, size, color, "soft")
            self.light_layer.add(sprite.light)
        if not an and sprite.light is not None:
            self.light_layer.remove(sprite.light)
            sprite.light = None

    def update_power(self):
        versorgt   = []
        zu_pruefen = []
        for gen in self.generator_list:
            an = gen.burn_timer > 0
            self.set_light(gen, an, GENERATOR_LIGHT_SIZE, GENERATOR_LIGHT_COLOR)
            if an:
                wire = self.wire_at(*self.port_tile(gen))
                if wire is not None and wire not in versorgt:
                    versorgt.append(wire)
                    zu_pruefen.append((wire.center_x, wire.center_y))

        while zu_pruefen:
            x, y = zu_pruefen.pop()
            for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
                wire = self.wire_at(x + dx * TILE_SIZE, y + dy * TILE_SIZE)
                if wire is not None and wire not in versorgt:
                    versorgt.append(wire)
                    zu_pruefen.append((wire.center_x, wire.center_y))

        for sprite in self.walk_through_list:
            if sprite.ore_type == "wire":
                sprite.powered = sprite in versorgt
                self.set_light(sprite, sprite.powered, WIRE_LIGHT_SIZE, WIRE_LIGHT_COLOR)

        self.powered_wires = versorgt

    def has_power(self, x, y):
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            nx = x + dx * TILE_SIZE
            ny = y + dy * TILE_SIZE
            wire = self.wire_at(nx, ny)
            if wire is not None and wire in self.powered_wires:
                return True
            for gen in self.generator_list:
                if gen.burn_timer > 0 and gen.center_x == nx and gen.center_y == ny:
                    return True
        return False

    def chest_nearby(self):
        for chest in self.chest_list:
            if arcade.get_distance_between_sprites(self.player_hitbox, chest) <= CRAFT_TABLE_RANGE:
                return chest
        return None

    def spill_chest(self, chest):
        for slot in chest.items:
            for i in range(slot["count"]):
                drop = arcade.Sprite(f"{slot['type']}.png", 0.6)
                drop.center_x = chest.center_x + random.uniform(-TILE_SIZE, TILE_SIZE)
                drop.center_y = chest.center_y + random.uniform(-TILE_SIZE, TILE_SIZE)
                drop.item_type = slot["type"]
                self.drop_list.append(drop)
                
    def place_wire(self, tile_x, tile_y):
        wire = arcade.Sprite("wire.png", )
        wire.center_x = tile_x
        wire.center_y = tile_y
        wire.ore_type = "wire"
        wire.light = None
        self.walk_through_list.append(wire)
        self.update_wire_look(wire)
        self.update_wires_around(tile_x, tile_y)

    def wire_at(self, x, y):
        for sprite in self.walk_through_list:
            if sprite.ore_type == "wire" and sprite.center_x == x and sprite.center_y == y:
                return sprite
        return None

    def port_tile(self, sprite):
        if sprite.ore_type == "generator":
            return (sprite.center_x - TILE_SIZE, sprite.center_y)
        if sprite.angle == 90:
            return (sprite.center_x - TILE_SIZE, sprite.center_y)
        if sprite.angle == 180:
            return (sprite.center_x, sprite.center_y + TILE_SIZE)
        if sprite.angle == 270:
            return (sprite.center_x + TILE_SIZE, sprite.center_y)
        return (sprite.center_x, sprite.center_y - TILE_SIZE)

    def power_at_port(self, sprite):
        px, py = self.port_tile(sprite)
        wire = self.wire_at(px, py)
        if wire is not None and wire in self.powered_wires:
            return True
        for gen in self.generator_list:
            if gen.burn_timer > 0 and gen.center_x == px and gen.center_y == py:
                if self.port_tile(gen) == (sprite.center_x, sprite.center_y):
                    return True
        return False

    def connects_at(self, x, y, wire_x, wire_y):
        if self.wire_at(x, y):
            return True
        for sprite in arcade.get_sprites_at_point((x, y), self.stone_list):
            if sprite.ore_type in NEEDS_POWER:
                return True
            if sprite.ore_type in ("generator", "charging_doc", "drill"):
                if self.port_tile(sprite) == (wire_x, wire_y):
                    return True
        return False

    def update_wire_look(self, wire):
        wx, wy = wire.center_x, wire.center_y
        oben   = self.connects_at(wx, wy + TILE_SIZE, wx, wy)
        unten  = self.connects_at(wx, wy - TILE_SIZE, wx, wy)
        links  = self.connects_at(wx - TILE_SIZE, wy, wx, wy)
        rechts = self.connects_at(wx + TILE_SIZE, wy, wx, wy)

        kurven = {
            (False, True,  True,  False): 0,
            (True,  False, True,  False): 90,
            (True,  False, False, True ): 180,
            (False, True,  False, True ): 270,
        }
        nachbarn = (oben, unten, links, rechts)
        if nachbarn in kurven:
            wire.texture = self.wire_textures["kurve"]
            wire.angle = kurven[nachbarn]
            return

        if nachbarn == (True, True, True, True):
            wire.texture = self.wire_textures["kreuz"]
            wire.angle = 0
            return

        t_stuecke = {
            (False, True,  True,  True ): 0,
            (True,  True,  True,  False): 90,
            (True,  False, True,  True ): 180,
            (True,  True,  False, True ): 270,
        }
        if nachbarn in t_stuecke:
            wire.texture = self.wire_textures["t"]
            wire.angle = t_stuecke[nachbarn]
            return

        wire.texture = self.wire_textures["gerade"]
        if (links or rechts) and not (oben or unten):
            wire.angle = 90
        else:
            wire.angle = 0

    def update_wires_around(self, tile_x, tile_y):
        for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            wire = self.wire_at(tile_x + dx * TILE_SIZE, tile_y + dy * TILE_SIZE)
            if wire:
                self.update_wire_look(wire)


    def place_torch(self, tile_x, tile_y):
        torch = arcade.Sprite("torch.png", )
        torch.center_x = tile_x
        torch.center_y = tile_y
        torch.ore_type = "torch"
        self.walk_through_list.append(torch)

        torch.light = Light(tile_x, tile_y, TORCH_LIGHT_SIZE, TORCH_LIGHT_COLOR, "soft")
        self.light_layer.add(torch.light)
        
    def place_generator(self, tile_x, tile_y):
        gen = arcade.Sprite("generator.png", 1)
        gen.center_x = tile_x
        gen.center_y = tile_y
        gen.ore_type = "generator"
        gen.fuel = {"type": None, "count": 0}
        gen.burn_timer = 0.0
        gen.light = None
        self.stone_list.append(gen)
        self.generator_list.append(gen)
        gen.angle = self.facing_angle()
        self.update_wires_around(tile_x, tile_y)

    def facing_angle(self):
        fx, fy = self.facing
        if fx > 0:
            return 90
        if fx < 0:
            return 270
        if fy < 0:
            return 180
        return 0

    def place_drill(self, tile_x, tile_y):
        drill = arcade.Sprite("drill.png", 1)
        drill.center_x = tile_x
        drill.center_y = tile_y
        drill.ore_type = "drill"
        drill.angle = self.facing_angle()
        drill.powered = False
        drill.farm_timer = 0.0
        drill.items = []
        for i in range(CHEST_ROWS * CHEST_COLS):
            drill.items.append({"type": None, "count": 0})
        self.stone_list.append(drill)
        self.drill_list.append(drill)
        self.chest_list.append(drill)
        self.update_wires_around(tile_x, tile_y)

    def update_drill_machines(self, delta_time):
        for drill in self.drill_list:
            an = self.power_at_port(drill)
            drill.powered = an
            if not an:
                continue

            drill.farm_timer += delta_time
            if drill.farm_timer >= DRILL_FARM_TIME:
                drill.farm_timer = 0.0
                erz = random.choice(ORE_POOLS["pickaxe_diamond"])
                if erz is not None:
                    if self.inventory.chest is drill:
                        self.put_in_storage(self.inventory.chest_slots, erz)
                    else:
                        self.put_in_storage(drill.items, erz)

    def put_in_storage(self, items, item_type):
        for slot in items:
            if slot["type"] == item_type:
                slot["count"] += 1
                return True
        for slot in items:
            if slot["type"] is None:
                slot["type"] = item_type
                slot["count"] = 1
                return True
        return False

    def stones_on_tile(self, tile_x, tile_y):
        stones = []
        for drop in self.drop_list:
            if drop.item_type != "stone":
                continue
            drop_x = round(drop.center_x / TILE_SIZE) * TILE_SIZE
            drop_y = round(drop.center_y / TILE_SIZE) * TILE_SIZE
            if drop_x == tile_x and drop_y == tile_y:
                stones.append(drop)
        return stones

    def place_charging_doc(self, tile_x, tile_y):
        doc = arcade.Sprite("charging_doc.png", 1)
        doc.center_x = tile_x
        doc.center_y = tile_y
        doc.ore_type = "charging_doc"
        doc.light = None
        doc.powered = False
        doc.drill_inside = False
        doc.charge_progress = 0.0
        self.stone_list.append(doc)
        self.charging_doc_list.append(doc)
        self.update_wires_around(tile_x, tile_y)

    def update_charging_docs(self):
        for doc in self.charging_doc_list:
            an = self.power_at_port(doc)
            doc.powered = an
            self.set_light(doc, an, CHARGING_DOC_LIGHT_SIZE, CHARGING_DOC_LIGHT_COLOR)

    def charging_doc_at(self, x, y):
        for doc in self.charging_doc_list:
            if doc.center_x == x and doc.center_y == y:
                return doc
        return None

    def dock_with_drill_nearby(self):
        for doc in self.charging_doc_list:
            if doc.drill_inside and arcade.get_distance_between_sprites(self.player_hitbox, doc) <= CRAFT_TABLE_RANGE:
                return doc
        return None

    def take_drill_from_dock(self, doc):
        if not self.inventory.add_to_hotbar("iron_drill", 1):
            return
        if doc.charge_progress >= DRILL_CHARGE_TIME:
            self.drill_charge = DRILL_POWER_TIME
        doc.drill_inside = False
        doc.charge_progress = 0.0
        doc.texture = self.charging_doc_textures["leer"]

    def update_drill(self, delta_time):
        if self.drill_charge > 0:
            self.drill_charge -= delta_time
            if self.drill_charge < 0:
                self.drill_charge = 0.0

        for doc in self.charging_doc_list:
            if doc.drill_inside and doc.powered and doc.charge_progress < DRILL_CHARGE_TIME:
                doc.charge_progress += delta_time
                if doc.charge_progress > DRILL_CHARGE_TIME:
                    doc.charge_progress = DRILL_CHARGE_TIME

    def drop_item(self):
        item_type = self.inventory.drop_one()
        if not item_type:
            return
        tile_x, tile_y = self.tile_in_front()

        if item_type == "crafting_block":
            self.place_crafting_block(tile_x, tile_y)
            return
        if item_type == "chest":
            self.place_chest(tile_x, tile_y)
            return
        if item_type == "wire":
            self.place_wire(tile_x, tile_y)
            return
        if item_type == "torch":
            self.place_torch(tile_x, tile_y)
            return
        if item_type == "generator":
            self.place_generator(tile_x, tile_y)
            return
        if item_type == "charging_doc":
            self.place_charging_doc(tile_x, tile_y)
            return
        if item_type == "drill":
            self.place_drill(tile_x, tile_y)
            return
        if item_type == "iron_drill":
            doc = self.charging_doc_at(tile_x, tile_y)
            if doc is not None and not doc.drill_inside:
                doc.drill_inside = True
                doc.charge_progress = 0.0
                doc.texture = self.charging_doc_textures["laedt"]
                return

        drop = arcade.Sprite(f"{item_type}.png", 0.6)
        drop.center_x = tile_x + random.uniform(-DROP_JITTER, DROP_JITTER)
        drop.center_y = tile_y + random.uniform(-DROP_JITTER, DROP_JITTER)
        drop.item_type = item_type
        self.drop_list.append(drop)

        if item_type == "stone":
            stones = self.stones_on_tile(tile_x, tile_y)
            if len(stones) >= STONES_TO_BLOCK:
                for stone in stones:
                    stone.remove_from_sprite_lists()
                self.place_crafting_block(tile_x, tile_y)

    def camera_position(self):
        x = max(SCREEN_WIDTH  / 2, min(self.player.center_x, WORLD_WIDTH  - SCREEN_WIDTH  / 2))
        y = max(SCREEN_HEIGHT / 2, min(self.player.center_y, WORLD_HEIGHT - SCREEN_HEIGHT / 2))
        return x, y

    def give_all_ores(self):
        for ore in ["stone", "coal", "copper", "iron", "diamond" ]:
            self.inventory.add_to_hotbar(ore, 9)

    def update_mining(self, delta_time):
        if not self.mine_target:
            return

        if arcade.get_distance_between_sprites(self.player_hitbox, self.mine_target) > MINE_RANGE:
            self.mine_target   = None
            self.mine_progress = 0.0
            return

        self.mine_progress += delta_time
        if self.mine_progress < self.mine_time():
            return

        if self.mine_target.ore_type in ("chest", "drill"):
            self.spill_chest(self.mine_target)

        if self.mine_target.ore_type == "charging_doc" and self.mine_target.drill_inside:
            drop = arcade.Sprite("iron_drill.png", 0.6)
            drop.center_x = self.mine_target.center_x + random.uniform(-TILE_SIZE, TILE_SIZE)
            drop.center_y = self.mine_target.center_y + random.uniform(-TILE_SIZE, TILE_SIZE)
            drop.item_type = "iron_drill"
            self.drop_list.append(drop)

        if self.mine_target.ore_type == "generator":
            for i in range(self.mine_target.fuel["count"]):
                drop = arcade.Sprite("coal.png", 0.6)
                drop.center_x = self.mine_target.center_x + random.uniform(-TILE_SIZE, TILE_SIZE)
                drop.center_y = self.mine_target.center_y + random.uniform(-TILE_SIZE, TILE_SIZE)
                drop.item_type = "coal"
                self.drop_list.append(drop)

        if self.mine_target.ore_type is not None:
            loot = self.mine_target.ore_type
        else:
            pool = ORE_POOLS[self.current_tool()]
            loot = random.choice(pool)

        if loot is not None:
            drop = arcade.Sprite(f"{loot}.png", 0.6)
            drop.center_x = self.mine_target.center_x + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.center_y = self.mine_target.center_y + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.item_type = loot
            self.drop_list.append(drop)

        if getattr(self.mine_target, "light", None) is not None:
            self.light_layer.remove(self.mine_target.light)

        self.mine_target.remove_from_sprite_lists()

        if self.mine_target.ore_type in ("wire", "generator", "charging_doc", "drill"):
            self.update_wires_around(self.mine_target.center_x, self.mine_target.center_y)

        self.mine_target   = None
        self.mine_progress = 0.0

    def on_key_press(self, key, _modifiers):
        if key in self.keys:
            self.keys[key] = True
        if arcade.key.KEY_1 <= key <= arcade.key.KEY_9:
            self.inventory.selected_slot = key - arcade.key.KEY_1
        if key == arcade.key.Q:
            self.drop_item()
        if key == arcade.key.G:
            self.give_all_ores()
        if key == arcade.key.E:
            if self.inventory.crafting_open:
                self.inventory.crafting_open = False
            elif self.inventory.chest is not None:
                self.inventory.close_chest()
            elif self.inventory.generator is not None:
                self.inventory.close_generator()
            elif self.dock_with_drill_nearby() is not None:
                self.take_drill_from_dock(self.dock_with_drill_nearby())
            elif self.near_crafting_table():
                self.inventory.crafting_open = True
                self.inventory.check_recipe()
                self.mine_target   = None
                self.mine_progress = 0.0
            else:
                chest = self.chest_nearby()
                if chest is not None:
                    self.inventory.open_chest(chest)
                    self.mine_target   = None
                    self.mine_progress = 0.0
                else:
                    gen = self.generator_nearby()
                    if gen is not None:
                        self.inventory.open_generator(gen)
                        self.mine_target   = None
                        self.mine_progress = 0.0
                    else:
                        self.e_mining = True
                        self.target_block_in_front()
        if key == arcade.key.C:
            menu_offen = (self.inventory.crafting_open
                          or self.inventory.chest is not None
                          or self.inventory.generator is not None)
            if not menu_offen:
                self.e_mining = True
                self.target_block_in_front()

    def target_block_in_front(self):
        tile_x, tile_y = self.tile_in_front()
        hits = arcade.get_sprites_at_point((tile_x, tile_y), self.stone_list)
        if not hits:
            hits = arcade.get_sprites_at_point((tile_x, tile_y), self.walk_through_list)
        if hits:
            self.mine_target   = hits[0]
            self.mine_progress = 0.0

    def on_key_release(self, key, _modifiers):
        if key in self.keys:
            self.keys[key] = False
        if key in (arcade.key.E, arcade.key.C):
            if not (self.keys[arcade.key.E] or self.keys[arcade.key.C] or self.mouse_mining):
                self.e_mining      = False
                self.mine_target   = None
                self.mine_progress = 0.0

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse_pos = (x, y)
        self.inventory.mouse_pos = (x, y)
        self.inventory.track_drag(x, y)

    def on_mouse_scroll(self, _x, _y, _scroll_x, scroll_y):
        self.inventory.selected_slot = (self.inventory.selected_slot - int(scroll_y)) % HOTBAR_SLOTS

    def on_mouse_press(self, x, y, button, _modifiers):
        menu_open = (self.inventory.crafting_open
                     or self.inventory.chest is not None
                     or self.inventory.generator is not None)
        if menu_open:
            if self.inventory.crafting_open and button == arcade.MOUSE_BUTTON_LEFT:
                index = self.inventory.recipe_index_at(x, y)
                if index is not None:
                    self.inventory.fill_recipe(index)
                    return
            if button in (arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT):
                self.inventory.start_drag(x, y, only_one=(button == arcade.MOUSE_BUTTON_RIGHT))
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_mining = True
            self.e_mining = True
            self.target_block_in_front()


    def on_mouse_release(self, x, y, button, _modifiers):
        if button not in (arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT):
            return

        if (self.inventory.crafting_open
                or self.inventory.chest is not None
                or self.inventory.generator is not None):
            self.inventory.end_drag(x, y)
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_mining = False
            if not (self.keys[arcade.key.E] or self.keys[arcade.key.C]):
                self.e_mining      = False
                self.mine_target   = None
                self.mine_progress = 0.0

    def player_texture(self):
        fx, fy = self.facing
        if fx != 0:
            frames = self.player_textures[(fx, 0)]
        else:
            frames = self.player_textures[(0, fy)]
        return frames[self.walk_frame]

    def on_update(self, delta_time):
        sprinting = self.keys[arcade.key.LSHIFT] or self.keys[arcade.key.RSHIFT]
        speed = SPRINT_SPEED if sprinting else WALK_SPEED

        dir_x = self.keys[arcade.key.D] - self.keys[arcade.key.A]
        dir_y = self.keys[arcade.key.W] - self.keys[arcade.key.S]
        if dir_x or dir_y:
            self.facing = (dir_x, dir_y)
            self.walk_timer += delta_time
            if self.walk_timer >= PLAYER_FRAME_TIME:
                self.walk_timer -= PLAYER_FRAME_TIME
                self.walk_frame = 1 - self.walk_frame
        else:
            self.walk_frame = 0
            self.walk_timer = 0.0
        self.player.texture = self.player_texture()

        self.player_hitbox.change_x = dir_x * speed
        self.player_hitbox.change_y = dir_y * speed
        self.physics.update()

        self.player.center_x = self.player_hitbox.center_x
        self.player.center_y = self.player_hitbox.center_y
        self.player_light.position = self.player.position
        
        

        menu_offen = (self.inventory.crafting_open
                      or self.inventory.chest is not None
                      or self.inventory.generator is not None)
        taste_gehalten = self.keys[arcade.key.E] or self.keys[arcade.key.C] or self.mouse_mining
        if self.e_mining and taste_gehalten and not menu_offen and self.mine_target is None:
            self.target_block_in_front()

        self.update_mining(delta_time)
        self.update_generators(delta_time)
        self.update_power()
        self.update_charging_docs()
        self.update_drill(delta_time)
        self.update_drill_machines(delta_time)

        for drop in arcade.check_for_collision_with_list(self.player_hitbox, self.drop_list):
            if self.inventory.add_to_hotbar(drop.item_type, 1):
                drop.remove_from_sprite_lists()

        self.camera.position = self.camera_position()

    def on_draw(self):
        self.clear()

        self.camera.use()
        with self.light_layer:
            self.stone_list.draw()
            self.walk_through_list.draw()
            self.drop_list.draw()
            self.player_list.draw(pixelated=True)
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        frame = self.inventory.images["slot"]
        tx, ty = self.tile_in_front()
        arcade.draw_texture_rect(frame, arcade.XYWH(tx, ty, TILE_SIZE, TILE_SIZE))

        if self.mine_target:
            arcade.draw_texture_rect(frame, arcade.XYWH(
                self.mine_target.center_x, self.mine_target.center_y, TILE_SIZE, TILE_SIZE))

        for doc in self.charging_doc_list:
            if doc.charge_progress > 0:
                ratio = doc.charge_progress / DRILL_CHARGE_TIME
                bx = doc.center_x
                by = doc.center_y + 22
                arcade.draw_lrbt_rectangle_filled(bx - 16, bx - 16 + 32 * ratio, by - 3, by + 3, arcade.color.GREEN)
                arcade.draw_lrbt_rectangle_outline(bx - 16, bx + 16, by - 3, by + 3, arcade.color.WHITE, 1)

        if self.mine_target:
            ratio = self.mine_progress / self.mine_time()
            bx = self.mine_target.center_x
            by = self.mine_target.center_y + 20
            arcade.draw_lrbt_rectangle_filled(bx - 16, bx - 16 + 32 * ratio, by - 3, by + 3, arcade.color.YELLOW)
            arcade.draw_lrbt_rectangle_outline(bx - 16, bx + 16, by - 3, by + 3, arcade.color.WHITE, 1)

        self.gui_camera.use()
        self.inventory.draw()

        if self.inventory.hotbar[self.inventory.selected_slot]["type"] == "iron_drill":
            if self.drill_charge > 0:
                text = "Drill: " + str(int(self.drill_charge) + 1) + "s"
                farbe = arcade.color.GREEN
            else:
                text = "Drill: leer (mit Q ins charging doc legen)"
                farbe = arcade.color.ORANGE
            arcade.draw_text(text, SCREEN_WIDTH / 2, SLOT_SIZE + 16,
                             farbe, font_size=12, anchor_x="center")


Game()
arcade.run()
