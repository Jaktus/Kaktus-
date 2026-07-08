import arcade
from arcade.future.light import Light, LightLayer
import random


# undergrounders 2
# steuerung:
#   W A S D        = laufen, shift = sprinten
#   linksklick     = stein abbauen (gedrueckt halten)
#   Q              = 1 item vor den spieler werfen
#   E              = crafting menue / kiste auf und zu
#   1-9 / mausrad  = hotbar slot waehlen

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
WORLD_WIDTH   = 4000
WORLD_HEIGHT  = 4000


WALK_SPEED   = 2
SPRINT_SPEED = 3

MINE_RANGE = 48    # wie nah man am stein sein muss

PLAYER_FRAME_TIME = 0.18   # so viele sekunden wird jeder lauf-frame gezeigt
PLAYER_SCALE      = 1      # wie gross der spieler gezeichnet wird

# licht: ohne lampe sieht man nur so viel (schwarz = stockdunkel)
AMBIENT_COLOR      = (10, 10, 60)
PLAYER_LIGHT_SIZE  = 100   # radius vom licht das dem spieler folgt
TORCH_LIGHT_SIZE   = 150   # radius vom licht einer fackel
TORCH_LIGHT_COLOR  = (220, 220, 255)   # warmes feuer-orange

# wie viele sekunden das abbauen dauert, pro werkzeug
MINE_TIME = {
    "hand":            1.0,
    "pickaxe":         0.6,
    "pickaxe_iron":    0.4,
    "pickaxe_diamond": 0.15,
}

HOTBAR_SLOTS = 9
SLOT_SIZE    = 48
SLOT_GAP     = 4

TILE_SIZE       = 32
DROP_JITTER     = 6
STONES_TO_BLOCK = 4    # 4 steine auf einer kachel = 1 crafting block

GRID_ROWS  = 5
GRID_COLS  = 5
DRAG_SCALE = 1.5

CHEST_ROWS = 3    # so viele faecher hat eine kiste
CHEST_COLS = 5

# (erz, prozent) - so viele von 100 steinen geben dieses erz.
# fuer jedes werkzeug gibt es eine eigene tabelle:
# je besser die spitzhacke, desto besser die chancen!
# (mit blossen haenden findet man keine diamanten)
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
    # baut einen lostopf mit 100 losen: jedes erz liegt so oft drin
    # wie sein prozent-wert, die restlichen lose sind nieten (None)
    pool = []
    for name, percent in table:
        for i in range(percent):
            pool.append(name)
    while len(pool) < 100:
        pool.append(None)
    return pool


# fuer jedes werkzeug ein eigener lostopf
ORE_POOLS = {
    "hand":            make_pool(ORE_TABLE_HAND),
    "pickaxe":         make_pool(ORE_TABLE_PICKAXE),
    "pickaxe_iron":    make_pool(ORE_TABLE_IRON_PICKAXE),
    "pickaxe_diamond": make_pool(ORE_TABLE_DIAMOND_PICKAXE),
}

# welcher buchstabe fuer welches item in den rezepten steht.
# kleiner buchstabe = material, grosser buchstabe = fertiger kopf daraus
LETTERS = {
    
    "stone":                "s",
    "copper_stick":         "k",   # muss genau 1 zeichen sein!
    "coal":                 "o",
    "copper":               "c",
    "iron":                 "i",
    "diamond":              "d",
    "pickaxe_handle":       "h",
    "pickaxe_head":         "S",
    "pickaxe_iron_head":    "I",
    "pickaxe_diamond_head": "D",
}

# rezepte: einfach neue dazuschreiben! "." heisst leeres feld.
# es zaehlt nur die form, egal wo im gitter sie liegt
RECIPES = [
    ("pickaxe_handle",       ["sss"]),
    
    ("copper_stick",         ["c",
                              "c",
                              "c",
                              "c"]),                # 4 kupfer nebeneinander
    ("torch",                ["o",
                              "k"]),                # kohle auf kupferstab
    ("wire",                 ["c",
                              "c",
                              "c"]),
    ("wire_curve",           ["cc",
                              ".c"]),
    ("pickaxe_handle",       ["s..",
                              ".s.",
                              "..s"]),              # 3 steine diagonal
    ("pickaxe_handle",       ["..s",
                              ".s.",
                              "s.."]),              # andere diagonale
    ("hammer",               ["iii",
                              "sss",
                              ".h."]),              # eisen, steine, stiel drunter
    ("crafting_block",       ["ss",
                              "ss"]),               # 2x2 steine
    ("chest",                ["sss",
                              "s.s",
                              "sss"]),              # ring aus 8 steinen
    ("pickaxe_head",         ["sss",
                              "s.s"]),              # 5 steine
    ("pickaxe_iron_head",    ["iii",
                              "i.i"]),              # 5 eisen
    ("pickaxe_diamond_head", ["ddd",
                              "d.d"]),              # 5 diamanten
    ("pickaxe",              ["S",
                              "h"]),                # stein-kopf auf stiel
    ("pickaxe_iron",         ["I",
                              "h"]),                # eisen-kopf auf stiel
    ("pickaxe_diamond",      ["D",
                              "h"]),                # diamant-kopf auf stiel
]

# wie viel kohle jedes rezept aus dem kohle-slot verbraucht
COAL_COST = {
    "copper_stick":         1,
    "torch":                1,
    "wire_curve":           1,
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
}

# diese rezepte gehen nur wenn ein hammer in der hotbar liegt
NEEDS_HAMMER = ["pickaxe", "pickaxe_iron", "pickaxe_diamond"]

CRAFT_TABLE_RANGE = 64   # wie nah man am crafting table stehen muss


class Inventory:
    def __init__(self):
        self.selected_slot = 0
        self.crafting_open = False
        self.in_hand       = None     # item das gerade an der maus haengt
        self.mouse_pos     = (0, 0)
        self.craft_hint    = ""       # hinweis-text, z.b. "Braucht 3 Kohle!"
        self.chest         = None     # die kiste die gerade offen ist
        self.drag_slots    = []       # slots die beim verteilen schon 1 bekommen haben
        self.drag_source   = None     # quell-slot beim verteilen (rechtsklick gehalten)

        self.images = {
            "wire_curve":      arcade.load_texture("wire_curve.png"),
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

            "pickaxe_iron":         arcade.load_texture("pickaxe_iron.png"),
            "pickaxe_iron_head":    arcade.load_texture("pickaxe_iron_head.png"),
            "pickaxe_diamond":      arcade.load_texture("pickaxe_diamond.png"),
            "pickaxe_diamond_head": arcade.load_texture("pickaxe_diamond_head.png"),
        }
        self.crafting_image = arcade.load_texture("crafting_gui.png")

        self.build_slots()

    def new_slot(self, kind, x, y):
        # ein slot weiss selber wo er auf dem bildschirm liegt
        slot = {"kind": kind, "x": x, "y": y, "type": None, "count": 0}
        self.slots.append(slot)
        return slot

    def build_slots(self):
        # alle slots einmal anlegen, jeder bekommt seine position
        self.slots = []

        # die hotbar, unten in der mitte
        total = HOTBAR_SLOTS * SLOT_SIZE + (HOTBAR_SLOTS - 1) * SLOT_GAP
        left = (SCREEN_WIDTH - total) / 2
        self.hotbar = []
        for i in range(HOTBAR_SLOTS):
            x = left + i * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2
            y = SLOT_GAP + SLOT_SIZE / 2
            self.hotbar.append(self.new_slot("hotbar", x, y))

        # das crafting gitter, als tabelle mit zeilen und spalten
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

        # der output-slot rechts neben dem gitter
        x = left + grid_width + 40 + SLOT_SIZE / 2
        y = top - 2 * (SLOT_SIZE + SLOT_GAP)
        self.output = self.new_slot("output", x, y)

        # der kohle-slot unter dem gitter
        x = SCREEN_WIDTH / 2
        y = top - GRID_ROWS * (SLOT_SIZE + SLOT_GAP) - 10
        self.fuel = self.new_slot("fuel", x, y)

        # die faecher einer kiste (sieht man nur wenn eine kiste offen ist)
        self.chest_slots = []
        for row in range(CHEST_ROWS):
            for col in range(CHEST_COLS):
                x = left + col * (SLOT_SIZE + SLOT_GAP) + SLOT_SIZE / 2
                y = top - row * (SLOT_SIZE + SLOT_GAP)
                self.chest_slots.append(self.new_slot("chest", x, y))

    def clear_slot(self, slot):
        slot["type"] = None
        slot["count"] = 0

    def current_tool(self):
        # welches werkzeug haelt der spieler gerade? sonst "hand"
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
        # nimmt 1 item aus dem gewaehlten slot und gibt den typ zurueck
        slot = self.hotbar[self.selected_slot]
        if slot["type"] is None:
            return None
        item_type = slot["type"]
        slot["count"] = slot["count"] - 1
        if slot["count"] <= 0:
            self.clear_slot(slot)
        return item_type

    def add_to_hotbar(self, item_type, count):
        # erst auf einen gleichen stapel legen, sonst leeren slot nehmen
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

    # ------------------------------------------------------------------
    # items mit der maus hin und her ziehen
    # ------------------------------------------------------------------

    def mouse_in_slot(self, x, y, slot):
        # die 4 kanten vom slot ausrechnen und schauen ob die maus drin ist
        links  = slot["x"] - SLOT_SIZE / 2
        rechts = slot["x"] + SLOT_SIZE / 2
        unten  = slot["y"] - SLOT_SIZE / 2
        oben   = slot["y"] + SLOT_SIZE / 2
        return links <= x <= rechts and unten <= y <= oben

    def slot_visible(self, slot):
        # die hotbar sieht man immer, den rest nur wenn das menue offen ist
        if slot["kind"] == "hotbar":
            return True
        if slot["kind"] == "chest":
            return self.chest is not None
        return self.crafting_open

    def slot_at(self, x, y):
        # welcher slot liegt unter der maus?
        for slot in self.slots:
            if not self.slot_visible(slot):
                continue
            if self.mouse_in_slot(x, y, slot):
                return slot
        return None

    def start_drag(self, x, y, only_one=False):
        # item unter der maus in die hand nehmen.
        # linksklick bewegt den ganzen stapel, rechtsklick startet den verteil-modus
        slot = self.slot_at(x, y)
        if slot is None or slot["type"] is None:
            return
        self.drag_slots  = []
        self.drag_source = None

        # aus dem output genommen = gebaut -> kohle und zutaten verbrauchen.
        # linksklick baut gleich so viele wie die zutaten hergeben, rechtsklick nur 1
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
            # verteil-modus: quell-slot merken, da geht der rest spaeter zurueck.
            # er steht auch in drag_slots, damit nicht in ihn selbst verteilt wird
            self.drag_source = slot
            self.drag_slots  = [slot]

        self.check_recipe()

    def track_drag(self, x, y):
        # nur im verteil-modus (rechtsklick gehalten): jeder neue slot
        # unter der maus bekommt sofort 1 item aus der hand
        if self.in_hand is None or self.drag_source is None:
            return
        if self.in_hand["count"] <= 0:
            return
        slot = self.slot_at(x, y)
        if slot is None:
            return
        for done in self.drag_slots:
            if done is slot:
                return   # der hat schon eins bekommen
        if slot["kind"] == "output":
            return
        if slot["kind"] == "fuel" and self.in_hand["type"] != "coal":
            return
        if slot["type"] is not None and slot["type"] != self.in_hand["type"]:
            return

        slot["type"]  = self.in_hand["type"]
        slot["count"] = slot["count"] + 1
        self.in_hand["count"] = self.in_hand["count"] - 1
        self.drag_slots.append(slot)
        self.check_recipe()

    def end_drag(self, x, y):
        # item aus der hand in den slot unter der maus legen
        if self.in_hand is None:
            return

        # verteil-modus: der slot unterm loslassen bekommt auch noch 1,
        # der rest wandert zurueck in den quell-slot
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
            ok = False        # in den output kann man nichts reinlegen
        if ok and slot["kind"] == "fuel" and self.in_hand["type"] != "coal":
            ok = False        # in den kohle-slot darf nur kohle
        if ok and slot["type"] is not None and slot["type"] != self.in_hand["type"]:
            ok = False        # da liegt schon ein anderes item drin

        if ok:
            slot["type"] = self.in_hand["type"]
            slot["count"] = slot["count"] + self.in_hand["count"]
        else:
            # daneben losgelassen -> zurueck in die hotbar
            self.add_to_hotbar(self.in_hand["type"], self.in_hand["count"])

        self.in_hand = None
        self.check_recipe()

    # ------------------------------------------------------------------
    # rezepte
    # ------------------------------------------------------------------

    def grid_as_text(self):
        # schreibt das gitter als text auf, ein string pro zeile.
        # 3 steine nebeneinander sehen dann z.b. so aus: ["sss"]
        lines = []
        for row in self.grid:
            line = ""
            for slot in row:
                if slot["type"] is None:
                    line = line + "."
                elif slot["type"] in LETTERS:
                    line = line + LETTERS[slot["type"]]
                else:
                    line = line + "?"   # item das in keinem rezept vorkommt
            lines.append(line)

        # leere zeilen oben und unten wegschneiden
        empty_row = "." * GRID_COLS
        while len(lines) > 0 and lines[0] == empty_row:
            lines.pop(0)
        while len(lines) > 0 and lines[-1] == empty_row:
            lines.pop()

        # leere spalten links und rechts wegschneiden,
        # lines[i][1:] heisst: das erste zeichen abschneiden
        while len(lines) > 0 and self.column_empty(lines, 0):
            for i in range(len(lines)):
                lines[i] = lines[i][1:]
        while len(lines) > 0 and self.column_empty(lines, -1):
            for i in range(len(lines)):
                lines[i] = lines[i][:-1]

        return lines

    def column_empty(self, lines, col):
        # ist in dieser spalte ueberall nur ein punkt? (-1 = letzte spalte)
        for line in lines:
            if line[col] != ".":
                return False
        return True

    def check_recipe(self):
        # das gitter als text mit jedem rezept vergleichen.
        # passt eins, landet das ergebnis im output-slot
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
        # wie oft geht das rezept mit dem was gerade da liegt?
        # das kleinste feld im gitter und die kohle begrenzen es
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
        # kohle abziehen und aus jedem benutzten feld n zutaten nehmen,
        # der rest bleibt liegen
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

    # ------------------------------------------------------------------
    # kisten
    # ------------------------------------------------------------------

    def open_chest(self, chest):
        # die sachen aus der kiste in die kisten-slots legen
        self.chest = chest
        for i in range(len(self.chest_slots)):
            self.chest_slots[i]["type"] = chest.items[i]["type"]
            self.chest_slots[i]["count"] = chest.items[i]["count"]

    def close_chest(self):
        # die slots zurueck in die kiste schreiben
        for i in range(len(self.chest_slots)):
            self.chest.items[i]["type"] = self.chest_slots[i]["type"]
            self.chest.items[i]["count"] = self.chest_slots[i]["count"]
        self.chest = None

    # ------------------------------------------------------------------
    # zeichnen
    # ------------------------------------------------------------------

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
            # hinweis wenn ein rezept passt aber noch was fehlt
            if self.craft_hint != "":
                arcade.draw_text(
                    self.craft_hint,
                    self.output["x"], self.output["y"] - SLOT_SIZE,
                    arcade.color.ORANGE, font_size=12, anchor_x="center",
                )

        # kisten-menue: dunkler kasten mit titel hinter den faechern
        if self.chest is not None:
            first = self.chest_slots[0]
            last = self.chest_slots[-1]
            arcade.draw_lrbt_rectangle_filled(
                first["x"] - SLOT_SIZE, last["x"] + SLOT_SIZE,
                last["y"] - SLOT_SIZE, first["y"] + SLOT_SIZE,
                (40, 40, 40, 230),
            )
            arcade.draw_text(
                "Kiste",
                SCREEN_WIDTH / 2, first["y"] + SLOT_SIZE / 2 + 6,
                arcade.color.WHITE, font_size=14, anchor_x="center",
            )

        # alle slots zeichnen die man gerade sehen kann
        for slot in self.slots:
            if self.slot_visible(slot):
                self.draw_slot(slot)

        # gelber rahmen um den gewaehlten hotbar-slot
        chosen = self.hotbar[self.selected_slot]
        arcade.draw_lrbt_rectangle_outline(
            chosen["x"] - SLOT_SIZE / 2, chosen["x"] + SLOT_SIZE / 2,
            chosen["y"] - SLOT_SIZE / 2, chosen["y"] + SLOT_SIZE / 2,
            arcade.color.YELLOW, 3,
        )

        # das item das gerade an der maus haengt
        if self.in_hand:
            size = (SLOT_SIZE - 8) * DRAG_SCALE
            mx, my = self.mouse_pos
            arcade.draw_texture_rect(self.images[self.in_hand["type"]], arcade.XYWH(mx, my, size, size))


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Game")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # merkt sich welche tasten gerade gedrueckt sind
        self.keys = {
            arcade.key.W: False,
            arcade.key.A: False,
            arcade.key.S: False,
            arcade.key.D: False,
            arcade.key.LSHIFT: False,
            arcade.key.RSHIFT: False,
        }

        self.mine_target   = None      # stein der gerade abgebaut wird
        self.mine_progress = 0.0
        self.facing        = (0, -1)   # letzte laufrichtung
        self.inventory     = Inventory()
        self.mouse_pos     = (0, 0)

        self.build_world()
        self.physics = arcade.PhysicsEngineSimple(self.player_hitbox, self.stone_list)

    def build_world(self):
        self.stone_list  = arcade.SpriteList(use_spatial_hash=True)
        self.drop_list   = arcade.SpriteList(use_spatial_hash=True)
        self.walk_through_list   = arcade.SpriteList(use_spatial_hash=True)   # wires: nicht in der physik, man laeuft durch
        self.table_list  = arcade.SpriteList()   # alle crafting tables in der welt
        self.chest_list  = arcade.SpriteList()   # alle kisten in der welt
        self.player_list = arcade.SpriteList()

        # je 2 lauf-frames pro blickrichtung; nach links wird einfach gespiegelt
        vorne  = [arcade.load_texture("player1.png"), arcade.load_texture("player2.png")]
        seite  = [arcade.load_texture("player3.png"), arcade.load_texture("player4.png")]
        hinten = [arcade.load_texture("player5.png"), arcade.load_texture("player6.png")]
        self.player_textures = {
            (0, -1): vorne,
            (0, 1):  hinten,
            (1, 0):  seite,
            (-1, 0): [seite[0].flip_left_right(), seite[1].flip_left_right()],
        }
        self.walk_frame = 0     # welcher der 2 lauf-frames gerade dran ist
        self.walk_timer = 0.0   # zaehlt die zeit bis zum naechsten frame-wechsel

        self.player = arcade.Sprite(vorne[0], PLAYER_SCALE)
        self.player.center_x = WORLD_WIDTH / 2
        self.player.center_y = WORLD_HEIGHT / 2
        self.player_list.append(self.player)

        # unsichtbare hitbox: nur sie steckt in der physik.
        # sie ist in keiner draw-liste, darum sieht man sie nie.
        # das sichtbare bild folgt ihr einfach jeden frame
        self.player_hitbox = arcade.Sprite("player_hitbox.png", 1)
        self.player_hitbox.center_x = self.player.center_x
        self.player_hitbox.center_y = self.player.center_y

        # ganze welt mit steinen fuellen, nur die mitte bleibt frei (spawn)
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
                # None heisst: das erz wird erst beim abbauen ausgelost
                stone.ore_type = None
                self.stone_list.append(stone)

        self.camera     = arcade.Camera2D()   # folgt dem spieler
        self.gui_camera = arcade.Camera2D()   # bleibt fest, fuer die hotbar

        # licht-schicht: alles was von licht getroffen werden soll wird
        # da reingezeichnet, danach macht sie den rest dunkel
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # das licht das dem spieler folgt
        self.player_light = Light(
            self.player.center_x, self.player.center_y,
            PLAYER_LIGHT_SIZE, arcade.csscolor.WHITE, "soft")
        self.light_layer.add(self.player_light)

    def mine_time(self):
        # bessere werkzeuge bauen schneller ab
        return MINE_TIME[self.inventory.current_tool()]

    def tile_in_front(self):
        # die kachel direkt vor dem spieler, auf das raster gerundet
        fx, fy = self.facing
        tile_x = round((self.player_hitbox.center_x + fx * TILE_SIZE) / TILE_SIZE) * TILE_SIZE
        tile_y = round((self.player_hitbox.center_y + fy * TILE_SIZE) / TILE_SIZE) * TILE_SIZE
        return tile_x, tile_y

    def place_crafting_block(self, tile_x, tile_y):
        block = arcade.Sprite("crafting_block.png", 0.5)
        block.center_x = tile_x
        block.center_y = tile_y
        block.ore_type = "crafting_block"   # gibt sich beim abbauen selber zurueck
        self.stone_list.append(block)
        self.table_list.append(block)   # extra liste, damit wir schnell checken koennen ob einer in der naehe ist

    def near_crafting_table(self):
        # steht irgendein crafting table nah genug am spieler?
        for table in self.table_list:
            if arcade.get_distance_between_sprites(self.player_hitbox, table) <= CRAFT_TABLE_RANGE:
                return True
        return False

    def place_chest(self, tile_x, tile_y):
        chest = arcade.Sprite("chest.png", 1)
        chest.center_x = tile_x
        chest.center_y = tile_y
        chest.ore_type = "chest"   # gibt sich beim abbauen selber zurueck
        # jede kiste hat ihre eigenen faecher
        chest.items = []
        for i in range(CHEST_ROWS * CHEST_COLS):
            chest.items.append({"type": None, "count": 0})
        self.stone_list.append(chest)
        self.chest_list.append(chest)
        
    

    def chest_nearby(self):
        # gibt eine kiste zurueck die nah genug am spieler ist, sonst None
        for chest in self.chest_list:
            if arcade.get_distance_between_sprites(self.player_hitbox, chest) <= CRAFT_TABLE_RANGE:
                return chest
        return None

    def spill_chest(self, chest):
        # alles was in der kiste war faellt auf den boden
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
        self.walk_through_list.append(wire)
        #es wird in die richtung in die der spieler schaut gelegt, also muss man die richtung merken
        if self.facing == (0, -1):
            wire.angle = 0
        elif self.facing == (0, 1):
            wire.angle = 180
        elif self.facing == (-1, 0):
            wire.angle = 90
        elif self.facing == (1, 0):
            wire.angle = 270
        
    def place_wire_curve(self, tile_x, tile_y):
        wire_c = arcade.Sprite("wire_curve.png", )
        wire_c.center_x = tile_x
        wire_c.center_y = tile_y
        wire_c.ore_type = "wire_curve"
        self.walk_through_list.append(wire_c)
        #es wird in die richtung in die der spieler schaut gelegt, also muss man die richtung merken
        if self.facing == (0, -1):
            wire_c.angle = 0
        elif self.facing == (0, 1):
            wire_c.angle = 180
        elif self.facing == (-1, 0):
            wire_c.angle = 90
        elif self.facing == (1, 0):
            wire_c.angle = 270
            
    def place_torch(self, tile_x, tile_y):
        torch = arcade.Sprite("torch.png", )
        torch.center_x = tile_x
        torch.center_y = tile_y
        torch.ore_type = "torch"
        self.walk_through_list.append(torch)

        # das licht sitzt genau auf der fackel. wir merken es uns am
        # sprite, damit wir es beim abbauen wieder ausmachen koennen
        torch.light = Light(tile_x, tile_y, TORCH_LIGHT_SIZE, TORCH_LIGHT_COLOR, "soft")
        self.light_layer.add(torch.light)
        
    def stones_on_tile(self, tile_x, tile_y):
        # alle stein-drops einsammeln die auf dieser kachel liegen
        stones = []
        for drop in self.drop_list:
            if drop.item_type != "stone":
                continue
            drop_x = round(drop.center_x / TILE_SIZE) * TILE_SIZE
            drop_y = round(drop.center_y / TILE_SIZE) * TILE_SIZE
            if drop_x == tile_x and drop_y == tile_y:
                stones.append(drop)
        return stones

    def drop_item(self):
        # q gedrueckt: 1 item vor den spieler werfen
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
        if item_type == "wire_curve":
            self.place_wire_curve(tile_x, tile_y)
            return
        if item_type == "torch":
            self.place_torch(tile_x, tile_y)
            return

        drop = arcade.Sprite(f"{item_type}.png", 0.6)
        drop.center_x = tile_x + random.uniform(-DROP_JITTER, DROP_JITTER)
        drop.center_y = tile_y + random.uniform(-DROP_JITTER, DROP_JITTER)
        drop.item_type = item_type
        self.drop_list.append(drop)

        # liegen jetzt genug steine auf der kachel? dann wird ein block draus
        if item_type == "stone":
            stones = self.stones_on_tile(tile_x, tile_y)
            if len(stones) >= STONES_TO_BLOCK:
                for stone in stones:
                    stone.remove_from_sprite_lists()
                self.place_crafting_block(tile_x, tile_y)

    def camera_position(self):
        # folgt dem spieler, bleibt aber am weltrand stehen
        x = max(SCREEN_WIDTH  / 2, min(self.player.center_x, WORLD_WIDTH  - SCREEN_WIDTH  / 2))
        y = max(SCREEN_HEIGHT / 2, min(self.player.center_y, WORLD_HEIGHT - SCREEN_HEIGHT / 2))
        return x, y

    def give_all_ores(self):
        for ore in ["stone", "coal", "copper", "iron", "diamond"]:
            self.inventory.add_to_hotbar(ore, 9)

    def update_mining(self, delta_time):
        if not self.mine_target:
            return

        # zu weit weggelaufen? dann abbrechen
        if arcade.get_distance_between_sprites(self.player_hitbox, self.mine_target) > MINE_RANGE:
            self.mine_target   = None
            self.mine_progress = 0.0
            return

        self.mine_progress += delta_time
        if self.mine_progress < self.mine_time():
            return

        # kisten verschuetten beim kaputtgehen ihren inhalt
        if self.mine_target.ore_type == "chest":
            self.spill_chest(self.mine_target)

        # stein ist kaputt -> was faellt raus?
        if self.mine_target.ore_type is not None:
            # crafting blocks geben sich selber zurueck
            loot = self.mine_target.ore_type
        else:
            # das werkzeug entscheidet aus welchem lostopf gezogen wird
            pool = ORE_POOLS[self.inventory.current_tool()]
            loot = random.choice(pool)

        if loot is not None:
            drop = arcade.Sprite(f"{loot}.png", 0.6)
            drop.center_x = self.mine_target.center_x + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.center_y = self.mine_target.center_y + random.uniform(-DROP_JITTER, DROP_JITTER)
            drop.item_type = loot
            self.drop_list.append(drop)

        # fackeln nehmen ihr licht mit
        if hasattr(self.mine_target, "light"):
            self.light_layer.remove(self.mine_target.light)

        self.mine_target.remove_from_sprite_lists()
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
            elif self.near_crafting_table():
                # menue geht nur auf wenn ein crafting table in der naehe steht
                self.inventory.crafting_open = True
                self.inventory.check_recipe()
                self.mine_target   = None
                self.mine_progress = 0.0
            else:
                # steht eine kiste in der naehe? dann aufmachen
                chest = self.chest_nearby()
                if chest is not None:
                    self.inventory.open_chest(chest)
                    self.mine_target   = None
                    self.mine_progress = 0.0

    def on_key_release(self, key, _modifiers):
        if key in self.keys:
            self.keys[key] = False

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.mouse_pos = (x, y)
        self.inventory.mouse_pos = (x, y)
        self.inventory.track_drag(x, y)

    def on_mouse_scroll(self, _x, _y, _scroll_x, scroll_y):
        # das % laesst die auswahl am ende wieder umspringen
        self.inventory.selected_slot = (self.inventory.selected_slot - int(scroll_y)) % HOTBAR_SLOTS

    def on_mouse_press(self, x, y, button, _modifiers):
        menu_open = self.inventory.crafting_open or self.inventory.chest is not None
        if menu_open:
            if button in (arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT):
                self.inventory.start_drag(x, y, only_one=(button == arcade.MOUSE_BUTTON_RIGHT))
            return

        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        # maus-position auf dem bildschirm in welt-position umrechnen
        cam_x, cam_y = self.camera_position()
        world_x = x + cam_x - SCREEN_WIDTH  / 2
        world_y = y + cam_y - SCREEN_HEIGHT / 2

        hits = arcade.get_sprites_at_point((world_x, world_y), self.stone_list)
        if not hits:
            # nichts festes getroffen? dann vielleicht ein wire
            hits = arcade.get_sprites_at_point((world_x, world_y), self.walk_through_list)
        if not hits:
            return

        stone = hits[0]
        if arcade.get_distance_between_sprites(self.player_hitbox, stone) <= MINE_RANGE:
            self.mine_target   = stone
            self.mine_progress = 0.0

    def on_mouse_release(self, x, y, button, _modifiers):
        if button not in (arcade.MOUSE_BUTTON_LEFT, arcade.MOUSE_BUTTON_RIGHT):
            return

        if self.inventory.crafting_open or self.inventory.chest is not None:
            self.inventory.end_drag(x, y)
            return

        self.mine_target   = None
        self.mine_progress = 0.0

    def player_texture(self):
        # sucht das passende bild zur blickrichtung aus.
        # bei diagonalem laufen gewinnt die seitenansicht
        fx, fy = self.facing
        if fx != 0:
            frames = self.player_textures[(fx, 0)]
        else:
            frames = self.player_textures[(0, fy)]
        return frames[self.walk_frame]

    def on_update(self, delta_time):
        sprinting = self.keys[arcade.key.LSHIFT] or self.keys[arcade.key.RSHIFT]
        speed = SPRINT_SPEED if sprinting else WALK_SPEED

        # True zaehlt als 1 und False als 0, D minus A gibt also -1, 0 oder 1
        dir_x = self.keys[arcade.key.D] - self.keys[arcade.key.A]
        dir_y = self.keys[arcade.key.W] - self.keys[arcade.key.S]
        if dir_x or dir_y:
            self.facing = (dir_x, dir_y)
            # beim laufen zwischen den 2 frames hin und her wechseln
            self.walk_timer += delta_time
            if self.walk_timer >= PLAYER_FRAME_TIME:
                self.walk_timer -= PLAYER_FRAME_TIME
                self.walk_frame = 1 - self.walk_frame
        else:
            # stillstehen: immer der erste frame
            self.walk_frame = 0
            self.walk_timer = 0.0
        self.player.texture = self.player_texture()

        self.player_hitbox.change_x = dir_x * speed
        self.player_hitbox.change_y = dir_y * speed
        self.physics.update()   # bewegt die hitbox und stoppt sie an steinen

        # das sichtbare bild und das licht folgen der hitbox
        self.player.center_x = self.player_hitbox.center_x
        self.player.center_y = self.player_hitbox.center_y
        self.player_light.position = self.player.position

        self.update_mining(delta_time)

        # drops einsammeln die der spieler beruehrt
        for drop in arcade.check_for_collision_with_list(self.player_hitbox, self.drop_list):
            if self.inventory.add_to_hotbar(drop.item_type, 1):
                drop.remove_from_sprite_lists()

        self.camera.position = self.camera_position()

    def on_draw(self):
        self.clear()

        self.camera.use()
        # alles in diesem with-block landet erst in der licht-schicht,
        # nicht auf dem bildschirm. beim draw danach wird es beleuchtet
        with self.light_layer:
            self.stone_list.draw()
            self.walk_through_list.draw()
            self.drop_list.draw()
            self.player_list.draw(pixelated=True)
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        # rahmen um die kachel vor dem spieler (da landet alles was man mit q droppt)
        frame = self.inventory.images["slot"]
        tx, ty = self.tile_in_front()
        arcade.draw_texture_rect(frame, arcade.XYWH(tx, ty, TILE_SIZE, TILE_SIZE))

        # rahmen um den block der gerade abgebaut wird
        if self.mine_target:
            arcade.draw_texture_rect(frame, arcade.XYWH(
                self.mine_target.center_x, self.mine_target.center_y, TILE_SIZE, TILE_SIZE))

        # fortschritts-balken ueber dem stein
        if self.mine_target:
            ratio = self.mine_progress / self.mine_time()
            bx = self.mine_target.center_x
            by = self.mine_target.center_y + 20
            arcade.draw_lrbt_rectangle_filled(bx - 16, bx - 16 + 32 * ratio, by - 3, by + 3, arcade.color.YELLOW)
            arcade.draw_lrbt_rectangle_outline(bx - 16, bx + 16, by - 3, by + 3, arcade.color.WHITE, 1)

        self.gui_camera.use()
        self.inventory.draw()


Game()
arcade.run()
#player1.png, player2.png, player3.png, player4.png, player5.png, player6.png das sind alle in zweier packs die richtungeng player1.png = nach unten, player2.png = nach unten aber ein pixel nach unten versetzt das soll jede sekunde wechseln wenn man nach unten läuft, player3.png = nach rechts, player4.png = nach rechts wieder versetzt, player5.png = nach oben, player6.png = oben wieder versetzt nach links machst du mit die richtung wechseln also umdrehen 