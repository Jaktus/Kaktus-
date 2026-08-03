import math
import random
from collections import deque
from pathlib import Path

import arcade
from PIL import Image

import make_textures

ASSETS_FOLDER = Path(__file__).parent / "assets"

TILE_SCALE = 3
TILE_SIZE = make_textures.TEXTURE_SIZE * TILE_SCALE

MAP_COLUMNS = 70
MAP_ROWS = 46
MAP_WIDTH = MAP_COLUMNS * TILE_SIZE
MAP_HEIGHT = MAP_ROWS * TILE_SIZE

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Ebene Gelb"

PLAYER_WALK_SPEED = 230
PLAYER_CROUCH_SPEED = 110
PLAYER_RADIUS = 21
CAMERA_FOLLOW = 0.12
REACH_DISTANCE = 70

DARKNESS_SCALE = 7

MINIMAP_SCALE = 4
MINIMAP_WIDTH = MAP_COLUMNS * MINIMAP_SCALE
MINIMAP_HEIGHT = MAP_ROWS * MINIMAP_SCALE
MINIMAP_LEFT = WINDOW_WIDTH - MINIMAP_WIDTH - 14
MINIMAP_BOTTOM = WINDOW_HEIGHT - MINIMAP_HEIGHT - 14

BEEP_NEAR_DELAY = 0.9
BEEP_FAR_DELAY = 3.5
BEEP_MAX_DISTANCE = 2200

MONSTER_CLIP_LENGTH = 4.089
MONSTER_STEP_TIMES = [0.18, 0.65, 1.12, 1.62, 2.11, 2.62, 3.16, 3.73]

MONSTER_FOLLOW_DISTANCE = 80
MONSTER_FOLLOW_SPEED = 240
MONSTER_ROAM_SPEED = 95
MONSTER_SEARCH_SPEED = 135
MONSTER_CHASE_SPEED = 205
MONSTER_RADIUS = 18
MONSTER_HEAR_DISTANCE = 500
MONSTER_VIEW_DISTANCE = 650
MONSTER_LOST_TIME = 5.0
MONSTER_SEARCH_TIME = 7.0
MONSTER_CATCH_DISTANCE = 42
MONSTER_SOUND_DISTANCE = 1400
PATH_REFRESH_TIME = 0.4
WAYPOINT_REACHED = 12
PATH_SHORTCUT_STEPS = 8

TRANSFORM_STEP_TIME = 0.8

WALL = 1
FLOOR = 0

WALL_COLUMNS = [14, 28, 42, 56]
WALL_ROWS = [11, 22, 33]

DOORWAYS = [
    (14, 5, 1, 2),
    (14, 27, 1, 2),
    (14, 38, 1, 2),
    (28, 5, 1, 2),
    (28, 16, 1, 2),
    (28, 38, 1, 2),
    (42, 5, 1, 2),
    (42, 27, 1, 2),
    (42, 38, 1, 2),
    (56, 5, 1, 2),
    (56, 16, 1, 2),
    (56, 38, 1, 2),
    (6, 11, 2, 1),
    (34, 11, 2, 1),
    (61, 11, 2, 1),
    (20, 22, 2, 1),
    (48, 22, 2, 1),
    (6, 33, 2, 1),
    (34, 33, 2, 1),
    (61, 33, 2, 1),
]

EXTRA_WALLS = [
    (18, 3, 1, 6),
    (32, 24, 6, 1),
    (46, 13, 1, 7),
    (58, 5, 8, 1),
    (20, 13, 5, 1),
    (33, 36, 1, 7),
]

PILLAR_FIELDS = [
    (4, 4, 3, 2, 4),
    (30, 13, 3, 2, 4),
    (58, 25, 3, 2, 4),
    (16, 36, 3, 2, 4),
    (44, 25, 3, 2, 4),
    (4, 36, 3, 2, 4),
]

TASKS = [
    ("Sektor A1", "wires", 3, 3),
    ("Sektor C2", "numbers", 36, 15),
    ("Sektor E4", "download", 60, 37),
    ("Sektor B3", "simon", 18, 26),
    ("Sektor D1", "swipe", 45, 4),
    ("Sektor E2", "align", 62, 15),
    ("Sektor A3", "wires", 6, 27),
    ("Sektor C4", "numbers", 37, 39),
    ("Sektor D4", "download", 50, 40),
]

TASK_NAMES = {
    "wires": "Kabel verbinden",
    "numbers": "Zahlen 1-6 anklicken",
    "download": "Daten runterladen",
    "simon": "Reaktor starten",
    "swipe": "Karte durchziehen",
    "align": "Antenne ausrichten",
}

TRANSFORM_TASK_INDEX = 2

START_COLUMN = 35
START_ROW = 5
MONSTER_START_COLUMN = 32
MONSTER_START_ROW = 5
MAP_MIDDLE_COLUMN = 35
MAP_MIDDLE_ROW = 27

INTRO_LINES = [
    "Hallo. Du bist neu hier, oder?",
    "Keine Angst. Ich beisse nicht.",
    "Noch nicht.",
    "Die Konsolen leuchten rot. Repariere sie alle.",
    "Dann darfst du gehen. So lautet die Regel.",
    "Ich bleibe in deiner Naehe. Nur zum Zuschauen.",
]

TRANSFORM_LINES = [
    "Nicht so schnell.",
    "Du bist zu schnell. Das gefaellt mir nicht.",
    "Die Regel hat sich gerade geaendert.",
]


def make_empty_map():
    tiles = []
    for row in range(MAP_ROWS):
        tiles.append([FLOOR] * MAP_COLUMNS)
    return tiles


def add_outer_walls(tiles):
    for column in range(MAP_COLUMNS):
        tiles[0][column] = WALL
        tiles[MAP_ROWS - 1][column] = WALL
    for row in range(MAP_ROWS):
        tiles[row][0] = WALL
        tiles[row][MAP_COLUMNS - 1] = WALL


def add_main_walls(tiles):
    for column in WALL_COLUMNS:
        for row in range(1, MAP_ROWS - 1):
            tiles[row][column] = WALL

    for row in WALL_ROWS:
        for column in range(1, MAP_COLUMNS - 1):
            tiles[row][column] = WALL


def add_rectangle(tiles, left, bottom, width, height, value):
    for row in range(bottom, bottom + height):
        for column in range(left, left + width):
            tiles[row][column] = value


def add_extra_walls(tiles):
    for left, bottom, width, height in EXTRA_WALLS:
        add_rectangle(tiles, left, bottom, width, height, WALL)


def add_pillars(tiles):
    for left, bottom, columns, rows, spacing in PILLAR_FIELDS:
        for pillar_row in range(rows):
            for pillar_column in range(columns):
                column = left + pillar_column * spacing
                row = bottom + pillar_row * spacing
                tiles[row][column] = WALL


def open_doorways(tiles):
    for left, bottom, width, height in DOORWAYS:
        add_rectangle(tiles, left, bottom, width, height, FLOOR)


def build_map():
    tiles = make_empty_map()
    add_outer_walls(tiles)
    add_main_walls(tiles)
    add_extra_walls(tiles)
    add_pillars(tiles)
    open_doorways(tiles)
    return tiles


def collect_floor_tiles(tiles):
    floor_tiles = []
    for row in range(MAP_ROWS):
        for column in range(MAP_COLUMNS):
            if tiles[row][column] == FLOOR:
                floor_tiles.append((column, row))
    return floor_tiles


def tile_center(column, row):
    x = column * TILE_SIZE + TILE_SIZE / 2
    y = row * TILE_SIZE + TILE_SIZE / 2
    return x, y


def point_is_wall(tiles, x, y):
    column = int(x // TILE_SIZE)
    row = int(y // TILE_SIZE)
    if column < 0 or column >= MAP_COLUMNS:
        return True
    if row < 0 or row >= MAP_ROWS:
        return True
    return tiles[row][column] == WALL


def box_hits_wall(tiles, x, y, radius):
    for corner_x in (x - radius, x + radius):
        for corner_y in (y - radius, y + radius):
            if point_is_wall(tiles, corner_x, corner_y):
                return True
    return False


def line_is_clear(tiles, start_x, start_y, end_x, end_y):
    distance = math.dist((start_x, start_y), (end_x, end_y))
    if distance <= 0:
        return True

    steps = int(distance / (TILE_SIZE / 3)) + 1
    for step in range(steps + 1):
        part = step / steps
        x = start_x + (end_x - start_x) * part
        y = start_y + (end_y - start_y) * part
        if point_is_wall(tiles, x, y):
            return False

    return True


def wide_line_is_clear(tiles, start_x, start_y, end_x, end_y, radius):
    difference_x = end_x - start_x
    difference_y = end_y - start_y
    length = math.hypot(difference_x, difference_y)
    if length == 0:
        return not point_is_wall(tiles, start_x, start_y)

    offset_x = -difference_y / length * radius
    offset_y = difference_x / length * radius

    for side in (-1, 0, 1):
        shift_x = offset_x * side
        shift_y = offset_y * side
        clear = line_is_clear(
            tiles,
            start_x + shift_x, start_y + shift_y,
            end_x + shift_x, end_y + shift_y,
        )
        if not clear:
            return False

    return True


def find_path(tiles, start, goal):
    if start == goal:
        return []
    if tiles[goal[1]][goal[0]] == WALL:
        return []

    came_from = {start: None}
    queue = deque()
    queue.append(start)
    found = False

    while queue:
        current = queue.popleft()
        if current == goal:
            found = True
            break

        column, row = current
        for step_column, step_row in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = (column + step_column, row + step_row)
            if neighbour in came_from:
                continue
            if neighbour[0] < 0 or neighbour[0] >= MAP_COLUMNS:
                continue
            if neighbour[1] < 0 or neighbour[1] >= MAP_ROWS:
                continue
            if tiles[neighbour[1]][neighbour[0]] == WALL:
                continue
            came_from[neighbour] = current
            queue.append(neighbour)

    if not found:
        return []

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]

    path.reverse()
    return path[1:]


def load_sound_file(name):
    mp3_path = ASSETS_FOLDER / (name + ".mp3")
    if mp3_path.exists():
        return arcade.load_sound(mp3_path)

    wav_path = ASSETS_FOLDER / (name + ".wav")
    if wav_path.exists():
        return arcade.load_sound(wav_path)

    return None


def play_sound_safe(sound, volume, loop=False):
    if sound is None:
        return None
    return arcade.play_sound(sound, volume=volume, loop=loop)


PANEL_WIDTH = 620
PANEL_HEIGHT = 420
PANEL_LEFT = WINDOW_WIDTH / 2 - PANEL_WIDTH / 2
PANEL_RIGHT = WINDOW_WIDTH / 2 + PANEL_WIDTH / 2
PANEL_BOTTOM = WINDOW_HEIGHT / 2 - PANEL_HEIGHT / 2
PANEL_TOP = WINDOW_HEIGHT / 2 + PANEL_HEIGHT / 2
PANEL_CENTER_X = WINDOW_WIDTH / 2
PANEL_CENTER_Y = WINDOW_HEIGHT / 2

WIRE_COLORS = [(224, 68, 68), (242, 206, 76), (86, 156, 244), (206, 96, 224)]

NUMBER_SPOTS = [
    (-210, 100),
    (-40, 130),
    (180, 110),
    (-160, -20),
    (40, -60),
    (200, -120),
]

SIMON_SPOTS = [
    (-130, 80),
    (130, 80),
    (-130, -80),
    (130, -80),
]


def draw_panel():
    arcade.draw_lrbt_rectangle_filled(
        PANEL_LEFT - 6, PANEL_RIGHT + 6, PANEL_BOTTOM - 6, PANEL_TOP + 6, (18, 16, 24)
    )
    arcade.draw_lrbt_rectangle_filled(
        PANEL_LEFT, PANEL_RIGHT, PANEL_BOTTOM, PANEL_TOP, (44, 42, 58)
    )


class WirePuzzle:
    def __init__(self, textures):
        self.title = "Kabel verbinden"
        self.hint = "Links ein Kabel anklicken, dann rechts die gleiche Farbe"
        self.solved = False
        self.selected = None
        self.connections = {}
        self.mouse = (0, 0)

        self.left_points = []
        self.right_points = []
        for index in range(4):
            y = PANEL_TOP - 90 - index * 80
            self.left_points.append((PANEL_LEFT + 90, y))
            self.right_points.append((PANEL_RIGHT - 90, y))

        self.right_colors = [0, 1, 2, 3]
        random.shuffle(self.right_colors)

        self.sprites = arcade.SpriteList()
        for index in range(4):
            left_plug = arcade.Sprite(textures["plug"], scale=3)
            left_plug.position = self.left_points[index]
            left_plug.color = WIRE_COLORS[index]
            self.sprites.append(left_plug)

            right_plug = arcade.Sprite(textures["plug"], scale=3)
            right_plug.position = self.right_points[index]
            right_plug.color = WIRE_COLORS[self.right_colors[index]]
            self.sprites.append(right_plug)

    def update(self, delta_time):
        pass

    def on_mouse_motion(self, x, y):
        self.mouse = (x, y)

    def on_mouse_press(self, x, y):
        for index in range(4):
            if index in self.connections:
                continue
            if math.dist((x, y), self.left_points[index]) < 32:
                self.selected = index
                return False

        if self.selected is None:
            return False

        for index in range(4):
            if math.dist((x, y), self.right_points[index]) < 32:
                if self.right_colors[index] == self.selected:
                    self.connections[self.selected] = index
                    self.selected = None
                    if len(self.connections) == 4:
                        self.solved = True
                    return True
                self.selected = None

        return False

    def on_mouse_release(self):
        pass

    def draw(self):
        draw_panel()

        for left_index in self.connections:
            right_index = self.connections[left_index]
            start = self.left_points[left_index]
            end = self.right_points[right_index]
            arcade.draw_line(start[0], start[1], end[0], end[1], WIRE_COLORS[left_index], 9)

        if self.selected is not None:
            start = self.left_points[self.selected]
            arcade.draw_line(
                start[0], start[1], self.mouse[0], self.mouse[1],
                WIRE_COLORS[self.selected], 5,
            )

        self.sprites.draw(pixelated=True)


class NumberPuzzle:
    def __init__(self, textures):
        self.title = "Zahlen 1-6 anklicken"
        self.hint = "Klicke die Zahlen der Reihe nach an: 1, 2, 3, 4, 5, 6"
        self.solved = False
        self.next_number = 1

        numbers = [1, 2, 3, 4, 5, 6]
        random.shuffle(numbers)

        self.buttons = []
        self.sprites = arcade.SpriteList()
        for index in range(6):
            offset_x, offset_y = NUMBER_SPOTS[index]
            x = PANEL_CENTER_X + offset_x
            y = PANEL_CENTER_Y + offset_y
            number = numbers[index]

            sprite = arcade.Sprite(textures["number_" + str(number)], scale=5)
            sprite.position = (x, y)
            self.sprites.append(sprite)
            self.buttons.append((number, x, y, sprite))

    def update(self, delta_time):
        pass

    def on_mouse_motion(self, x, y):
        pass

    def reset(self):
        self.next_number = 1
        for number, x, y, sprite in self.buttons:
            sprite.color = (255, 255, 255)

    def on_mouse_press(self, x, y):
        for number, button_x, button_y, sprite in self.buttons:
            if math.dist((x, y), (button_x, button_y)) > 44:
                continue

            if number == self.next_number:
                sprite.color = (90, 220, 130)
                self.next_number = self.next_number + 1
                if self.next_number > 6:
                    self.solved = True
                return True

            self.reset()
            return False

        return False

    def on_mouse_release(self):
        pass

    def draw(self):
        draw_panel()
        self.sprites.draw(pixelated=True)


class DownloadPuzzle:
    def __init__(self, textures):
        self.title = "Daten runterladen"
        self.hint = "Knopf gedrueckt halten, bis der Balken voll ist"
        self.solved = False
        self.progress = 0.0
        self.holding = False

        self.button_x = PANEL_CENTER_X
        self.button_y = PANEL_CENTER_Y - 90
        self.button_radius = 70

    def update(self, delta_time):
        if self.holding and not self.solved:
            self.progress = self.progress + delta_time * 0.4
            if self.progress >= 1.0:
                self.progress = 1.0
                self.solved = True

    def on_mouse_motion(self, x, y):
        pass

    def on_mouse_press(self, x, y):
        if math.dist((x, y), (self.button_x, self.button_y)) < self.button_radius:
            self.holding = True
        return False

    def on_mouse_release(self):
        self.holding = False

    def draw(self):
        draw_panel()

        bar_left = PANEL_LEFT + 60
        bar_right = PANEL_RIGHT - 60
        bar_bottom = PANEL_CENTER_Y + 60
        bar_top = bar_bottom + 46

        arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (26, 24, 34))
        filled_right = bar_left + (bar_right - bar_left) * self.progress
        if filled_right > bar_left:
            arcade.draw_lrbt_rectangle_filled(
                bar_left, filled_right, bar_bottom, bar_top, (90, 220, 130)
            )

        if self.holding:
            button_color = (200, 150, 70)
        else:
            button_color = (150, 110, 50)
        arcade.draw_circle_filled(self.button_x, self.button_y, self.button_radius, button_color)
        arcade.draw_circle_filled(
            self.button_x, self.button_y, self.button_radius - 12, (230, 190, 90)
        )


class SimonPuzzle:
    def __init__(self, textures):
        self.title = "Reaktor starten"
        self.hint = "Merke dir die Reihenfolge und klicke sie danach nach"
        self.solved = False

        self.sequence = []
        for _ in range(4):
            self.sequence.append(random.randrange(4))

        self.showing = True
        self.show_step = 0
        self.show_timer = 0.8
        self.lit_button = None
        self.input_index = 0

        self.points = []
        self.sprites = arcade.SpriteList()
        for index in range(4):
            offset_x, offset_y = SIMON_SPOTS[index]
            x = PANEL_CENTER_X + offset_x
            y = PANEL_CENTER_Y + offset_y
            self.points.append((x, y))

            sprite = arcade.Sprite(textures["plug"], scale=6)
            sprite.position = (x, y)
            self.sprites.append(sprite)

    def update(self, delta_time):
        if not self.showing:
            return

        self.show_timer = self.show_timer - delta_time
        if self.show_timer > 0:
            return

        if self.lit_button is None:
            if self.show_step >= len(self.sequence):
                self.showing = False
                self.show_step = 0
                return
            self.lit_button = self.sequence[self.show_step]
            self.show_timer = 0.45
        else:
            self.lit_button = None
            self.show_step = self.show_step + 1
            self.show_timer = 0.2

    def restart_showing(self):
        self.showing = True
        self.show_step = 0
        self.show_timer = 0.6
        self.lit_button = None
        self.input_index = 0

    def on_mouse_motion(self, x, y):
        pass

    def on_mouse_press(self, x, y):
        if self.showing:
            return False

        for index in range(4):
            if math.dist((x, y), self.points[index]) > 54:
                continue

            if index == self.sequence[self.input_index]:
                self.input_index = self.input_index + 1
                if self.input_index >= len(self.sequence):
                    self.solved = True
                return True

            self.restart_showing()
            return False

        return False

    def on_mouse_release(self):
        pass

    def draw(self):
        draw_panel()

        for index in range(4):
            sprite = self.sprites[index]
            color = WIRE_COLORS[index]
            if self.showing and self.lit_button != index:
                sprite.color = (color[0] // 4, color[1] // 4, color[2] // 4)
            elif self.showing:
                sprite.color = color
            elif index < self.input_index:
                sprite.color = color
            else:
                sprite.color = (color[0] // 2, color[1] // 2, color[2] // 2)

        self.sprites.draw(pixelated=True)


class SwipePuzzle:
    def __init__(self, textures):
        self.title = "Karte durchziehen"
        self.hint = "Karte mit gedrueckter Maustaste nach rechts ziehen"
        self.solved = False
        self.dragging = False

        self.slot_left = PANEL_LEFT + 90
        self.slot_right = PANEL_RIGHT - 90
        self.slot_y = PANEL_CENTER_Y
        self.card_x = self.slot_left

        self.sprite = arcade.Sprite(textures["card"], scale=5)
        self.sprite.position = (self.card_x, self.slot_y)
        self.sprites = arcade.SpriteList()
        self.sprites.append(self.sprite)

    def update(self, delta_time):
        self.sprite.position = (self.card_x, self.slot_y)

    def on_mouse_motion(self, x, y):
        if not self.dragging or self.solved:
            return

        if x < self.slot_left:
            self.card_x = self.slot_left
        elif x > self.slot_right:
            self.card_x = self.slot_right
        else:
            self.card_x = x

        if self.card_x >= self.slot_right - 2:
            self.solved = True

    def on_mouse_press(self, x, y):
        if math.dist((x, y), (self.card_x, self.slot_y)) < 50:
            self.dragging = True
        return False

    def on_mouse_release(self):
        self.dragging = False
        if not self.solved:
            self.card_x = self.slot_left

    def draw(self):
        draw_panel()

        arcade.draw_lrbt_rectangle_filled(
            self.slot_left - 40, self.slot_right + 40,
            self.slot_y - 46, self.slot_y + 46,
            (26, 24, 34),
        )
        arcade.draw_line(
            self.slot_left, self.slot_y, self.slot_right, self.slot_y, (90, 88, 110), 3
        )
        self.sprites.draw(pixelated=True)


class AlignPuzzle:
    def __init__(self, textures):
        self.title = "Antenne ausrichten"
        self.hint = "Punkt in den gruenen Kreis ziehen und ruhig halten"
        self.solved = False
        self.dragging = False
        self.hold_timer = 0.0

        self.target_x = PANEL_CENTER_X
        self.target_y = PANEL_CENTER_Y
        self.target_radius = 46

        self.marker_x = PANEL_CENTER_X + random.choice([-190, 190])
        self.marker_y = PANEL_CENTER_Y + random.choice([-120, 120])

    def update(self, delta_time):
        if self.solved:
            return

        distance = math.dist((self.marker_x, self.marker_y), (self.target_x, self.target_y))
        if distance < self.target_radius:
            self.hold_timer = self.hold_timer + delta_time
            if self.hold_timer >= 1.2:
                self.solved = True
        else:
            self.hold_timer = 0.0

    def on_mouse_motion(self, x, y):
        if self.dragging and not self.solved:
            self.marker_x = x
            self.marker_y = y

    def on_mouse_press(self, x, y):
        if math.dist((x, y), (self.marker_x, self.marker_y)) < 40:
            self.dragging = True
        return False

    def on_mouse_release(self):
        self.dragging = False

    def draw(self):
        draw_panel()

        arcade.draw_circle_outline(
            self.target_x, self.target_y, self.target_radius, (90, 220, 130), 4
        )

        bar_left = PANEL_LEFT + 60
        bar_right = PANEL_RIGHT - 60
        bar_bottom = PANEL_BOTTOM + 40
        arcade.draw_lrbt_rectangle_filled(
            bar_left, bar_right, bar_bottom, bar_bottom + 24, (26, 24, 34)
        )
        filled = bar_left + (bar_right - bar_left) * min(1.0, self.hold_timer / 1.2)
        if filled > bar_left:
            arcade.draw_lrbt_rectangle_filled(
                bar_left, filled, bar_bottom, bar_bottom + 24, (90, 220, 130)
            )

        arcade.draw_circle_filled(self.marker_x, self.marker_y, 18, (240, 200, 90))
        arcade.draw_circle_outline(self.marker_x, self.marker_y, 18, (60, 50, 30), 3)


PUZZLE_CLASSES = {
    "wires": WirePuzzle,
    "numbers": NumberPuzzle,
    "download": DownloadPuzzle,
    "simon": SimonPuzzle,
    "swipe": SwipePuzzle,
    "align": AlignPuzzle,
}


def monster_frame_for_time(time_in_clip):
    step_index = 0
    for index in range(len(MONSTER_STEP_TIMES)):
        if time_in_clip >= MONSTER_STEP_TIMES[index]:
            step_index = index + 1

    if step_index == 0:
        return 1

    step_start = MONSTER_STEP_TIMES[step_index - 1]
    if step_index < len(MONSTER_STEP_TIMES):
        step_end = MONSTER_STEP_TIMES[step_index]
    else:
        step_end = MONSTER_CLIP_LENGTH

    part_of_step = (time_in_clip - step_start) / (step_end - step_start)
    left_foot = (step_index - 1) % 2 == 0

    if part_of_step < 0.5:
        if left_foot:
            return 0
        return 2
    return 1


class Monster:
    def __init__(self, textures, walk_sound, tiles, floor_tiles):
        self.textures = textures
        self.tiles = tiles
        self.floor_tiles = floor_tiles

        self.phase_one_frames = []
        self.phase_two_frames = []
        for number in range(4):
            self.phase_one_frames.append(textures["monster_1_walk_" + str(number)])
            self.phase_two_frames.append(textures["monster_2_walk_" + str(number)])

        self.morph_frames = []
        for number in range(3):
            self.morph_frames.append(textures["monster_morph_" + str(number)])

        self.x, self.y = tile_center(MONSTER_START_COLUMN, MONSTER_START_ROW)
        self.state = "follow"
        self.phase = 1
        self.clip_time = 0.0
        self.is_moving = False

        self.target_x = self.x
        self.target_y = self.y
        self.path = []
        self.path_timer = 0.0
        self.roam_timer = 0.0
        self.search_timer = 0.0
        self.lost_timer = 0.0
        self.morph_step = 0
        self.morph_timer = 0.0
        self.sees_player = False

        self.sprite = None
        self.sprites = arcade.SpriteList()
        self.show_texture(self.phase_one_frames[1])

        self.walk_player = play_sound_safe(walk_sound, 0.0, loop=True)

    def show_texture(self, texture):
        if self.sprite is not None and self.sprite.texture.height == texture.height:
            self.sprite.texture = texture
            return

        self.sprites.clear()
        self.sprite = arcade.Sprite(texture, scale=TILE_SCALE)
        self.sprites.append(self.sprite)

    def place_sprite(self):
        self.sprite.center_x = self.x
        self.sprite.center_y = self.y - TILE_SIZE / 2 + self.sprite.height / 2

    def blocked(self, x, y):
        return box_hits_wall(self.tiles, x, y, MONSTER_RADIUS)

    def can_see(self, x, y, max_distance):
        if math.dist((self.x, self.y), (x, y)) > max_distance:
            return False
        return line_is_clear(self.tiles, self.x, self.y, x, y)

    def move_straight(self, target_x, target_y, speed, delta_time):
        difference_x = target_x - self.x
        difference_y = target_y - self.y
        length = math.hypot(difference_x, difference_y)
        if length == 0:
            self.is_moving = False
            return

        distance = speed * delta_time
        if distance > length:
            distance = length

        next_x = self.x + difference_x / length * distance
        next_y = self.y + difference_y / length * distance

        if not self.blocked(next_x, next_y):
            self.x = next_x
            self.y = next_y
            self.is_moving = True
        elif not self.blocked(next_x, self.y):
            self.x = next_x
            self.is_moving = True
        elif not self.blocked(self.x, next_y):
            self.y = next_y
            self.is_moving = True
        else:
            self.is_moving = False

    def set_goal(self, goal_x, goal_y):
        start = (int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))
        goal = (int(goal_x // TILE_SIZE), int(goal_y // TILE_SIZE))
        self.path = find_path(self.tiles, start, goal)

    def refresh_path(self, delta_time, goal_x, goal_y):
        self.path_timer = self.path_timer - delta_time
        if self.path_timer > 0 and len(self.path) > 0:
            return
        self.path_timer = PATH_REFRESH_TIME
        self.set_goal(goal_x, goal_y)

    def shorten_path(self):
        limit = len(self.path)
        if limit > PATH_SHORTCUT_STEPS:
            limit = PATH_SHORTCUT_STEPS

        for index in range(limit - 1, 0, -1):
            column, row = self.path[index]
            x, y = tile_center(column, row)
            if wide_line_is_clear(self.tiles, self.x, self.y, x, y, MONSTER_RADIUS):
                self.path = self.path[index:]
                return

    def walk_along_path(self, speed, delta_time):
        if len(self.path) == 0:
            self.is_moving = False
            return

        self.shorten_path()

        column, row = self.path[0]
        target_x, target_y = tile_center(column, row)
        if math.dist((self.x, self.y), (target_x, target_y)) < WAYPOINT_REACHED:
            self.path.pop(0)
            if len(self.path) == 0:
                self.is_moving = False
                return
            column, row = self.path[0]
            target_x, target_y = tile_center(column, row)

        self.move_straight(target_x, target_y, speed, delta_time)

        if not self.is_moving:
            self.path = []
            self.path_timer = 0.0
            self.roam_timer = 0.0

    def pick_roam_target(self):
        for _ in range(40):
            column, row = random.choice(self.floor_tiles)
            x, y = tile_center(column, row)
            if math.dist((self.x, self.y), (x, y)) < TILE_SIZE * 8:
                continue

            self.set_goal(x, y)
            if len(self.path) > 0:
                self.target_x = x
                self.target_y = y
                self.roam_timer = 45.0
                return

        self.target_x, self.target_y = tile_center(MAP_MIDDLE_COLUMN, MAP_MIDDLE_ROW)
        self.set_goal(self.target_x, self.target_y)
        self.roam_timer = 45.0

    def pick_search_spot(self):
        middle_column = int(self.target_x // TILE_SIZE)
        middle_row = int(self.target_y // TILE_SIZE)

        for _ in range(20):
            column = middle_column + random.randint(-4, 4)
            row = middle_row + random.randint(-4, 4)
            if column < 0 or column >= MAP_COLUMNS:
                continue
            if row < 0 or row >= MAP_ROWS:
                continue
            if self.tiles[row][column] == WALL:
                continue

            self.set_goal(*tile_center(column, row))
            if len(self.path) > 0:
                return

    def start_transform(self):
        self.state = "transform"
        self.morph_step = 0
        self.morph_timer = TRANSFORM_STEP_TIME
        self.show_texture(self.morph_frames[0])

    def alert_to(self, x, y):
        if self.phase != 2:
            return
        if self.state == "chase":
            return
        self.target_x = x
        self.target_y = y
        self.state = "investigate"
        self.search_timer = MONSTER_SEARCH_TIME
        self.set_goal(x, y)
        self.path_timer = PATH_REFRESH_TIME

    def update(self, delta_time, player_x, player_y, player_is_loud):
        self.is_moving = False
        self.sees_player = False

        if self.state == "follow":
            self.update_follow(delta_time, player_x, player_y)
        elif self.state == "transform":
            self.update_transform(delta_time)
        elif self.state == "roam":
            self.update_roam(delta_time, player_x, player_y, player_is_loud)
        elif self.state == "investigate":
            self.update_investigate(delta_time, player_x, player_y, player_is_loud)
        elif self.state == "chase":
            self.update_chase(delta_time, player_x, player_y)

        self.update_animation(delta_time, player_x, player_y)

    def update_follow(self, delta_time, player_x, player_y):
        distance = math.dist((self.x, self.y), (player_x, player_y))

        if distance > MONSTER_FOLLOW_DISTANCE + 10:
            self.refresh_path(delta_time, player_x, player_y)
            self.walk_along_path(MONSTER_FOLLOW_SPEED, delta_time)
        elif distance < MONSTER_FOLLOW_DISTANCE - 10:
            away_x = self.x - (player_x - self.x)
            away_y = self.y - (player_y - self.y)
            self.move_straight(away_x, away_y, MONSTER_FOLLOW_SPEED, delta_time)
            self.path = []
        else:
            self.path = []

    def update_transform(self, delta_time):
        self.morph_timer = self.morph_timer - delta_time
        if self.morph_timer > 0:
            return

        self.morph_step = self.morph_step + 1
        self.morph_timer = TRANSFORM_STEP_TIME

        if self.morph_step < len(self.morph_frames):
            self.show_texture(self.morph_frames[self.morph_step])
            return

        self.phase = 2
        self.x, self.y = tile_center(MAP_MIDDLE_COLUMN, MAP_MIDDLE_ROW)
        self.show_texture(self.phase_two_frames[1])
        self.state = "roam"
        self.pick_roam_target()

    def notice_player(self, player_x, player_y, player_is_loud):
        if self.can_see(player_x, player_y, MONSTER_VIEW_DISTANCE):
            self.sees_player = True
            self.state = "chase"
            self.lost_timer = 0.0
            return True

        if player_is_loud:
            distance = math.dist((self.x, self.y), (player_x, player_y))
            if distance < MONSTER_HEAR_DISTANCE:
                self.target_x = player_x
                self.target_y = player_y
                self.state = "investigate"
                self.search_timer = MONSTER_SEARCH_TIME
                return True

        return False

    def update_roam(self, delta_time, player_x, player_y, player_is_loud):
        if self.notice_player(player_x, player_y, player_is_loud):
            return

        self.roam_timer = self.roam_timer - delta_time
        if len(self.path) == 0 or self.roam_timer <= 0:
            self.pick_roam_target()

        self.walk_along_path(MONSTER_ROAM_SPEED, delta_time)

    def update_investigate(self, delta_time, player_x, player_y, player_is_loud):
        if self.notice_player(player_x, player_y, player_is_loud):
            return

        distance = math.dist((self.x, self.y), (self.target_x, self.target_y))
        if distance > TILE_SIZE:
            self.refresh_path(delta_time, self.target_x, self.target_y)
            self.walk_along_path(MONSTER_SEARCH_SPEED, delta_time)
            return

        self.search_timer = self.search_timer - delta_time
        if self.search_timer <= 0:
            self.state = "roam"
            self.pick_roam_target()
            return

        if len(self.path) == 0:
            self.pick_search_spot()
        self.walk_along_path(MONSTER_ROAM_SPEED, delta_time)

    def update_chase(self, delta_time, player_x, player_y):
        if self.can_see(player_x, player_y, MONSTER_VIEW_DISTANCE * 2):
            self.sees_player = True
            self.lost_timer = 0.0
            self.target_x = player_x
            self.target_y = player_y
        else:
            self.lost_timer = self.lost_timer + delta_time
            if self.lost_timer >= MONSTER_LOST_TIME:
                self.state = "roam"
                self.pick_roam_target()
                return

        self.refresh_path(delta_time, self.target_x, self.target_y)
        self.walk_along_path(MONSTER_CHASE_SPEED, delta_time)

    def update_animation(self, delta_time, player_x, player_y):
        if self.is_moving:
            self.clip_time = self.clip_time + delta_time
            while self.clip_time >= MONSTER_CLIP_LENGTH:
                self.clip_time = self.clip_time - MONSTER_CLIP_LENGTH

        if self.state != "transform":
            frame = monster_frame_for_time(self.clip_time)
            if not self.is_moving:
                frame = 1
            if self.phase == 1:
                self.show_texture(self.phase_one_frames[frame])
            else:
                self.show_texture(self.phase_two_frames[frame])

        self.place_sprite()

        if self.walk_player is not None:
            if not self.is_moving:
                self.walk_player.volume = 0.0
                return
            distance = math.dist((player_x, player_y), (self.x, self.y))
            loudness = 1.0 - distance / MONSTER_SOUND_DISTANCE
            if loudness < 0.0:
                loudness = 0.0
            self.walk_player.volume = loudness * 0.8

    def draw(self):
        self.sprites.draw(pixelated=True)


class YellowLevelGame(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.background_color = arcade.color.BLACK

        texture_paths = make_textures.generate_all()
        self.textures = {}
        for name in texture_paths:
            self.textures[name] = arcade.load_texture(texture_paths[name])

        self.beep_sound = load_sound_file("beep")
        self.made_it_sound = load_sound_file("made_it")
        self.player_walk_sound = load_sound_file("player_walk")
        self.monster_walk_sound = load_sound_file("monster walk")

        self.camera = arcade.camera.Camera2D()
        self.hud_camera = arcade.camera.Camera2D()

        self.task_text = arcade.Text("", 16, WINDOW_HEIGHT - 34, arcade.color.WHITE, 18)
        self.hint_text = arcade.Text("", 16, WINDOW_HEIGHT - 60, (210, 195, 130), 14)
        self.state_text = arcade.Text("", 16, WINDOW_HEIGHT - 84, (200, 120, 120), 14)
        self.puzzle_title = arcade.Text(
            "", PANEL_CENTER_X, PANEL_TOP + 24, arcade.color.WHITE, 20, anchor_x="center"
        )
        self.puzzle_hint = arcade.Text(
            "", PANEL_CENTER_X, PANEL_BOTTOM - 34, (175, 180, 200), 14, anchor_x="center"
        )
        self.speaker_text = arcade.Text("???", 130, 128, (220, 190, 120), 16)
        self.dialogue_text = arcade.Text("", 130, 96, arcade.color.WHITE, 17)
        self.dialogue_more = arcade.Text(
            "LEERTASTE", WINDOW_WIDTH - 150, 60, (150, 150, 170), 13
        )
        self.caught_text = arcade.Text(
            "", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, (240, 90, 90), 30, anchor_x="center"
        )

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.crouching = False

        self.mouse_position = (0, 0)
        self.timer = 0.0
        self.beep_timer = 2.0
        self.task_index = 0
        self.active_puzzle = None
        self.walk_player = None
        self.dialogue_lines = []
        self.dialogue_index = 0
        self.dialogue_after = ""
        self.caught = False
        self.transform_done = False

        self.setup()
        self.start_dialogue(INTRO_LINES, "")

    def setup(self):
        self.tiles = build_map()
        self.floor_tiles = collect_floor_tiles(self.tiles)

        self.floor_sprites = arcade.SpriteList()
        self.wall_sprites = arcade.SpriteList()
        for row in range(MAP_ROWS):
            for column in range(MAP_COLUMNS):
                if self.tiles[row][column] == WALL:
                    sprite = arcade.Sprite(self.textures["wall"], scale=TILE_SCALE)
                    sprite.position = tile_center(column, row)
                    self.wall_sprites.append(sprite)
                else:
                    sprite = arcade.Sprite(self.textures["floor"], scale=TILE_SCALE)
                    sprite.position = tile_center(column, row)
                    self.floor_sprites.append(sprite)

        self.station_sprites = arcade.SpriteList()
        for name, kind, column, row in TASKS:
            sprite = arcade.Sprite(self.textures["station"], scale=TILE_SCALE)
            sprite.position = tile_center(column, row)
            self.station_sprites.append(sprite)

        self.player = arcade.Sprite(self.textures["player"], scale=TILE_SCALE)
        self.player.position = tile_center(START_COLUMN, START_ROW)
        self.player_sprites = arcade.SpriteList()
        self.player_sprites.append(self.player)

        self.monster = Monster(
            self.textures, self.monster_walk_sound, self.tiles, self.floor_tiles
        )

        self.darkness = arcade.Sprite(self.textures["darkness"], scale=DARKNESS_SCALE)
        self.darkness_sprites = arcade.SpriteList()
        self.darkness_sprites.append(self.darkness)

        self.minimap = arcade.Sprite(self.build_minimap_texture(), scale=MINIMAP_SCALE)
        self.minimap.center_x = MINIMAP_LEFT + MINIMAP_WIDTH / 2
        self.minimap.center_y = MINIMAP_BOTTOM + MINIMAP_HEIGHT / 2
        self.minimap_sprites = arcade.SpriteList()
        self.minimap_sprites.append(self.minimap)

        self.camera.position = self.player.position

    def build_minimap_texture(self):
        image = Image.new("RGBA", (MAP_COLUMNS, MAP_ROWS))
        for row in range(MAP_ROWS):
            for column in range(MAP_COLUMNS):
                if self.tiles[row][column] == WALL:
                    color = (92, 80, 44, 230)
                else:
                    color = (176, 162, 112, 230)
                image.putpixel((column, MAP_ROWS - 1 - row), color)

        path = ASSETS_FOLDER / "minimap.png"
        image.save(path)
        return arcade.load_texture(path)

    def start_dialogue(self, lines, after):
        self.dialogue_lines = lines
        self.dialogue_index = 0
        self.dialogue_after = after

    def advance_dialogue(self):
        self.dialogue_index = self.dialogue_index + 1
        if self.dialogue_index < len(self.dialogue_lines):
            return

        self.dialogue_lines = []
        self.dialogue_index = 0
        if self.dialogue_after == "transform":
            self.monster.start_transform()
            self.transform_done = True
        self.dialogue_after = ""

    def dialogue_is_open(self):
        return len(self.dialogue_lines) > 0

    def current_task(self):
        if self.task_index >= len(TASKS):
            return None
        return TASKS[self.task_index]

    def distance_to_task(self):
        task = self.current_task()
        if task is None:
            return None
        target = tile_center(task[2], task[3])
        return math.dist(self.player.position, target)

    def hits_wall(self, x, y):
        return box_hits_wall(self.tiles, x, y, PLAYER_RADIUS)

    def on_update(self, delta_time):
        self.timer = self.timer + delta_time

        if self.caught:
            self.stop_walk_sound()
            return

        player_is_loud = False

        if self.active_puzzle is None:
            player_is_loud = self.move_player(delta_time)
            self.update_beep(delta_time)
        else:
            self.active_puzzle.update(delta_time)
            self.stop_walk_sound()
            if self.active_puzzle.solved:
                self.finish_task()

        self.monster.update(delta_time, self.player.center_x, self.player.center_y, player_is_loud)

        if self.monster.phase == 2:
            distance = math.dist(self.player.position, (self.monster.x, self.monster.y))
            if distance < MONSTER_CATCH_DISTANCE:
                self.get_caught()

        self.update_texts()

    def move_player(self, delta_time):
        move_x = 0.0
        move_y = 0.0

        if self.left_pressed:
            move_x = move_x - 1.0
        if self.right_pressed:
            move_x = move_x + 1.0
        if self.down_pressed:
            move_y = move_y - 1.0
        if self.up_pressed:
            move_y = move_y + 1.0

        if move_x != 0.0 and move_y != 0.0:
            move_x = move_x * 0.7071
            move_y = move_y * 0.7071

        if self.crouching:
            speed = PLAYER_CROUCH_SPEED
        else:
            speed = PLAYER_WALK_SPEED

        distance = speed * delta_time

        next_x = self.player.center_x + move_x * distance
        if not self.hits_wall(next_x, self.player.center_y):
            self.player.center_x = next_x

        next_y = self.player.center_y + move_y * distance
        if not self.hits_wall(self.player.center_x, next_y):
            self.player.center_y = next_y

        is_walking = move_x != 0.0 or move_y != 0.0
        if is_walking:
            self.start_walk_sound()
        else:
            self.stop_walk_sound()

        if self.crouching:
            self.player.texture = self.textures["player_crouch"]
        else:
            self.player.texture = self.textures["player"]

        self.follow_with_camera()
        return is_walking and not self.crouching

    def follow_with_camera(self):
        half_width = self.width / 2
        half_height = self.height / 2

        target_x = self.player.center_x
        if target_x < half_width:
            target_x = half_width
        if target_x > MAP_WIDTH - half_width:
            target_x = MAP_WIDTH - half_width

        target_y = self.player.center_y
        if target_y < half_height:
            target_y = half_height
        if target_y > MAP_HEIGHT - half_height:
            target_y = MAP_HEIGHT - half_height

        camera_x, camera_y = self.camera.position
        camera_x = camera_x + (target_x - camera_x) * CAMERA_FOLLOW
        camera_y = camera_y + (target_y - camera_y) * CAMERA_FOLLOW
        self.camera.position = (camera_x, camera_y)

    def start_walk_sound(self):
        if self.walk_player is None:
            if self.crouching:
                volume = 0.15
            else:
                volume = 0.4
            self.walk_player = play_sound_safe(self.player_walk_sound, volume, loop=True)

    def stop_walk_sound(self):
        if self.walk_player is not None:
            arcade.stop_sound(self.walk_player)
            self.walk_player = None

    def update_beep(self, delta_time):
        distance = self.distance_to_task()
        if distance is None:
            return

        self.beep_timer = self.beep_timer - delta_time
        if self.beep_timer > 0:
            return

        nearness = distance / BEEP_MAX_DISTANCE
        if nearness > 1.0:
            nearness = 1.0

        self.beep_timer = BEEP_NEAR_DELAY + (BEEP_FAR_DELAY - BEEP_NEAR_DELAY) * nearness
        play_sound_safe(self.beep_sound, 0.2 + 0.3 * (1.0 - nearness))

    def update_texts(self):
        task = self.current_task()

        if task is None:
            self.task_text.text = "Alle Aufgaben erledigt!"
            self.hint_text.text = "Aber der Ausgang ist nicht da, wo du ihn vermutest."
        else:
            self.task_text.text = (
                "Aufgabe " + str(self.task_index + 1) + "/" + str(len(TASKS))
                + ": " + TASK_NAMES[task[1]] + " - " + task[0]
            )

            if self.active_puzzle is not None:
                self.hint_text.text = "ESC = Konsole schliessen"
            elif self.distance_to_task() < REACH_DISTANCE:
                self.hint_text.text = "E = Konsole benutzen"
            elif self.crouching:
                self.hint_text.text = "Du schleichst. Er hoert dich nicht."
            else:
                self.hint_text.text = "SHIFT = schleichen (er hoert deine Schritte 500 px weit)"

        if self.monster.phase == 1:
            self.state_text.text = ""
        elif self.monster.state == "chase":
            self.state_text.text = "ER HAT DICH GESEHEN"
        elif self.monster.state == "investigate":
            self.state_text.text = "Er sucht dich."
        else:
            self.state_text.text = "Er streift umher."

    def on_draw(self):
        self.clear()

        self.camera.use()
        self.floor_sprites.draw(pixelated=True)
        self.wall_sprites.draw(pixelated=True)
        self.station_sprites.draw(pixelated=True)
        self.monster.draw()
        self.player_sprites.draw(pixelated=True)

        self.darkness.position = self.player.position
        self.darkness_sprites.draw()

        self.hud_camera.use()
        self.draw_minimap()
        self.task_text.draw()
        self.hint_text.draw()
        self.state_text.draw()

        if self.active_puzzle is not None:
            arcade.draw_lrbt_rectangle_filled(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, (0, 0, 0, 190))
            self.active_puzzle.draw()
            self.puzzle_title.text = self.active_puzzle.title
            self.puzzle_hint.text = self.active_puzzle.hint
            self.puzzle_title.draw()
            self.puzzle_hint.draw()

        if self.dialogue_is_open():
            self.draw_dialogue()

        if self.caught:
            self.draw_caught()

    def draw_dialogue(self):
        arcade.draw_lrbt_rectangle_filled(100, WINDOW_WIDTH - 100, 40, 170, (14, 12, 18, 235))
        arcade.draw_lrbt_rectangle_filled(104, WINDOW_WIDTH - 104, 44, 166, (40, 34, 30, 235))

        self.dialogue_text.text = self.dialogue_lines[self.dialogue_index]
        self.speaker_text.draw()
        self.dialogue_text.draw()
        self.dialogue_more.draw()

    def draw_caught(self):
        arcade.draw_lrbt_rectangle_filled(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, (30, 0, 0, 200))
        self.caught_text.text = "Er hat dich erwischt.   R = weiter"
        self.caught_text.draw()

    def draw_minimap(self):
        arcade.draw_lrbt_rectangle_filled(
            MINIMAP_LEFT - 6, MINIMAP_LEFT + MINIMAP_WIDTH + 6,
            MINIMAP_BOTTOM - 6, MINIMAP_BOTTOM + MINIMAP_HEIGHT + 6,
            (16, 14, 22, 230),
        )
        self.minimap_sprites.draw(pixelated=True)

        for index in range(len(TASKS)):
            column = TASKS[index][2]
            row = TASKS[index][3]
            spot_x = MINIMAP_LEFT + (column + 0.5) * MINIMAP_SCALE
            spot_y = MINIMAP_BOTTOM + (row + 0.5) * MINIMAP_SCALE

            if index < self.task_index:
                arcade.draw_circle_filled(spot_x, spot_y, 3, (60, 180, 90))
            elif index == self.task_index:
                if int(self.timer * 4) % 2 == 0:
                    arcade.draw_circle_filled(spot_x, spot_y, 5, (255, 50, 50))
            else:
                arcade.draw_circle_filled(spot_x, spot_y, 3, (120, 90, 40))

        player_x = MINIMAP_LEFT + self.player.center_x / TILE_SIZE * MINIMAP_SCALE
        player_y = MINIMAP_BOTTOM + self.player.center_y / TILE_SIZE * MINIMAP_SCALE
        arcade.draw_circle_filled(player_x, player_y, 4, arcade.color.WHITE)

    def open_puzzle(self):
        task = self.current_task()
        if task is None:
            return
        if self.distance_to_task() >= REACH_DISTANCE:
            return

        if self.task_index == TRANSFORM_TASK_INDEX and not self.transform_done:
            self.start_dialogue(TRANSFORM_LINES, "transform")
            return

        self.active_puzzle = PUZZLE_CLASSES[task[1]](self.textures)

    def finish_task(self):
        task = TASKS[self.task_index]
        self.station_sprites[self.task_index].texture = self.textures["station_done"]
        self.task_index = self.task_index + 1
        self.active_puzzle = None
        self.beep_timer = 2.0
        play_sound_safe(self.made_it_sound, 0.6)

        alert_x, alert_y = tile_center(task[2], task[3])
        self.monster.alert_to(alert_x, alert_y)

    def get_caught(self):
        self.caught = True
        self.active_puzzle = None
        self.stop_walk_sound()

    def restart_after_caught(self):
        self.caught = False
        self.player.position = tile_center(START_COLUMN, START_ROW)
        self.camera.position = self.player.position
        self.monster.x, self.monster.y = tile_center(MAP_MIDDLE_COLUMN, MAP_MIDDLE_ROW)
        self.monster.state = "roam"
        self.monster.pick_roam_target()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position = (x, y)
        if self.active_puzzle is not None:
            self.active_puzzle.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.active_puzzle is None:
            return

        good_click = self.active_puzzle.on_mouse_press(x, y)
        if good_click and not self.active_puzzle.solved:
            play_sound_safe(self.beep_sound, 0.3)
        if self.active_puzzle.solved:
            self.finish_task()

    def on_mouse_release(self, x, y, button, modifiers):
        if self.active_puzzle is not None:
            self.active_puzzle.on_mouse_release()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.active_puzzle is None:
                self.close()
            else:
                self.active_puzzle = None
        elif key == arcade.key.SPACE:
            if self.dialogue_is_open():
                self.advance_dialogue()
        elif key == arcade.key.R:
            if self.caught:
                self.restart_after_caught()
        elif key == arcade.key.E:
            if self.active_puzzle is None and not self.dialogue_is_open():
                self.open_puzzle()
        elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.crouching = True
            self.stop_walk_sound()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.crouching = False
            self.stop_walk_sound()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False


def main():
    YellowLevelGame()
    arcade.run()


if __name__ == "__main__":
    main()
