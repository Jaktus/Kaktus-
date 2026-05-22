"""
Physik Engine Simulation
========================
Steuerung:
  Linksklick        → Ball an Mausposition spawnen
  Rechtsklick       → letzten Ball entfernen
  Leertaste         → Simulation zurücksetzen

Fixes gegenüber v1:
  - Kein Klumpen mehr: 8 Solver-Iterationen pro Frame +
    massengewichtete Positionskorrektur
  - Minimale Trenngeschwindigkeit verhindert "festkleben"
  - dist ≈ 0 (übereinanderliegende Bälle) sicher behandelt
  - Jump Pad in der Bildschirmmitte mit Leuchteffekt
"""

import math
import random
import arcade

# ── Konstanten ────────────────────────────────────────────────────────────────
SCREEN_WIDTH   = 800
SCREEN_HEIGHT  = 600
SCREEN_TITLE   = "Physik Engine"

GRAVITY        = 0.45
FRICTION       = 0.995
RESTITUTION    = 0.72      # Ball-zu-Ball Elastizität
WALL_DAMP      = 0.78      # Energieverlust an Wänden
SOLVER_ITERS   = 8         # Kollisions-Iterationen pro Frame  ← Klumpen-Fix

JUMP_FORCE     = 18.0      # Aufwärtsgeschwindigkeit durch Jump Pad
JUMP_W, JUMP_H = 160, 18   # Breite/Höhe des Jump Pads

BALL_COLORS = [
    (255, 213,  79),
    (255, 112,  67),
    ( 77, 208, 225),
    (129, 212, 119),
    (206, 147, 216),
    (255, 138, 101),
    ( 79, 195, 247),
    (240,  98, 146),
    (174, 213,  91),
    (100, 181, 246),
]


# ── Jump Pad ──────────────────────────────────────────────────────────────────
class JumpPad:
    """Rechteckiges Sprungpad das Bälle nach oben katapultiert."""

    def __init__(self, cx: float, cy: float, w: float = JUMP_W, h: float = JUMP_H):
        self.cx = cx
        self.cy = cy
        self.w  = w
        self.h  = h
        self._glow = 0.0

    @property
    def left(self):   return self.cx - self.w / 2
    @property
    def right(self):  return self.cx + self.w / 2
    @property
    def top(self):    return self.cy + self.h / 2
    @property
    def bottom(self): return self.cy - self.h / 2

    def check_and_launch(self, ball: "Ball"):
        if not (self.left - ball.radius < ball.x < self.right + ball.radius):
            return
        if ball.vy >= 0:
            return
        prev_bottom = ball.y - ball.radius - ball.vy
        if prev_bottom >= self.top and ball.y - ball.radius <= self.top:
            ball.y  = self.top + ball.radius
            ball.vy = JUMP_FORCE
            self._glow = 1.0

    def update(self):
        self._glow = max(0.0, self._glow - 0.05)

    def draw(self):
        glow = self._glow
        if glow > 0.01:
            for layer in range(4, 0, -1):
                alpha = int(glow * 60 * (layer / 4))
                expand = layer * 6
                arcade.draw_lrbt_rectangle_filled(
                    self.left  - expand, self.right + expand,
                    self.bottom - expand, self.top   + expand,
                    (100, 255, 180, alpha)
                )
        base_g = int(180 + 75 * glow)
        arcade.draw_lrbt_rectangle_filled(
            self.left, self.right, self.bottom, self.top,
            (30, base_g, 120)
        )
        edge_g = int(200 + 55 * glow)
        arcade.draw_lrbt_rectangle_filled(
            self.left, self.right, self.top - 3, self.top,
            (80, edge_g, 220)
        )
        mx, my = self.cx, self.cy
        arrow_color = (180, 255, 220, int(180 + 75 * glow))
        arcade.draw_triangle_filled(
            mx - 12, my - 3,
            mx + 12, my - 3,
            mx,      my + 7,
            arrow_color
        )


# ── Ball ──────────────────────────────────────────────────────────────────────
class Ball:
    def __init__(self, x: float, y: float, radius: float, color):
        self.x      = float(x)
        self.y      = float(y)
        self.radius = float(radius)
        self.color  = color
        self.vx     = random.uniform(-5, 5)
        self.vy     = random.uniform(1, 7)
        self.mass   = math.pi * radius ** 2

    def update(self, jump_pad: JumpPad):
        self.vy -= GRAVITY
        self.x  += self.vx
        self.y  += self.vy
        self.vx *= FRICTION
        self.vy *= FRICTION

        if self.x - self.radius < 0:
            self.x  = self.radius
            self.vx = abs(self.vx) * WALL_DAMP
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x  = SCREEN_WIDTH - self.radius
            self.vx = -abs(self.vx) * WALL_DAMP

        if self.y - self.radius < 0:
            self.y  = self.radius
            self.vy = abs(self.vy) * WALL_DAMP
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y  = SCREEN_HEIGHT - self.radius
            self.vy = -abs(self.vy) * WALL_DAMP

        jump_pad.check_and_launch(self)

    def draw(self):
        arcade.draw_circle_filled(self.x + 4, self.y - 4, self.radius, (0, 0, 0, 50))
        arcade.draw_circle_filled(self.x, self.y, self.radius, self.color)
        arcade.draw_circle_filled(
            self.x - self.radius * 0.28,
            self.y + self.radius * 0.28,
            self.radius * 0.22,
            (255, 255, 255, 90)
        )


# ── Kollisionsauflösung ───────────────────────────────────────────────────────
def resolve_pair(a: Ball, b: Ball):
    dx   = b.x - a.x
    dy   = b.y - a.y
    dist = math.hypot(dx, dy)
    min_d = a.radius + b.radius

    if dist >= min_d:
        return

    if dist < 0.001:
        angle = random.uniform(0, math.tau)
        dx, dy, dist = math.cos(angle), math.sin(angle), 0.001

    nx = dx / dist
    ny = dy / dist

    overlap    = min_d - dist
    inv_ma     = 1.0 / a.mass
    inv_mb     = 1.0 / b.mass
    inv_total  = inv_ma + inv_mb

    # Massengewichtete Positionskorrektur
    a.x -= nx * overlap * (inv_ma / inv_total)
    a.y -= ny * overlap * (inv_ma / inv_total)
    b.x += nx * overlap * (inv_mb / inv_total)
    b.y += ny * overlap * (inv_mb / inv_total)

    dvx = a.vx - b.vx
    dvy = a.vy - b.vy
    dot = dvx * nx + dvy * ny

    if dot >= 0:
        return

    impulse = -(1.0 + RESTITUTION) * dot / inv_total
    a.vx += (impulse * inv_ma) * nx
    a.vy += (impulse * inv_ma) * ny
    b.vx -= (impulse * inv_mb) * nx
    b.vy -= (impulse * inv_mb) * ny

    # Minimale Trenngeschwindigkeit verhindert Festkleben
    sep = (a.vx - b.vx) * nx + (a.vy - b.vy) * ny
    if sep < 0.3:
        corr = (0.3 - sep) * 0.5
        a.vx += corr * nx;  a.vy += corr * ny
        b.vx -= corr * nx;  b.vy -= corr * ny


# ── Hauptfenster ──────────────────────────────────────────────────────────────
class PhysikEngine(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
                         update_rate=1 / 60)
        arcade.set_background_color((18, 18, 28))
        self.balls:    list[Ball] = []
        self.jump_pad: JumpPad   = JumpPad(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self._fps = 60.0

    def setup(self, count: int = 10):
        self.balls.clear()
        for _ in range(count):
            self._spawn_random()

    def _spawn_random(self, x=None, y=None):
        r  = random.randint(10, 26)
        sx = x if x is not None else random.randint(r, SCREEN_WIDTH - r)
        sy = y if y is not None else random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - r)
        self.balls.append(Ball(sx, sy, r, random.choice(BALL_COLORS)))

    def on_draw(self):
        self.clear()
        self.jump_pad.draw()
        for ball in self.balls:
            ball.draw()
        arcade.draw_text(
            f"Bälle: {len(self.balls)}   FPS: {self._fps:.0f}",
            10, SCREEN_HEIGHT - 26, (220, 220, 220), 14, bold=True
        )
        arcade.draw_text(
            "LK: Ball spawnen  |  RK: entfernen  |  Leertaste: reset",
            10, 8, (130, 130, 150), 11
        )

    def on_update(self, delta_time: float):
        self._fps = 1.0 / delta_time if delta_time > 0 else 60.0
        self.jump_pad.update()

        for ball in self.balls:
            ball.update(self.jump_pad)

        # Mehrere Iterationen → Klumpen-Fix
        for _ in range(SOLVER_ITERS):
            for i in range(len(self.balls)):
                for j in range(i + 1, len(self.balls)):
                    resolve_pair(self.balls[i], self.balls[j])

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._spawn_random(x, y)
        elif button == arcade.MOUSE_BUTTON_RIGHT and self.balls:
            self.balls.pop()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.setup()


# ── Einstiegspunkt ────────────────────────────────────────────────────────────
def main():
    win = PhysikEngine()
    win.setup(count=10)
    arcade.run()


if __name__ == "__main__":
    main()