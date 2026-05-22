import arcade
from arcade.future.light import Light, LightLayer
import random, os, math

# ─── Einstellungen ────────────────────────────────────────────────────────
SCREEN_WIDTH,  SCREEN_HEIGHT = 1024, 768
SCREEN_TITLE   = "Frogo Roguelike"
TILE_SIZE      = 16
ROOM_WIDTH,  ROOM_HEIGHT = 12, 10

PLAYER_SPEED      = 1.5
PLAYER_MAX_HP     = 8      # mehr Leben am Anfang
DAMAGE_COOLDOWN   = 0.9
SPAWN_PROTECTION  = 1.0      # Sekunden Unverwundbarkeit nach Raum-Eintritt

SHARD_SPEED       = 7.0
SHARD_COOLDOWN    = 0.35
SHARD_LIFETIME    = 3.0      # Sekunden bis Shard despawnt
ENEMY_BASE_SPEED  = 30.0
ORBIT_RADIUS      = 30.0

CAMERA_ZOOM  = 3.5
CAMERA_LERP  = 0.14
AMBIENT_COLOR = (10, 10, 20, 255)

# Retro-Pixel-Font
PIXEL_FONT = "Courier New"

# HP-Herzen Positionen
HP_W, HP_H, HP_GAP = 18, 18, 5
HP_X, HP_Y = 20, SCREEN_HEIGHT - 30

# Farbkarten für Seltenheit
RARITY_COLORS = {
    "common": (200, 200, 200, 220),
    "uncommon": (80, 200, 80, 220),
    "rare": (80, 140, 220, 220),
    "epic": (180, 80, 200, 220),
    "legendary": (220, 190, 60, 220),
}
COIN_COSTS = {
    "common": 5,
    "uncommon": 12,
    "rare": 25,
    "epic": 55,
    "legendary": 110,
}

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────
def split_every_n_words(text: str, n: int):
    """Split text into lines with n words each."""
    words = text.split()
    lines = []
    for i in range(0, len(words), n):
        lines.append(" ".join(words[i:i+n]))
    return "\n".join(lines)

# ─── Card / Inventory System ──────────────────────────────────────────────
class Card:
    def __init__(self, id, name, desc, rarity, kind, apply_fn, bad_fn,
                 buff_text="", bad_text="", icon=None):
        self.id = id
        self.name = name
        self.desc = desc
        self.rarity = rarity        # "common","uncommon","rare","epic","legendary"
        self.kind = kind            # "shot" or "buff"
        self.apply_fn = apply_fn    # called when used (LMB/RMB)
        self.bad_fn = bad_fn        # called when bought (permanent for run)
        self.buff_text = buff_text  # short human text for buff (shown green)
        self.bad_text = bad_text    # short human text for bad (shown red)
        self.icon = icon

class Inventory:
    def __init__(self):
        self.cards = {}  # id -> count

    def add(self, card_id, n=1):
        self.cards[card_id] = self.cards.get(card_id, 0) + n

    def remove(self, card_id, n=1):
        if card_id in self.cards:
            self.cards[card_id] = max(0, self.cards[card_id] - n)
            if self.cards[card_id] == 0:
                del self.cards[card_id]

    def count(self, card_id):
        return self.cards.get(card_id, 0)

class EquipSlot:
    def __init__(self):
        self.card_id = None
        self.charges = 0

    def is_empty(self):
        return self.card_id is None

    def use_charge(self):
        if self.charges > 0:
            self.charges -= 1

# ─── Shard (Spieler-Projektil) ─────────────────────────────────────────────
class Shard(arcade.Sprite):
    def __init__(self, texture, angle_rad, speed, is_piercing,
                 lifetime=SHARD_LIFETIME):
        super().__init__(texture, scale=1.0)
        self.angle      = math.degrees(angle_rad)
        self.change_x   = math.cos(angle_rad) * speed
        self.change_y   = math.sin(angle_rad) * speed
        self.is_piercing = is_piercing
        self.lifetime   = lifetime
        self.timer      = 0.0
        self.light      = None   # wird im View zugewiesen

# ─── Raum ─────────────────────────────────────────────────────────────────
class Room:
    def __init__(self, grid_x, grid_y):
        self.grid_x, self.grid_y = grid_x, grid_y
        self.width, self.height  = ROOM_WIDTH, ROOM_HEIGHT
        self.passages  = []
        self.cleared   = False
        self.visited   = False
        self.is_boss_room = False
        self.is_escape_room = False
        self.tiles = [["floor"] * self.width for _ in range(self.height)]
        for y in range(self.height):
            self.tiles[y][0] = self.tiles[y][self.width - 1] = "wall"
        for x in range(self.width):
            self.tiles[0][x] = self.tiles[self.height - 1][x] = "wall"

    def get_pixel_pos(self):
        return self.grid_x * self.width * TILE_SIZE, self.grid_y * self.height * TILE_SIZE

    def center_world(self):
        px, py = self.get_pixel_pos()
        return px + self.width * TILE_SIZE / 2, py + self.height * TILE_SIZE / 2

    def contains(self, wx, wy):
        px, py = self.get_pixel_pos()
        return (px <= wx <= px + self.width  * TILE_SIZE and
                py <= wy <= py + self.height * TILE_SIZE)

    def create_passages(self, other):
        dx, dy = other.grid_x - self.grid_x, other.grid_y - self.grid_y
        my, mx  = self.height // 2, self.width // 2
        if   dx ==  1: self.tiles[my][self.width - 1] = "floor"; self.passages.append((self.width - 1, my))
        elif dx == -1: self.tiles[my][0]              = "floor"; self.passages.append((0, my))
        elif dy ==  1: self.tiles[self.height - 1][mx]= "floor"; self.passages.append((mx, self.height - 1))
        elif dy == -1: self.tiles[0][mx]              = "floor"; self.passages.append((mx, 0))

# ─── Gegner ────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y, body_tex, attack_tex, room, light_layer, is_boss=False):
        self.room = room
        self.body = arcade.Sprite(body_tex, scale=1.0)
        self.body.center_x = x
        self.body.center_y = y
        self.hp = 20 if not is_boss else 100
        self.max_hp = self.hp
        self.is_boss = is_boss
        self.behavior = random.choice(["chaser", "ravager", "circler"])
        self.wander_t = random.random() * 10
        self.circle_dir = random.choice([1, -1])
        self.frenzy = False
        self.speed_multiplier = 1.0

        n_orb = 6 if is_boss else 3
        self.orbiters = arcade.SpriteList()
        for _ in range(n_orb):
            self.orbiters.append(arcade.Sprite(attack_tex, scale=1.0))

        self.orbit_angle = random.uniform(0, 6.28)

        l_col = (255, 0, 0) if is_boss else (200, 60, 60)
        self.light = Light(x, y, radius=110 if is_boss else 55,
                           color=l_col, mode="soft")
        light_layer.add(self.light)

    # ── Lebensleiste über dem Kopf (in Weltkoordinaten) ──────────────────
    def draw_health_bar(self):
        w = 30 if self.is_boss else 20
        h = 4
        x = self.body.center_x
        y = self.body.top + 7

        arcade.draw_rect_filled(arcade.XYWH(x, y, w, h), (40, 0, 0, 230))
        fill_w = w * (self.hp / self.max_hp)
        if fill_w > 0:
            col = (60, 220, 60) if self.hp > self.max_hp // 2 else (220, 40, 40)
            arcade.draw_rect_filled(
                arcade.XYWH(x - w / 2 + fill_w / 2, y, fill_w, h), col)
        arcade.draw_rect_outline(arcade.XYWH(x, y, w, h), (255, 255, 255, 130), 1)

    # ── KI-Update ───────────────────────────────────────────────────────
    def update(self, delta_time, px, py):
        dx = px - self.body.center_x
        dy = py - self.body.center_y
        dist = math.hypot(dx, dy)

        # Frenzy bei halber HP
        if self.hp <= self.max_hp // 2 and not self.frenzy:
            self.frenzy = True
            self.body.color = (255, 110, 110)
            self.light.color = (255, 30, 30)

        speed = (ENEMY_BASE_SPEED * delta_time
                 * (1.7 if self.frenzy else 1.0)
                 * (1.5 if self.is_boss else 1.0)
                 * self.speed_multiplier)

        if dist > 1 and dist < 650:
            angle = math.atan2(dy, dx)

            if self.behavior == "chaser":
                self.body.center_x += math.cos(angle) * speed
                self.body.center_y += math.sin(angle) * speed

            elif self.behavior == "ravager":
                self.wander_t += delta_time * 4.0
                zigzag = math.sin(self.wander_t) * 0.55
                a = angle + zigzag
                self.body.center_x += math.cos(a) * speed
                self.body.center_y += math.sin(a) * speed

            elif self.behavior == "circler":
                perp = angle + self.circle_dir * math.pi / 2
                mx_ = math.cos(angle) * 0.3 + math.cos(perp) * 0.7
                my_ = math.sin(angle) * 0.3 + math.sin(perp) * 0.7
                length = math.hypot(mx_, my_) or 1
                self.body.center_x += (mx_ / length) * speed
                self.body.center_y += (my_ / length) * speed
                if random.random() < 0.004:
                    self.circle_dir *= -1

        # Innerhalb Raumgrenzen halten
        rx, ry = self.room.get_pixel_pos()
        m = TILE_SIZE + 2
        self.body.left   = max(self.body.left,   rx + m)
        self.body.right  = min(self.body.right,  rx + self.room.width  * TILE_SIZE - m)
        self.body.bottom = max(self.body.bottom, ry + m)
        self.body.top    = min(self.body.top,    ry + self.room.height * TILE_SIZE - m)

        # Licht + Orbiters
        self.light.position = self.body.position
        self.orbit_angle   += (8.0 if self.frenzy else 3.5) * delta_time
        r = ORBIT_RADIUS * (1.8 if self.is_boss else 1.0)
        n = len(self.orbiters)
        for i, spr in enumerate(self.orbiters):
            a = self.orbit_angle + i * (2 * math.pi / n)
            spr.center_x = self.body.center_x + math.cos(a) * r
            spr.center_y = self.body.center_y + math.sin(a) * r

# ─── Karten-Datenbank (Beispiele) ────────────────────────────────────────
def make_cards_db():
    db = {}

    # Hilfs-Defaults (werden beim Game.setup() zurückgesetzt)
    def apply_normal_shot(game):
        game.player_shot_mode = "normal"

    def bad_none(game):
        pass

    # Common: Normaler Schuss (weiß) - keine Strafe
    db["normal_shot"] = Card(
        "normal_shot", "Normal Shot",
        "Gezielter Schuss. Keine Strafe.",
        "common", "shot", apply_normal_shot, bad_none,
        buff_text="+0 dmg (standard)", bad_text="Keine")

    # Uncommon: Shotgun (grün) - -5% Bewegungsgeschwindigkeit
    def apply_shotgun(game):
        game.player_shot_mode = "shotgun"

    def bad_shotgun(game):
        game.player_speed_multiplier *= 0.95

    db["shotgun"] = Card(
        "shotgun", "Splitter Shot",
        "Feuert Shards in zufälligem Winkel fächerförmig. Kurze Reichweite.",
        "uncommon", "shot", apply_shotgun, bad_shotgun,
        buff_text="Random spread", bad_text="-5% player speed")

    # Rare: Cluster - -1 Max HP
    def apply_cluster(game):
        game.player_shot_mode = "cluster"
        game.cluster_timer = 0.0

    def bad_cluster(game):
        game.player_max_hp = max(1, game.player_max_hp - 10)  # -10 Max HP

    db["cluster"] = Card(
        "cluster", "Cluster Shot",
        "Große Kugel, explodiert nach 2s in 10 kleine Shards.",
        "rare", "shot", apply_cluster, bad_cluster,
        buff_text="Explodes into 10 shards", bad_text="-10 Max HP")

    # Epic: Shockwave - -15% attack speed (cooldown multiplier)
    def apply_shockwave(game):
        # immediate radial attack
        game.do_shockwave()

    def bad_shockwave(game):
        game.attack_speed_multiplier *= 1.15

    db["shockwave"] = Card(
        "shockwave", "Shockwave",
        "8 Projektile in alle Richtungen. 5s Cooldown.",
        "epic", "shot", apply_shockwave, bad_shockwave,
        buff_text="8-way radial", bad_text="-15% attack speed")

    # Legendary: Invincibility (buff) - -3 Max HP
    def apply_invinc(game):
        game.activate_invincibility(5.0)

    def bad_invinc(game):
        game.player_max_hp = max(1, game.player_max_hp - 3)

    db["invinc"] = Card(
        "invinc", "Invincibility",
        "5s Unverwundbarkeit (RMB). Sehr starke Strafe.",
        "legendary", "buff", apply_invinc, bad_invinc,
        buff_text="5s invincibility", bad_text="-3 Max HP")

    # Buff examples
    def apply_lifeup(game):
        game.hp = min(game.player_max_hp, game.hp + 2)
        game.player_max_hp = game.player_max_hp + 1

    def bad_lifeup(game):
        game.cooldown_multiplier *= 1.02

    db["lifeup"] = Card(
        "lifeup", "Life Up",
        "Heilt und erhöht Max HP. Kleine Strafe.",
        "common", "buff", apply_lifeup, bad_lifeup,
        buff_text="+1 Max HP, +2 heal", bad_text="+2% cooldowns")

    return db

# ─── Hauptspiel-View ───────────────────────────────────────────────────────
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        bp = os.path.dirname(os.path.abspath(__file__))
        def load(n): return arcade.load_texture(os.path.join(bp, "assets", n))

        # Texturen laden (falls nicht vorhanden, bitte Platzhalter bereitstellen)
        self.tex_floor  = load("floor.png")
        self.tex_wall   = load("wall.png")
        self.tex_p      = {"up":   load("frog_w.png"),
                           "down": load("frog_s.png"),
                           "side": load("frog_l_r.png")}
        self.tex_eye    = load("eye.png")
        self.tex_atk    = load("attack.png")
        self.tex_staff  = load("staff.png")
        self.tex_shard  = load("shard.png")

        # Sprite-Listen
        self.wall_list       = arcade.SpriteList(use_spatial_hash=True)
        self.floor_list      = arcade.SpriteList()
        self.blocker_list    = arcade.SpriteList()
        self.player_list     = arcade.SpriteList()
        self.staff_list      = arcade.SpriteList()
        self.shard_list      = arcade.SpriteList()
        self.enemy_sprites   = arcade.SpriteList()
        self.orbiter_sprites = arcade.SpriteList()

        # Kamera
        self.camera    = arcade.camera.Camera2D()
        self.camera.zoom = CAMERA_ZOOM
        self.ui_camera = arcade.camera.Camera2D()

        # Beleuchtung
        self.light_layer  = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_light = Light(0, 0, radius=130,
                                  color=(200, 150, 255), mode="soft")
        self.light_layer.add(self.player_light)

        # Spieler-Sprite
        self.player = arcade.Sprite(self.tex_p["down"], scale=1.0)
        self.player_list.append(self.player)

        # Staff-Sprite
        self.staff = arcade.Sprite(self.tex_staff, scale=1.0)
        self.staff_list.append(self.staff)

        # Spieler-Zustand
        self.player_max_hp = PLAYER_MAX_HP
        self.hp        = self.player_max_hp
        self.player_shot_mode = "normal"
        self.shot_count = 1
        self.game_over = False
        self.win       = False

        # Multiplikatoren (werden beim setup zurückgesetzt)
        self.enemy_speed_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.attack_speed_multiplier = 1.0
        self.player_speed_multiplier = 1.0

        # Steuerung
        self.mx, self.my  = 0, 0
        self.fire_mode    = 0
        self.shoot_timer  = 0.0
        self.dmg_timer    = 0.0
        self.protection_timer = 0.0
        self.shockwave_timer = 0.0

        # Bewegung (keyboard)
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        # Dungeon-Daten
        self.rooms        = []
        self.enemies      = []
        self.current_room = None

        # Card system
        self.cards_db = make_cards_db()
        self.inventory = Inventory()
        self.slot_primary = EquipSlot()   # LMB
        self.slot_secondary = EquipSlot() # RMB

        # UI state
        self.showing_shop = False
        self.shop_choices = []
        self.showing_inventory = False
        self.selected_inventory_card = None  # für "ziehen" / auswählen

        self.difficulty = 1
        self.boss_defeated = False
        self.coins = 30
        self.map_timer = 120.0
        self.timer_shop_opened = False
        self.pending_dungeon_after_shop = False

        self._generate_dungeon()
        self._build_world()

        # Startraum betreten
        start = self.rooms[0]
        self.player.position  = start.center_world()
        self.camera.position  = start.center_world()
        self.enter_room(start)
        self.open_shop()

    # ── Dungeon-Generierung ──────────────────────────────────────────────
    def _generate_dungeon(self):
        placed = {(0, 0)}
        self.rooms.append(Room(0, 0))
        for _ in range(12):
            base = random.choice(self.rooms)
            for dx, dy in random.sample([(0,1),(0,-1),(1,0),(-1,0)], 4):
                nx, ny = base.grid_x + dx, base.grid_y + dy
                if (nx, ny) not in placed:
                    nr = Room(nx, ny)
                    self.rooms.append(nr)
                    placed.add((nx, ny))
                    base.create_passages(nr)
                    nr.create_passages(base)
                    break
        self.boss_room = max(self.rooms,
                             key=lambda r: abs(r.grid_x) + abs(r.grid_y))
        self.boss_room.is_boss_room = True

        # Escape room direkt neben dem Boss
        boss_neighbors = [(self.boss_room.grid_x + dx, self.boss_room.grid_y + dy)
                          for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]
        escape_pos = next((pos for pos in boss_neighbors if pos not in placed), None)
        if escape_pos:
            escape_room = Room(escape_pos[0], escape_pos[1])
            self.rooms.append(escape_room)
            escape_room.is_escape_room = True
            self.boss_room.create_passages(escape_room)
            escape_room.create_passages(self.boss_room)

    def _build_world(self):
        for r in self.rooms:
            px, py = r.get_pixel_pos()
            for y in range(r.height):
                for x in range(r.width):
                    is_wall = r.tiles[y][x] == "wall"
                    spr = arcade.Sprite(self.tex_wall if is_wall else self.tex_floor)
                    spr.left, spr.bottom = px + x * TILE_SIZE, py + y * TILE_SIZE
                    (self.wall_list if is_wall else self.floor_list).append(spr)

    # ── Raum betreten ────────────────────────────────────────────────────
    def enter_room(self, room):
        self.protection_timer = SPAWN_PROTECTION
        self.current_room     = room

        cx, cy = room.center_world()
        self.player.position = (cx, cy)
        self.camera.position = (cx, cy)

        if not room.visited:
            room.visited = True
            if room is self.rooms[0]:
                room.cleared = True
            elif room.is_escape_room:
                # Escape room betreten = Spiel gewonnen!
                self.win = True
                return
            else:
                count = 1 if room.is_boss_room else random.randint(1, 3)
                for i in range(count):
                    angle = i * (2 * math.pi / count)
                    ex = cx + math.cos(angle) * TILE_SIZE * 3
                    ey = cy + math.sin(angle) * TILE_SIZE * 3
                    e = Enemy(ex, ey, self.tex_eye, self.tex_atk,
                              room, self.light_layer, room.is_boss_room)
                    e.hp *= self.difficulty
                    e.max_hp *= self.difficulty
                    e.speed_multiplier = 1 + (self.difficulty - 1) * 0.2
                    self.enemies.append(e)
                    self.enemy_sprites.append(e.body)
                    for o in e.orbiters:
                        self.orbiter_sprites.append(o)

        self._update_doors()

    def _new_dungeon(self):
        self.difficulty += 1
        self.boss_defeated = False
        self.timer_shop_opened = False
        self.pending_dungeon_after_shop = False
        self.map_timer = 120.0

        # Dungeon neu generieren
        self.rooms = []
        self.enemies = []
        self.current_room = None

        # Sprite-Lists leeren und neu
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.floor_list = arcade.SpriteList()
        self.blocker_list = arcade.SpriteList()
        self.enemy_sprites = arcade.SpriteList()
        self.orbiter_sprites = arcade.SpriteList()

        self._generate_dungeon()
        self._build_world()

        # Startraum betreten
        start = self.rooms[0]
        self.player.position = start.center_world()
        self.camera.position = start.center_world()
        self.enter_room(start)

    def _update_doors(self):
        for s in self.blocker_list:
            self.wall_list.remove(s)
        self.blocker_list = arcade.SpriteList()

        if not self.current_room or self.current_room.cleared:
            return
        rx, ry = self.current_room.get_pixel_pos()
        for tx, ty in self.current_room.passages:
            b = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE,
                                        color=(120, 10, 10, 255))
            b.left, b.bottom = rx + tx * TILE_SIZE, ry + ty * TILE_SIZE
            self.blocker_list.append(b)
            self.wall_list.append(b)

    # ── HUD ─────────────────────────────────────────────────────────────
    def draw_hud(self):
        # HP-Herzen
        for i in range(self.player_max_hp):
            x = HP_X + i * (HP_W + HP_GAP) + HP_W / 2
            col = (200, 30, 30, 255) if i < self.hp else (50, 50, 50, 180)
            arcade.draw_rect_filled(arcade.XYWH(x, HP_Y, HP_W, HP_H), col)
            arcade.draw_rect_outline(arcade.XYWH(x, HP_Y, HP_W, HP_H),
                                     (255, 255, 255, 110), 1)

        arcade.draw_text(f"HP  {self.hp}/{self.player_max_hp}",
                         HP_X, HP_Y - HP_H,
                         arcade.color.LIGHT_GRAY, 11, font_name=PIXEL_FONT)

        mode = "[ PIERCE ]" if self.fire_mode == 2 else "[ NORMAL ]"
        arcade.draw_text(mode, SCREEN_WIDTH - 130, 20,
                         arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)

        arcade.draw_text(f"Coins: {self.coins}", HP_X, HP_Y - 26,
                         arcade.color.GOLD, 12, font_name=PIXEL_FONT)
        minutes = int(self.map_timer) // 60
        seconds = int(self.map_timer) % 60
        arcade.draw_text(f"Time: {minutes:02d}:{seconds:02d}", HP_X, HP_Y - 42,
                         arcade.color.SKY_BLUE, 12, font_name=PIXEL_FONT)
        arcade.draw_text("Q = -30s", HP_X, HP_Y - 58,
                         arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)

        # Minimap
        mm_cx, mm_cy = SCREEN_WIDTH - 90, SCREEN_HEIGHT - 90
        arcade.draw_rect_filled(arcade.XYWH(mm_cx, mm_cy, 140, 140),
                                (0, 0, 0, 160))
        for r in self.rooms:
            if not r.visited:
                continue
            col = (100, 200, 255) if r is self.current_room else \
                  (255, 255,   0) if r.is_escape_room      else \
                  (255, 215,   0) if r.is_boss_room        else \
                  (120, 220, 120) if r.cleared             else (220, 80,  80)
            rx = mm_cx + r.grid_x * 14
            ry = mm_cy + r.grid_y * 14
            arcade.draw_rect_filled(arcade.XYWH(rx, ry, 11, 11), col)
        arcade.draw_rect_outline(arcade.XYWH(mm_cx, mm_cy, 140, 140),
                                 (255, 255, 255, 80), 1)

        # Equip Slots (rechts unten) - persistent HUD
        sx = SCREEN_WIDTH - 180
        sy = 60
        # Primary (LMB)
        arcade.draw_rect_outline(arcade.XYWH(sx, sy, 64, 64), (255,255,255,120), 2)
        if self.slot_primary.card_id:
            c = self.cards_db[self.slot_primary.card_id]
            arcade.draw_text(c.name, sx + 70, sy + 40, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)
            arcade.draw_text(f"Charges: {self.slot_primary.charges}", sx + 70, sy + 20, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
        else:
            arcade.draw_text("LMB: -", sx + 70, sy + 30, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)

        # Secondary (RMB)
        arcade.draw_rect_outline(arcade.XYWH(sx + 80, sy, 64, 64), (255,255,255,120), 2)
        if self.slot_secondary.card_id:
            c = self.cards_db[self.slot_secondary.card_id]
            arcade.draw_text(c.name, sx + 150, sy + 40, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)
            arcade.draw_text(f"Charges: {self.slot_secondary.charges}", sx + 150, sy + 20, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
        else:
            arcade.draw_text("RMB: -", sx + 150, sy + 30, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)

    # ── Shop / Inventory UI ───────────────────────────────────────────────
    def open_shop(self):
        # Wähle Karten nach Gewichtung, basierend auf vorhandenen Coins
        if self.coins <= 10:
            rarities = {"common":80, "uncommon":15, "rare":4, "epic":1, "legendary":0}
        elif self.coins <= 20:
            rarities = {"common":60, "uncommon":25, "rare":10, "epic":4, "legendary":1}
        elif self.coins <= 40:
            rarities = {"common":40, "uncommon":30, "rare":15, "epic":10, "legendary":5}
        else:
            rarities = {"common":30, "uncommon":30, "rare":20, "epic":12, "legendary":8}

        pool = []
        for c in self.cards_db.values():
            weight = rarities.get(c.rarity, 10)
            pool.extend([c.id] * weight)
        self.shop_choices = random.sample(pool, 3)
        self.showing_shop = True
        self.showing_inventory = False
        self.selected_inventory_card = None

    def buy_card(self, card_id):
        card = self.cards_db[card_id]
        cost = COIN_COSTS.get(card.rarity, 10)
        if self.coins < cost:
            return
        self.coins -= cost
        # wende Strafe an (permanent für Run)
        card.bad_fn(self)
        # füge Karte dem Inventar hinzu
        self.inventory.add(card_id, 1)
        self.showing_shop = False
        # öffne Inventar direkt nach Kauf
        self.showing_inventory = True
        self.selected_inventory_card = None

    def grant_timer_reward(self):
        pool = []
        for c in self.cards_db.values():
            if c.id == "normal_shot":
                continue
            weight = {"common":60, "uncommon":25, "rare":10, "epic":4, "legendary":1}[c.rarity]
            pool.extend([c.id] * weight)
        card_id = random.choice(pool)
        card = self.cards_db[card_id]
        self.inventory.add(card_id, 1)
        card.bad_fn(self)
        self.map_timer = 120.0

    def open_inventory(self):
        self.showing_inventory = True
        self.showing_shop = False
        self.selected_inventory_card = None

    def equip_card_from_inventory(self, card_id, slot):
        """
        Wenn der Spieler eine Karte in einen Slot legt, reservieren wir die Karten
        aus dem Inventar: die Anzahl gleicher Karten im Inventar wird als Charges
        in den Slot übernommen und gleichzeitig aus dem Inventar entfernt.
        Dadurch kann die Karte nicht mehrfach "rekursiv" aus dem Inventar
        gezogen werden und es entsteht kein unendliches Schießen.
        """
        card = self.cards_db[card_id]
        if card.kind == "buff" and slot == "primary":
            return  # Buffs nur in secondary slot

        cnt = self.inventory.count(card_id)
        if cnt <= 0:
            return

        # Reserve alle vorhandenen gleichen Karten als Charges
        charges = cnt

        # Entferne diese Karten aus dem Inventar (sie sind jetzt im Slot)
        self.inventory.remove(card_id, charges)

        if slot == "primary":
            # Wenn bereits etwas im Slot ist, gib dessen verbleibende Charges zurück
            if self.slot_primary.card_id:
                self.inventory.add(self.slot_primary.card_id, self.slot_primary.charges)
            self.slot_primary.card_id = card_id
            self.slot_primary.charges = charges
        else:
            if self.slot_secondary.card_id:
                self.inventory.add(self.slot_secondary.card_id, self.slot_secondary.charges)
            self.slot_secondary.card_id = card_id
            self.slot_secondary.charges = charges

    def unequip_slot(self, slot_name):
        """Gibt verbleibende Charges zurück ins Inventar und leert den Slot."""
        if slot_name == "primary":
            slot = self.slot_primary
        else:
            slot = self.slot_secondary

        if slot.card_id:
            if slot.charges > 0:
                self.inventory.add(slot.card_id, slot.charges)
            slot.card_id = None
            slot.charges = 0

    # ── Utility Actions (Effekte) ────────────────────────────────────────
    def do_shockwave(self):
        # 8 Projektile in alle Richtungen, mehr bei stacking
        num = 8 + (self.slot_primary.charges - 1) * 4
        cx, cy = self.player.position
        for i in range(num):
            a = i * (2 * math.pi / num)
            s = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.5)
            s.position = (cx, cy)
            sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
            self.light_layer.add(sl)
            s.light = sl
            self.shard_list.append(s)

    def activate_invincibility(self, duration):
        # einfache Implementierung: setze protection_timer temporär hoch
        self.protection_timer = max(self.protection_timer, duration)

    # ── Zeichnen ─────────────────────────────────────────────────────────
    def on_draw(self):
        self.clear()
        self.camera.use()
        with self.light_layer:
            self.floor_list.draw(pixelated=True)
            self.wall_list.draw(pixelated=True)
            self.blocker_list.draw(pixelated=True)
            self.shard_list.draw(pixelated=True)
            self.orbiter_sprites.draw(pixelated=True)
            self.enemy_sprites.draw(pixelated=True)

            blink_on = int(self.protection_timer / 0.15) % 2 == 0
            self.player.alpha = 60 if (self.protection_timer > 0 and blink_on) else 255
            self.player_list.draw(pixelated=True)
            self.staff_list.draw(pixelated=True)

        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        self.camera.use()
        for e in self.enemies:
            if e.room is self.current_room:
                e.draw_health_bar()

        self.ui_camera.use()
        if self.game_over:
            self.draw_pixel_screen(
                "GAME  OVER",
                "[  R  ]   Nochmal versuchen",
                (220, 40, 40, 255))
        elif self.win:
            # Escape room betreten = echter Win!
            self.draw_pixel_screen(
                "VICTORY !",
                "Du hast den Dungeon verlassen!",
                (255, 215, 0, 255))
        else:
            if self.showing_shop:
                self.draw_shop_ui()
            elif self.showing_inventory:
                self.draw_inventory_ui()
            else:
                self.draw_hud()

    def draw_shop_ui(self):
        # Dunkles Overlay
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            SCREEN_WIDTH, SCREEN_HEIGHT),
                                (0, 0, 0, 200))
        arcade.draw_text("SHOP - Wähle eine Karte", SCREEN_WIDTH/2, SCREEN_HEIGHT - 80,
                         arcade.color.LIGHT_GRAY, 28, font_name=PIXEL_FONT, anchor_x="center")

        # Erklärungstext in Box (aufgeteilt: jede 3 Wörter in neue Zeile)
        expl = "Wähle eine Karte: Upgrade gegen Handicap. Die Karte gibt dir einen Bonus; der rote Text zeigt die permanente Strafe."
        expl_lines = split_every_n_words(expl, 3)
        expl_box_x = SCREEN_WIDTH/2
        expl_box_y = SCREEN_HEIGHT - 140
        arcade.draw_rect_filled(arcade.XYWH(expl_box_x, expl_box_y, 820, 80), (20,20,30,220))
        arcade.draw_rect_outline(arcade.XYWH(expl_box_x, expl_box_y, 820, 80), (180,180,180,160), 2)
        arcade.draw_text(expl_lines, expl_box_x - 390, expl_box_y + 10,
                         arcade.color.LIGHT_GRAY, 14, font_name=PIXEL_FONT)

        # Drei Karten anzeigen
        start_x = SCREEN_WIDTH/2 - 300
        y = SCREEN_HEIGHT/2
        for i, cid in enumerate(self.shop_choices):
            x = start_x + i * 300
            card = self.cards_db[cid]
            # Karte Hintergrund
            arcade.draw_rect_filled(arcade.XYWH(x, y, 260, 360), (20,20,30,230))
            # Randfarbe nach Seltenheit
            border_col = RARITY_COLORS.get(card.rarity, (200,200,200,220))
            arcade.draw_rect_outline(arcade.XYWH(x, y, 260, 360), border_col, 4)
            # Name + Beschreibung (Beschreibung splitten für Lesbarkeit)
            desc_lines = split_every_n_words(card.desc, 6)
            arcade.draw_text(card.name, x - 100, y + 140, arcade.color.WHITE, 14, font_name=PIXEL_FONT)
            arcade.draw_text(desc_lines, x - 100, y + 100, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
            price = COIN_COSTS.get(card.rarity, 10)
            arcade.draw_text(f"Rarity: {card.rarity}", x - 100, y + 70, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
            arcade.draw_text(f"Price: {price} coins", x - 100, y + 55, arcade.color.GOLD, 10, font_name=PIXEL_FONT)
            # Buff (grün) und Bad (rot) getrennt in Box
            arcade.draw_text("Buff:", x - 100, y + 30, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
            arcade.draw_text(card.buff_text, x - 60, y + 30, arcade.color.GREEN, 10, font_name=PIXEL_FONT)
            arcade.draw_text("Bad:", x + 20, y + 30, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
            arcade.draw_text(card.bad_text, x + 60, y + 30, arcade.color.RED, 10, font_name=PIXEL_FONT)
            # Zeige konkrete Zahlen: buff_text / bad_text enthalten bereits Zahlen
            arcade.draw_text("Klicken zum Kaufen", x - 100, y - 140, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)

    def draw_inventory_ui(self):
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            SCREEN_WIDTH, SCREEN_HEIGHT),
                                (0, 0, 0, 200))
        arcade.draw_text("INVENTAR - Linksklick = auswählen, dann unten in Slot klicken",
                         SCREEN_WIDTH/2, SCREEN_HEIGHT - 80,
                         arcade.color.LIGHT_GRAY, 16, font_name=PIXEL_FONT, anchor_x="center")
        # Liste der Karten
        start_x = 120
        start_y = SCREEN_HEIGHT - 160
        i = 0
        for cid, count in self.inventory.cards.items():
            card = self.cards_db[cid]
            x = start_x + (i % 6) * 160
            y = start_y - (i // 6) * 120
            # Hintergrundfarbe je nach Art: Buff = gelb, Attack = rot-ish
            if card.kind == "buff":
                bg = (180, 160, 60, 220)  # gelb
            else:
                bg = (140, 40, 40, 220)   # rot
            arcade.draw_rect_filled(arcade.XYWH(x, y, 140, 100), bg)
            arcade.draw_rect_outline(arcade.XYWH(x, y, 140, 100), (255,255,255,80), 1)
            arcade.draw_text(card.name, x - 60, y + 20, arcade.color.WHITE, 12, font_name=PIXEL_FONT)
            arcade.draw_text(f"x{count}", x + 40, y - 30, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)
            desc_lines = split_every_n_words(card.desc, 6)
            arcade.draw_text(desc_lines, x - 60, y - 5, arcade.color.LIGHT_GRAY, 9, font_name=PIXEL_FONT)
            # Markiere ausgewählte Karte
            if self.selected_inventory_card == cid:
                arcade.draw_rect_outline(arcade.XYWH(x, y, 140, 100), (255, 255, 0, 255), 3)
            i += 1

        # Unten: zwei Boxen zum "reinziehen" (klicken) - Primary / Secondary
        box_w, box_h = 160, 120
        bx = SCREEN_WIDTH/2 - 200
        by = 80
        # Primary box (links) - Attacken bevorzugt (visual hint)
        arcade.draw_rect_filled(arcade.XYWH(bx, by, box_w, box_h), (30,30,40,220))
        arcade.draw_rect_outline(arcade.XYWH(bx, by, box_w, box_h), (255,255,255,120), 2)
        arcade.draw_text("Primary (LMB)", bx - 60, by + 40, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)
        if self.slot_primary.card_id:
            c = self.cards_db[self.slot_primary.card_id]
            arcade.draw_text(c.name, bx - 60, by + 10, arcade.color.WHITE, 12, font_name=PIXEL_FONT)
            arcade.draw_text(f"Charges: {self.slot_primary.charges}", bx - 60, by - 20, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
        else:
            arcade.draw_text("-", bx, by, arcade.color.LIGHT_GRAY, 20, font_name=PIXEL_FONT, anchor_x="center", anchor_y="center")

        # Secondary box (rechts) - Buffs preferred visual hint
        bx2 = SCREEN_WIDTH/2 + 200
        arcade.draw_rect_filled(arcade.XYWH(bx2, by, box_w, box_h), (30,30,40,220))
        arcade.draw_rect_outline(arcade.XYWH(bx2, by, box_w, box_h), (255,255,255,120), 2)
        arcade.draw_text("Secondary (RMB)", bx2 - 60, by + 40, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT)
        if self.slot_secondary.card_id:
            c = self.cards_db[self.slot_secondary.card_id]
            arcade.draw_text(c.name, bx2 - 60, by + 10, arcade.color.WHITE, 12, font_name=PIXEL_FONT)
            arcade.draw_text(f"Charges: {self.slot_secondary.charges}", bx2 - 60, by - 20, arcade.color.LIGHT_GRAY, 10, font_name=PIXEL_FONT)
        else:
            arcade.draw_text("-", bx2, by, arcade.color.LIGHT_GRAY, 20, font_name=PIXEL_FONT, anchor_x="center", anchor_y="center")

        arcade.draw_text("Klicke auf einen Slot, um ihn zu leeren (Charges zurück ins Inventar).", SCREEN_WIDTH/2, 40, arcade.color.LIGHT_GRAY, 12, font_name=PIXEL_FONT, anchor_x="center")

    # ── Spiellogik ───────────────────────────────────────────────────────
    def on_update(self, delta_time):
        if self.game_over:
            return

        # Shop pausiert das Spiel vollständig; Inventory lässt Bewegung zu
        if self.showing_shop:
            return

        # Bewegungseingaben verarbeiten (auch wenn Inventory offen)
        move_x = 0
        move_y = 0
        if self.move_left:
            move_x -= PLAYER_SPEED * self.player_speed_multiplier
        if self.move_right:
            move_x += PLAYER_SPEED * self.player_speed_multiplier
        if self.move_up:
            move_y += PLAYER_SPEED * self.player_speed_multiplier
        if self.move_down:
            move_y -= PLAYER_SPEED * self.player_speed_multiplier

        # Kamera Lerp zur Spielerposition (sanft)
        cam_x = self.camera.position[0]
        cam_y = self.camera.position[1]
        target_x = self.player.center_x
        target_y = self.player.center_y
        self.camera.position = (cam_x + (target_x - cam_x) * CAMERA_LERP,
                                cam_y + (target_y - cam_y) * CAMERA_LERP)

        # Update Timers (Cooldowns beeinflusst durch multiplikatoren)
        self.shoot_timer      = max(0.0, self.shoot_timer      - delta_time * self.cooldown_multiplier)
        self.dmg_timer        = max(0.0, self.dmg_timer        - delta_time)
        self.protection_timer = max(0.0, self.protection_timer - delta_time)
        self.shockwave_timer  = max(0.0, self.shockwave_timer  - delta_time)

        # Spieler Bewegung (X und Y getrennt → Wandgleiten)
        old_x, old_y = self.player.center_x, self.player.center_y

        self.player.center_x += move_x
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x = old_x

        self.player.center_y += move_y
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_y = old_y

        # Staff dreht sich zur Maus
        wm = self.camera.unproject((self.mx, self.my))
        dx  = wm[0] - self.player.center_x
        dy  = wm[1] - self.player.center_y
        rad = math.atan2(dy, dx)
        self.staff.center_x = self.player.center_x + math.cos(rad) * 12
        self.staff.center_y = self.player.center_y + math.sin(rad) * 12
        self.staff.angle    = 90 - math.degrees(rad)

        # Shards bewegen + Kollision
        dead_shards  = set()
        dead_enemies = set()

        for s in list(self.shard_list):
            s.timer += delta_time
            if s.timer >= s.lifetime:
                # cluster behavior: spawn shards when cluster expires
                if getattr(s, "is_cluster", False):
                    # spawn many small shards
                    num_small = 10 + (self.slot_primary.charges - 1) * 5  # stärker bei stacking
                    for i in range(num_small):
                        a = random.uniform(0, 2 * math.pi)
                        ss = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.2)
                        ss.position = s.position
                        sl = Light(ss.center_x, ss.center_y, 20, (180, 200, 255), "soft")
                        self.light_layer.add(sl)
                        ss.light = sl
                        self.shard_list.append(ss)
                dead_shards.add(s)
                continue

            s.center_x += s.change_x
            s.center_y += s.change_y
            if s.light:
                s.light.position = s.position

            # Wand-Kollision
            if arcade.check_for_collision_with_list(s, self.wall_list):
                dead_shards.add(s)
                continue

            # Gegner-Treffer
            for e in self.enemies:
                if id(e) in dead_enemies:
                    continue
                if e.room is self.current_room and arcade.check_for_collision(s, e.body):
                    e.hp -= 1
                    if not s.is_piercing:
                        dead_shards.add(s)
                    if e.hp <= 0:
                        dead_enemies.add(id(e))
                    break

        # Tote Shards entfernen
        for s in dead_shards:
            if s.light and s.light in self.light_layer:
                self.light_layer.remove(s.light)
            s.remove_from_sprite_lists()

        # Tote Gegner entfernen
        actually_dead = [e for e in self.enemies if id(e) in dead_enemies]
        for e in actually_dead:
            if e.light in self.light_layer:
                self.light_layer.remove(e.light)
            e.body.remove_from_sprite_lists()
            for o in e.orbiters:
                o.remove_from_sprite_lists()
            self.enemies.remove(e)

        # Gegner-Kill belohnt mit Coins
        if actually_dead:
            self.coins += 5 * len(actually_dead)

        # Timer weiterlaufen lassen, nur wenn Spiel läuft
        self.map_timer = max(0.0, self.map_timer - delta_time)
        if (self.map_timer <= 0 and not self.showing_shop and not self.showing_inventory
                and not self.win and not self.game_over and not self.timer_shop_opened):
            self.open_shop()
            self.timer_shop_opened = True
            self.pending_dungeon_after_shop = True

        if self.pending_dungeon_after_shop and not self.showing_shop and not self.showing_inventory:
            self._new_dungeon()

        # Gegner KI-Update
        for e in self.enemies:
            e.update(delta_time, self.player.center_x, self.player.center_y)

        # Spieler nimmt Schaden
        if self.dmg_timer <= 0 and self.protection_timer <= 0:
            for e in self.enemies:
                if e.room is not self.current_room:
                    continue
                hit = (arcade.check_for_collision(self.player, e.body) or
                       arcade.check_for_collision_with_list(self.player, e.orbiters))
                if hit:
                    self.hp       -= 1
                    self.dmg_timer = DAMAGE_COOLDOWN
                    if self.hp <= 0:
                        self.game_over = True
                    break

        # Raum auto-clearen wenn keine Gegner mehr
        if self.current_room and not self.current_room.cleared:
            if not any(e.room is self.current_room for e in self.enemies):
                self.current_room.cleared = True
                self._update_doors()
                # Öffne Shop nach Raum-Clear (oder nur bei Boss, je nach Wunsch)
                self.open_shop()
                if self.current_room is self.boss_room:
                    self.win = True

        # Raum-Wechsel erkennen
        for r in self.rooms:
            if r is not self.current_room and r.contains(
                    self.player.center_x, self.player.center_y):
                self.enter_room(r)
                break

        # Lichter nachführen
        self.player_light.position = self.player.position

    # ── Eingaben ─────────────────────────────────────────────────────────
    def on_mouse_motion(self, x, y, dx, dy):
        self.mx, self.my = x, y

    def on_mouse_press(self, x, y, button, modifiers):
        # Wenn Shop offen: Klick auf eine Karte kauft sie
        if self.showing_shop:
            # einfache Hit-Detection: Karte i hat Bereich
            start_x = SCREEN_WIDTH/2 - 300
            y_center = SCREEN_HEIGHT/2
            for i, cid in enumerate(self.shop_choices):
                cx = start_x + i * 300
                left = cx - 130
                right = cx + 130
                top = y_center + 180
                bottom = y_center - 180
                if left <= x <= right and bottom <= y <= top:
                    self.buy_card(cid)
                    return
            # Klick außerhalb schließt Shop nicht automatisch
            return

        if self.showing_inventory:
            # Klick auf Inventar-Karte: wähle Karte aus
            start_x = 120
            start_y = SCREEN_HEIGHT - 160
            i = 0
            for cid, count in list(self.inventory.cards.items()):
                x_cell = start_x + (i % 6) * 160
                y_cell = start_y - (i // 6) * 120
                left = x_cell - 70
                right = x_cell + 70
                top = y_cell + 50
                bottom = y_cell - 50
                if left <= x <= right and bottom <= y <= top:
                    # Auswahl toggeln
                    if self.selected_inventory_card == cid:
                        self.selected_inventory_card = None
                    else:
                        self.selected_inventory_card = cid
                    return
                i += 1

            # Klick auf Equip-Boxen unten: wenn eine Karte ausgewählt ist, equippe sie
            box_w, box_h = 160, 120
            bx = SCREEN_WIDTH/2 - 200
            by = 80
            bx2 = SCREEN_WIDTH/2 + 200
            # Primary box (links)
            if bx - box_w/2 <= x <= bx + box_w/2 and by - box_h/2 <= y <= by + box_h/2:
                # Wenn Klick direkt auf Slot (ohne Auswahl) -> unequip
                if not self.selected_inventory_card:
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.unequip_slot("primary")
                    return
                if self.selected_inventory_card:
                    # Linksklick = primary
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.equip_card_from_inventory(self.selected_inventory_card, "primary")
                        self.selected_inventory_card = None
                    # Rechtsklick = secondary
                    elif button == arcade.MOUSE_BUTTON_RIGHT:
                        self.equip_card_from_inventory(self.selected_inventory_card, "secondary")
                        self.selected_inventory_card = None
                return
            # Secondary box (rechts)
            if bx2 - box_w/2 <= x <= bx2 + box_w/2 and by - box_h/2 <= y <= by + box_h/2:
                if not self.selected_inventory_card:
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.unequip_slot("secondary")
                    return
                if self.selected_inventory_card:
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.equip_card_from_inventory(self.selected_inventory_card, "primary")
                        self.selected_inventory_card = None
                    elif button == arcade.MOUSE_BUTTON_RIGHT:
                        self.equip_card_from_inventory(self.selected_inventory_card, "secondary")
                        self.selected_inventory_card = None
                return

            return

        # Wenn normales Spiel: LMB = feuern / benutzen primary, RMB = benutzen secondary
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.use_primary()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.use_secondary()

    def use_primary(self):
        # Respect a short cooldown so player can't spam faster than SHARD_COOLDOWN
        if self.shoot_timer > 0:
            return

        # If there's a shot-card equipped, use it (unlimited ammo).
        if self.slot_primary.card_id:
            cid = self.slot_primary.card_id
            card = self.cards_db[cid]
            if card.kind == "shot":
                rad = math.atan2(self.camera.unproject((self.mx, self.my))[1] - self.player.center_y,
                                 self.camera.unproject((self.mx, self.my))[0] - self.player.center_x)
                if cid == "normal_shot":
                    s = Shard(self.tex_shard, rad, SHARD_SPEED, is_piercing=False)
                    s.position = self.staff.position
                    sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
                    self.light_layer.add(sl)
                    s.light = sl
                    self.shard_list.append(s)
                elif cid == "shotgun":
                    num_shards = 5 + (self.slot_primary.charges - 1) * 2
                    for i in range(num_shards):
                        spread = random.uniform(-0.5, 0.5)
                        a = rad + spread
                        s = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.5)
                        s.position = self.staff.position
                        sl = Light(s.center_x, s.center_y, 25, (200, 180, 255), "soft")
                        self.light_layer.add(sl)
                        s.light = sl
                        self.shard_list.append(s)
                elif cid == "cluster":
                    num_clusters = 1 + (self.slot_primary.charges - 1) // 2  # mehr bei stacking
                    for _ in range(num_clusters):
                        big = Shard(self.tex_shard, rad, SHARD_SPEED * 0.3, is_piercing=True, lifetime=2.0)
                        big.position = self.staff.position
                        big.is_cluster = True
                        big.cluster_timer = 0.0
                        sl = Light(big.center_x, big.center_y, 40, (180, 200, 255), "soft")
                        self.light_layer.add(sl)
                        big.light = sl
                        self.shard_list.append(big)
                elif cid == "shockwave":
                    if self.shockwave_timer <= 0:
                        self.do_shockwave()
                        self.shockwave_timer = 5.0
                # setze shoot cooldown
                self.shoot_timer = SHARD_COOLDOWN
                return

        # Fallback: kein Shot-Card oder keine Charges mehr -> normaler Schuss (unbegrenzt)
        rad = math.atan2(self.camera.unproject((self.mx, self.my))[1] - self.player.center_y,
                         self.camera.unproject((self.mx, self.my))[0] - self.player.center_x)
        s = Shard(self.tex_shard, rad, SHARD_SPEED, is_piercing=False)
        s.position = self.staff.position
        sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
        self.light_layer.add(sl)
        s.light = sl
        self.shard_list.append(s)
        self.shoot_timer = SHARD_COOLDOWN

    def use_secondary(self):
        if self.slot_secondary.card_id and self.slot_secondary.charges > 0:
            cid = self.slot_secondary.card_id
            card = self.cards_db[cid]
            if card.kind != "buff":
                return
            # Buffs: rufe apply_fn direkt
            card.apply_fn(self)
            self.slot_secondary.use_charge()

    def on_key_press(self, symbol, modifiers):
        # ESC schließt Shop/Inventory
        if symbol == arcade.key.ESCAPE:
            if self.showing_shop:
                self.showing_shop = False
            elif self.showing_inventory:
                self.showing_inventory = False
                self.selected_inventory_card = None
            return

        # R zum Neustarten bei Game Over
        if symbol == arcade.key.R:
            if self.game_over:
                self.setup()
            return

        # Q verkürzt den Timer um 30 Sekunden
        if symbol == arcade.key.Q:
            if not self.game_over and not self.win:
                self.map_timer = max(0.0, self.map_timer - 30.0)
            return

        # N öffnet / schließt den Shop (Toggle)
        if symbol == arcade.key.N:
            # Wenn Inventory offen, schließe es und öffne Shop
            if self.showing_inventory:
                self.open_shop()
                return
            # Toggle shop visibility
            if self.showing_shop:
                self.showing_shop = False
            else:
                # Öffne Shop nur, wenn Spiel nicht pausiert durch Game Over
                if not self.game_over:
                    self.open_shop()
            return

        # Bewegungstasten
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.move_left = True
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.move_right = True
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.move_up = True
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.move_down = True

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.move_left = False
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.move_right = False
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.move_up = False
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.move_down = False

    # ── Pixel-Screen (Game Over / Victory) ───────────────────────────────
    def draw_pixel_screen(self, title, sub, title_col):
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 185))
        arcade.draw_rect_outline(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        640, 220),
            title_col, 4)
        for ox, oy in [(4, -4), (2, -2)]:
            arcade.draw_text(
                title,
                SCREEN_WIDTH / 2 + ox, SCREEN_HEIGHT / 2 + 55 + oy,
                (0, 0, 0, 210), 54,
                font_name=PIXEL_FONT, bold=True,
                anchor_x="center", anchor_y="center")
        arcade.draw_text(
            title,
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 55,
            title_col, 54,
            font_name=PIXEL_FONT, bold=True,
            anchor_x="center", anchor_y="center")
        arcade.draw_text(
            sub,
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30,
            arcade.color.LIGHT_GRAY, 16,
            font_name=PIXEL_FONT,
            anchor_x="center", anchor_y="center")

# ─── Spiel starten ───────────────────────────────────────────────────────
if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()
