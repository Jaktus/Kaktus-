import arcade
import math
import random
from arcade.experimental.shadertoy import Shadertoy

# ── Einstellungen ──────────────────────────────────────────
class MyGame(arcade.Window):
    W, H = 800, 600

    def __init__(self):
        super().__init__(self.W, self.H, "Point and Click")
        self.set_mouse_visible(False)
        self.background_color = arcade.color.AMAZON
        self.show_view(GameView())

# ── Level-Vorlage ──────────────────────────────────────────
class Level(arcade.View):
    OBSTACLES = []
    BOX_START  = (100, 100)
    NEXT       = None

    def on_show_view(self):
        win = self.window
        self.cam = arcade.Camera2D(projection=arcade.LRBT(0, win.W, 0, win.H))
        self.cam.match_window(projection=False)
        self.cam.position = (0, 0)

        self.cursor = arcade.Sprite("maus1.png")
        self.cursor.append_texture(arcade.load_texture("maus2.png"))
        self.button = arcade.Sprite("button1.png", center_x=win.W // 2, center_y=win.H // 2)
        self.button.append_texture(arcade.load_texture("button2.png"))
        self.box = arcade.Sprite("box.png", center_x=self.BOX_START[0], center_y=self.BOX_START[1])
        self.walls = arcade.SpriteList()
        for img, x, y in self.OBSTACLES:
            self.walls.append(arcade.Sprite(img, center_x=x, center_y=y))
        self.dragging = False
        self.done     = False

    def on_update(self, dt):
        if not self.done and arcade.check_for_collision(self.box, self.button):
            self.done = True
            if self.NEXT:
                self.window.show_view(self.NEXT())

    def on_draw(self):
        self.clear()
        self.cam.use()
        self.button.set_texture(1 if self.done else 0)
        arcade.draw_sprite(self.button)
        self.walls.draw()
        arcade.draw_sprite(self.box)
        arcade.draw_sprite(self.cursor)

    def _gxy(self, x, y):
        p = self.cam.unproject((x, y))
        return p.x, p.y

    def _move_box(self, dx, dy):
        scale = self.window.W / self.window.width
        old = self.box.position
        self.box.center_x += dx * scale
        self.box.center_y += dy * scale
        if arcade.check_for_collision_with_list(self.box, self.walls):
            self.box.position = old
            return dx * scale, dy * scale
        return 0, 0

    def on_mouse_motion(self, x, y, dx, dy):
        gx, gy = self._gxy(x, y)
        self.cursor.left, self.cursor.top = gx, gy
        if self.dragging:
            if (gx - self.box.center_x)**2 + (gy - self.box.center_y)**2 > 80**2:
                self.dragging = False
                return
            self._move_box(dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor.set_texture(1)
        if self.box.collides_with_point(self._gxy(x, y)):
            self.dragging = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor.set_texture(0)
        self.dragging = False

    def on_key_press(self, key, mod):
        super().on_key_press(key, mod)
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.cam.match_window(projection=False)
            self.cam.position = (0, 0)

# ── Level 0 ────────────────────────────────────────────────
class GameView(Level):
    OBSTACLES = []
    BOX_START  = (100, 100)

# ── Level 1 ────────────────────────────────────────────────
class Level1(Level):
    OBSTACLES = [
        ("wand1.png", 300, 300),
        ("wand1.png", 300, 332),
        ("wand1.png", 300, 364),
        ("wand1.png", 300, 396),
        ("wand1.png", 300, 428),
        ("wand1.png", 300, 460),
    ]
    BOX_START     = (100, 100)
    HIT_THRESHOLD = 8

    def on_show_view(self):
        super().on_show_view()
        self.particles      = []
        self.screwdriver    = None
        self.screw_dragging = False
        self.loch           = None
        self.box_gone       = False

    def _spawn_hit(self):
        if self.screwdriver or self.loch:
            return
        bx, by = self.box.center_x, self.box.center_y
        for _ in range(25):
            angle = random.uniform(0, math.tau)
            spd   = random.uniform(40, 150)
            self.particles.append({
                'x': bx, 'y': by,
                'vx': math.cos(angle) * spd,
                'vy': math.sin(angle) * spd,
                'life': 1.0,
            })
        self.box_gone    = True
        self.dragging    = False
        self.screwdriver = arcade.Sprite("screwdriver.png", center_x=bx, center_y=by)

    def on_update(self, dt):
        for p in self.particles[:]:
            p['life'] -= dt * 1.5
            p['x']    += p['vx'] * dt
            p['y']    += p['vy'] * dt
            if p['life'] <= 0:
                self.particles.remove(p)

        if self.screwdriver and not self.loch:
            if arcade.check_for_collision(self.screwdriver, self.button):
                self.loch = arcade.Sprite("loch.png",
                                          center_x=self.button.center_x,
                                          center_y=self.button.center_y)
                self.screwdriver    = None
                self.screw_dragging = False

        if not self.loch and not self.box_gone and not self.done:
            if arcade.check_for_collision(self.box, self.button):
                self.done = True
                if self.NEXT:
                    self.window.show_view(self.NEXT())

    def on_draw(self):
        self.clear()
        self.cam.use()
        if self.loch:
            arcade.draw_sprite(self.loch)
        else:
            self.button.set_texture(1 if self.done else 0)
            arcade.draw_sprite(self.button)
        self.walls.draw()
        if not self.box_gone:
            arcade.draw_sprite(self.box)
        if self.screwdriver:
            arcade.draw_sprite(self.screwdriver)
        for p in self.particles:
            a = int(255 * max(0, p['life']))
            arcade.draw_rect_filled(arcade.XYWH(p['x'], p['y'], 8, 8), (101, 67, 33, a))
        arcade.draw_sprite(self.cursor)

    def on_mouse_motion(self, x, y, dx, dy):
        gx, gy = self._gxy(x, y)
        self.cursor.left, self.cursor.top = gx, gy
        scale = self.window.W / self.window.width
        if self.screw_dragging and self.screwdriver:
            self.screwdriver.center_x += dx * scale
            self.screwdriver.center_y += dy * scale
        if self.dragging and not self.box_gone:
            if (gx - self.box.center_x)**2 + (gy - self.box.center_y)**2 > 80**2:
                self.dragging = False
                return
            vx, vy = self._move_box(dx, dy)
            if (vx**2 + vy**2) ** 0.5 > self.HIT_THRESHOLD:
                self._spawn_hit()

    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        gx, gy = self._gxy(x, y)
        if self.loch and self.loch.collides_with_point((gx, gy)):
            self.window.show_view(Level2())
            return
        if self.screwdriver and self.screwdriver.collides_with_point((gx, gy)):
            self.dragging       = False
            self.screw_dragging = True

    def on_mouse_release(self, x, y, button, modifiers):
        super().on_mouse_release(x, y, button, modifiers)
        self.screw_dragging = False

# ── Level 2 – Schwarzes Loch (Shadertoy) ──────────────────
class Level2(arcade.View):
    GLSL = """
        void mainImage(out vec4 fragColor, in vec2 fragCoord) {
            vec2  center = iResolution.xy * 0.5;
            float scale  = min(iResolution.x, iResolution.y);
            vec2  uv     = (fragCoord - center) / scale;
            float dist   = length(uv);

            vec3 col = vec3(0.45);

            for (int i = 0; i < 60; i++) {
                float fi   = float(i);
                float seed = fi * 1.6180339887;
                float baseAngle  = fract(seed * 2.399) * 6.28318;
                float baseRadius = 0.08 + fract(seed * 0.753) * 0.50;
                float speed      = 0.4 + fract(seed * 0.310) * 0.70;

                float t      = mod(iTime * speed + fract(seed * 0.47), 1.0);
                float radius = baseRadius * (1.0 - t);
                float angle  = baseAngle + t * 8.0 + iTime * speed;

                vec2  ppos  = vec2(cos(angle), sin(angle)) * radius;
                float d     = length(uv - ppos);
                float psize = mix(0.013, 0.001, t);
                float b     = smoothstep(psize, 0.0, d) * (1.0 - t * 0.3);

                vec3 pcolor = (mod(fi, 2.0) < 1.0)
                    ? mix(vec3(0.55, 0.0, 0.65), vec3(0.0), t)
                    : mix(vec3(0.10, 0.0, 0.15), vec3(0.0), t * 0.5);
                col = mix(col, pcolor, clamp(b, 0.0, 1.0));
            }

            col += vec3(0.2, 0.0, 0.3) * (0.025 / (dist * dist + 0.002)) * 0.3;
            col  = mix(col, vec3(0.0), smoothstep(0.07, 0.04, dist));

            vec2  mouseUV = (iMouse.xy - center) / scale;
            float cd      = length(uv - mouseUV);
            col = mix(col, vec3(1.0), smoothstep(0.018, 0.006, cd));

            fragColor = vec4(col, 1.0);
        }
    """

    def on_show_view(self):
        win = self.window
        self.cx, self.cy = win.W // 2, win.H // 2
        self.cur_x = float(win.W * 0.15)
        self.cur_y = float(win.H * 0.15)
        self.time  = 0.0
        self.shader = Shadertoy((win.W, win.H), self.GLSL)
        self.cam = arcade.Camera2D(projection=arcade.LRBT(0, win.W, 0, win.H))
        self.cam.match_window(projection=False)
        self.cam.position = (0, 0)
        self.cursor = arcade.Sprite("maus1.png")
        self.cursor.append_texture(arcade.load_texture("maus2.png"))

    def on_update(self, dt):
        self.time  += dt
        self.cur_x += (self.cx - self.cur_x) * 0.015
        self.cur_y += (self.cy - self.cur_y) * 0.015
        if (self.cur_x - self.cx)**2 + (self.cur_y - self.cy)**2 < 30**2:
            self.window.show_view(Level3())

    def on_draw(self):
        self.clear()
        self.shader.render(time=self.time, mouse_position=(self.cur_x, self.cur_y))
        self.cam.use()
        self.cursor.left = self.cur_x
        self.cursor.top  = self.cur_y
        arcade.draw_sprite(self.cursor)

    def on_mouse_motion(self, x, y, dx, dy):
        self.cur_x += (x - self.cur_x) * 0.08 + dx * 0.4
        self.cur_y += (y - self.cur_y) * 0.08 + dy * 0.4

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor.set_texture(1)

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor.set_texture(0)

# ── Level 3 – Zahnräder ───────────────────────────────────
class Level3(arcade.View):
    PM_X, PM_Y = 400, 300   # pause-menu center
    PM_W, PM_H = 420, 360   # pause-menu size

    def on_show_view(self):
        win = self.window
        self.cam = arcade.Camera2D(projection=arcade.LRBT(0, win.W, 0, win.H))
        self.cam.match_window(projection=False)
        self.cam.position = (0, 0)
        self.window.background_color = (50, 50, 55)

        self.cursor = arcade.Sprite("maus1.png")
        self.cursor.append_texture(arcade.load_texture("maus2.png"))

        self.left_view = False
        self.paused    = False

        # screwdriver (taken from pause menu)
        self.screw_taken = False
        self.screw       = None
        self.screw_drag  = False
        self.pause_screw = arcade.Sprite("screwdriver.png",
                                          center_x=self.PM_X + 168,
                                          center_y=self.PM_Y + 155)

        # slider knob = cogwheel small texture
        self.slider_x    = float(self.PM_X)
        self.slider_drag = False
        self.slider_knob = arcade.Sprite("cogwheel small.png",
                                          center_x=self.slider_x,
                                          center_y=self.PM_Y - 40)

        # right view
        self.big_place    = arcade.Sprite("cogwheel big place.png",   center_x=150, center_y=340)
        self.small_place  = arcade.Sprite("cogwheel smallplace.png",  center_x=430, center_y=340)
        self.massiv_place = arcade.Sprite("cogwheel massivplace.png", center_x=660, center_y=340)
        self.big_cog      = arcade.Sprite("cogwheel big.png",         center_x=150, center_y=340)
        self.panel        = arcade.Sprite("wand2.png",                 center_x=430, center_y=490)
        self.small_cog    = arcade.Sprite("cogwheel small.png",        center_x=430, center_y=490)
        self.massiv_cog_r = arcade.Sprite("cogwheel massiv.png",       center_x=660, center_y=340)

        self.big_placed    = True   # pre-placed
        self.small_freed   = False
        self.small_drag    = False
        self.small_placed  = False
        self.massiv_placed = False

        # left view
        self.cover_pos      = (350, 490)
        self.cover_removed  = False
        self.btn_pressed    = False
        self.massiv_cog     = arcade.Sprite("cogwheel massiv.png", center_x=350, center_y=565)
        self.massiv_vy      = 0.0
        self.massiv_fall    = False
        self.massiv_place_L = arcade.Sprite("cogwheel massivplace.png", center_x=350, center_y=220)

    def _gxy(self, x, y):
        p = self.cam.unproject((x, y))
        return p.x, p.y

    def on_update(self, dt):
        if self.paused:
            return
        if self.massiv_fall:
            self.massiv_vy -= 600 * dt
            self.massiv_cog.center_y += self.massiv_vy * dt
            if self.massiv_cog.center_y <= self.massiv_place_L.center_y:
                self.massiv_cog.center_y = self.massiv_place_L.center_y
                self.massiv_vy   = 0.0
                self.massiv_fall = False
                self.massiv_placed = True
        if self.big_placed and self.small_placed and self.massiv_placed:
            self.window.show_view(Level4())

    def on_draw(self):
        self.clear()
        self.cam.use()
        if not self.left_view:
            self._draw_right()
        else:
            self._draw_left()
        if self.screw and not self.paused:
            arcade.draw_sprite(self.screw)
        if self.paused:
            self._draw_pause()
        arcade.draw_sprite(self.cursor)

    def _draw_right(self):
        arcade.draw_sprite(self.big_place)
        arcade.draw_sprite(self.small_place)
        arcade.draw_sprite(self.massiv_place)
        arcade.draw_sprite(self.big_cog)
        if self.small_freed:
            arcade.draw_sprite(self.small_cog)
        else:
            arcade.draw_sprite(self.panel)
        if self.massiv_placed:
            arcade.draw_sprite(self.massiv_cog_r)
        if self.small_placed:
            arcade.draw_text("◄", 18, 272, arcade.color.WHITE, 48)
        arcade.draw_text("ESC", 10, 10, (110, 110, 110), 12)

    def _draw_left(self):
        arcade.draw_sprite(self.massiv_place_L)
        arcade.draw_sprite(self.massiv_cog)
        cx, cy = self.cover_pos
        if not self.cover_removed:
            arcade.draw_rect_filled(arcade.XYWH(cx, cy, 100, 22), (130, 130, 140))
            arcade.draw_rect_outline(arcade.XYWH(cx, cy, 100, 22), (70, 70, 70), 2)
        elif not self.btn_pressed:
            arcade.draw_circle_filled(cx, cy, 18, (190, 30, 30))
            arcade.draw_circle_outline(cx, cy, 18, (50, 50, 50), 2)
        arcade.draw_text("►", 738, 272, arcade.color.WHITE, 48)

    def _draw_pause(self):
        win = self.window
        px, py, pw, ph = self.PM_X, self.PM_Y, self.PM_W, self.PM_H
        arcade.draw_rect_filled(
            arcade.XYWH(win.W // 2, win.H // 2, win.W, win.H), (0, 0, 0, 160))
        arcade.draw_rect_filled(arcade.XYWH(px, py, pw, ph), (55, 55, 60))
        arcade.draw_rect_outline(arcade.XYWH(px, py, pw, ph), (150, 150, 150), 3)
        arcade.draw_text("PAUSE", px - 38, py + 155, arcade.color.WHITE, 22)
        if not self.screw_taken:
            arcade.draw_sprite(self.pause_screw)
        arcade.draw_rect_filled(arcade.XYWH(px, py - 40, 300, 8), (90, 90, 90))
        self.slider_knob.center_x = self.slider_x
        self.slider_knob.center_y = py - 40
        arcade.draw_sprite(self.slider_knob)
        arcade.draw_text("ESC zum Schließen", px - 88, py - 160, (170, 170, 170), 13)

    def on_mouse_motion(self, x, y, dx, dy):
        gx, gy = self._gxy(x, y)
        self.cursor.left, self.cursor.top = gx, gy
        scale = self.window.W / self.window.width
        if self.screw_drag and self.screw:
            self.screw.center_x += dx * scale
            self.screw.center_y += dy * scale
        if self.slider_drag:
            lo, hi = self.PM_X - 140, self.PM_X + 140
            self.slider_x = max(lo, min(hi, self.slider_x + dx * scale))
        if self.small_drag:
            self.small_cog.center_x += dx * scale
            self.small_cog.center_y += dy * scale

    def on_mouse_press(self, x, y, button, modifiers):
        self.cursor.set_texture(1)
        gx, gy = self._gxy(x, y)
        if self.paused:
            self._press_pause(gx, gy)
            return
        if not self.left_view:
            self._press_right(gx, gy)
        else:
            self._press_left(gx, gy)

    def _press_pause(self, gx, gy):
        if not self.screw_taken and self.pause_screw.collides_with_point((gx, gy)):
            self.screw_taken = True
            self.screw       = arcade.Sprite("screwdriver.png", center_x=gx, center_y=gy)
            self.screw_drag  = True
            self.paused      = False
            return
        if self.slider_knob.collides_with_point((gx, gy)):
            self.slider_drag = True

    def _press_right(self, gx, gy):
        if self.screw and not self.small_freed and self.panel.collides_with_point((gx, gy)):
            self.small_freed = True
            return
        if self.small_freed and not self.small_placed \
                and self.small_cog.collides_with_point((gx, gy)):
            self.small_drag = True
            return
        if self.small_placed and gx < 72 and 255 < gy < 335:
            self.left_view = True
            return
        if self.screw and self.screw.collides_with_point((gx, gy)):
            self.screw_drag = True

    def _press_left(self, gx, gy):
        cx, cy = self.cover_pos
        if self.screw and not self.cover_removed:
            if abs(gx - cx) < 55 and abs(gy - cy) < 16:
                self.cover_removed = True
                return
        if self.cover_removed and not self.btn_pressed:
            if (gx - cx) ** 2 + (gy - cy) ** 2 < 22 ** 2:
                self.btn_pressed = True
                self.massiv_fall = True
                self.massiv_vy   = 0.0
                return
        if gx > 728 and 255 < gy < 335:
            self.left_view = False
            return
        if self.screw and self.screw.collides_with_point((gx, gy)):
            self.screw_drag = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.cursor.set_texture(0)
        if self.small_drag:
            if arcade.check_for_collision(self.small_cog, self.small_place):
                self.small_cog.center_x = self.small_place.center_x
                self.small_cog.center_y = self.small_place.center_y
                self.small_placed = True
            self.small_drag = False
        self.screw_drag  = False
        self.slider_drag = False

    def on_key_press(self, key, mod):
        super().on_key_press(key, mod)
        if key == arcade.key.ESCAPE:
            self.paused = not self.paused
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.cam.match_window(projection=False)
            self.cam.position = (0, 0)

# ── Level 4 ────────────────────────────────────────────────
class Level4(arcade.View):
    def on_show_view(self):
        self.window.background_color = (30, 30, 30)

    def on_draw(self):
        self.clear()

GameView.NEXT = Level1
Level1.NEXT   = GameView

MyGame()
arcade.run()
