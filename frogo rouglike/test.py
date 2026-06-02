import arcade
import os
import math

SPEED  = 3.0
ROOM_W = 800
ROOM_H = 600
MARGIN = 32
SCALE  = 2.0

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(ROOM_W, ROOM_H, "Test")
        self.set_mouse_visible(False)
        arcade.set_background_color((15, 30, 15))

        bp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        # Texturen
        self.tex_down  = arcade.load_texture(os.path.join(bp, "frog_s.png"))
        self.tex_up    = arcade.load_texture(os.path.join(bp, "frog_w.png"))
        self.tex_right = arcade.load_texture(os.path.join(bp, "frog_l_r.png"))
        self.tex_left  = self.tex_right.flip_left_right()

        self.player = arcade.Sprite(self.tex_down, scale=SCALE)
        self.player.center_x = ROOM_W / 2
        self.player.center_y = ROOM_H / 2

        # Bewegung
        self.move_left  = False
        self.move_right = False
        self.move_up    = False
        self.move_down  = False

        # Maus
        self.maus_sprite = arcade.Sprite(os.path.join(bp, "maus.png"), scale=1.0)
        self.maus_x = ROOM_W / 2
        self.maus_y = ROOM_H / 2

        # Türen
        self.türen = arcade.SpriteList()
        farbe = arcade.color.DARK_BROWN
        self.türen.append(arcade.SpriteSolidColor(100, 18, 400, ROOM_H - 9, farbe))  # oben
        self.türen.append(arcade.SpriteSolidColor(100, 18, 400,           9, farbe))  # unten
        self.türen.append(arcade.SpriteSolidColor(18, 100,           9, 300, farbe))  # links
        self.türen.append(arcade.SpriteSolidColor(18, 100, ROOM_W - 9, 300, farbe))  # rechts

        # Wände (grau, 24 px breit, Lücken an den Türen)
        WAND = 24
        wand_farbe = (120, 120, 120)
        self.wände = arcade.SpriteList()
        # Tür-Mittelpunkte und halbe Öffnungsbreiten
        tür_x, tür_hw = 400, 50   # horizontale Türen: Mitte x=400, Öffnung ±50
        tür_y, tür_hh = 300, 50   # vertikale  Türen: Mitte y=300, Öffnung ±50

        # Oben: links und rechts der Tür
        self.wände.append(arcade.SpriteSolidColor(tür_x - tür_hw, WAND,
                                                   (tür_x - tür_hw) // 2, ROOM_H - WAND // 2, wand_farbe))
        self.wände.append(arcade.SpriteSolidColor(ROOM_W - (tür_x + tür_hw), WAND,
                                                   (tür_x + tür_hw + ROOM_W) // 2, ROOM_H - WAND // 2, wand_farbe))
        # Unten: links und rechts der Tür
        self.wände.append(arcade.SpriteSolidColor(tür_x - tür_hw, WAND,
                                                   (tür_x - tür_hw) // 2, WAND // 2, wand_farbe))
        self.wände.append(arcade.SpriteSolidColor(ROOM_W - (tür_x + tür_hw), WAND,
                                                   (tür_x + tür_hw + ROOM_W) // 2, WAND // 2, wand_farbe))
        # Links: unterhalb und oberhalb der Tür
        self.wände.append(arcade.SpriteSolidColor(WAND, tür_y - tür_hh,
                                                   WAND // 2, (tür_y - tür_hh) // 2, wand_farbe))
        self.wände.append(arcade.SpriteSolidColor(WAND, ROOM_H - (tür_y + tür_hh),
                                                   WAND // 2, (tür_y + tür_hh + ROOM_H) // 2, wand_farbe))
        # Rechts: unterhalb und oberhalb der Tür
        self.wände.append(arcade.SpriteSolidColor(WAND, tür_y - tür_hh,
                                                   ROOM_W - WAND // 2, (tür_y - tür_hh) // 2, wand_farbe))
        self.wände.append(arcade.SpriteSolidColor(WAND, ROOM_H - (tür_y + tür_hh),
                                                   ROOM_W - WAND // 2, (tür_y + tür_hh + ROOM_H) // 2, wand_farbe))

    def on_update(self, _dt):
        dx, dy = 0.0, 0.0
        if self.move_left:  dx -= SPEED
        if self.move_right: dx += SPEED
        if self.move_up:    dy += SPEED
        if self.move_down:  dy -= SPEED

        length = math.hypot(dx, dy)
        if length > 0:
            dx = dx / length * SPEED
            dy = dy / length * SPEED

        # Textur nach Richtung
        if dy > 0 and abs(dy) >= abs(dx):
            self.player.texture = self.tex_up
        elif dy < 0 and abs(dy) >= abs(dx):
            self.player.texture = self.tex_down
        elif dx > 0:
            self.player.texture = self.tex_right
        elif dx < 0:
            self.player.texture = self.tex_left

        # Bewegung + Randkollision
        new_x = max(MARGIN, min(ROOM_W - MARGIN, self.player.center_x + dx))
        new_y = max(MARGIN, min(ROOM_H - MARGIN, self.player.center_y + dy))
        self.player.center_x = new_x
        self.player.center_y = new_y

    def on_draw(self):
        self.clear()
        self.wände.draw()
        self.türen.draw()
        arcade.draw_sprite(self.player)
        self.maus_sprite.center_x = self.maus_x
        self.maus_sprite.center_y = self.maus_y
        arcade.draw_sprite(self.maus_sprite)

    def on_mouse_motion(self, x, y, _dx, _dy):
        self.maus_x = x
        self.maus_y = y

    def on_key_press(self, key, _mod):
        if key in (arcade.key.A, arcade.key.LEFT):  self.move_left  = True
        if key in (arcade.key.D, arcade.key.RIGHT): self.move_right = True
        if key in (arcade.key.W, arcade.key.UP):    self.move_up    = True
        if key in (arcade.key.S, arcade.key.DOWN):  self.move_down  = True

    def on_key_release(self, key, _mod):
        if key in (arcade.key.A, arcade.key.LEFT):  self.move_left  = False
        if key in (arcade.key.D, arcade.key.RIGHT): self.move_right = False
        if key in (arcade.key.W, arcade.key.UP):    self.move_up    = False
        if key in (arcade.key.S, arcade.key.DOWN):  self.move_down  = False


MyGame()
arcade.run()
