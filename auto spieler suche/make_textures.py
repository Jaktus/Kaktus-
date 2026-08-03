import math
from pathlib import Path

from PIL import Image

TEXTURE_SIZE = 16
ASSETS_FOLDER = Path(__file__).parent / "assets"

DARKNESS_SIZE = 256
DARKNESS_CLEAR_RADIUS = 18
DARKNESS_DARK_RADIUS = 52
DARKNESS_MAX_ALPHA = 228

COLORS = {
    ".": (0, 0, 0, 0),

    "W": (240, 226, 156, 255),
    "Y": (226, 208, 128, 255),
    "y": (204, 184, 104, 255),
    "o": (172, 152, 80, 255),
    "b": (140, 120, 60, 255),

    "c": (128, 118, 86, 255),
    "C": (140, 130, 96, 255),
    "d": (114, 104, 74, 255),

    "k": (26, 22, 32, 255),
    "R": (92, 60, 40, 255),
    "N": (236, 186, 146, 255),
    "E": (30, 26, 36, 255),
    "B": (74, 134, 208, 255),
    "L": (48, 96, 168, 255),
    "P": (86, 62, 48, 255),
    "O": (54, 42, 36, 255),

    "X": (32, 14, 20, 255),
    "H": (232, 214, 186, 255),
    "A": (198, 58, 58, 255),
    "V": (142, 34, 42, 255),
    "I": (236, 116, 96, 255),
    "e": (244, 244, 244, 255),
    "z": (28, 18, 22, 255),

    "p": (206, 200, 192, 255),
    "s": (158, 152, 148, 255),
    "m": (198, 130, 118, 255),
    "n": (150, 92, 88, 255),
    "h": (10, 8, 12, 255),
    "t": (240, 238, 232, 255),
    "r": (90, 20, 26, 255),

    "T": (198, 202, 214, 255),
    "U": (146, 152, 168, 255),
    "Q": (242, 248, 255, 255),
    "1": (110, 240, 150, 255),
    "2": (38, 128, 78, 255),
    "3": (255, 146, 112, 255),
    "4": (152, 46, 40, 255),
}

WALL_ART = [
    "bbbbbbbbbbbbbbbb",
    "WWWoYYYoWWWoYYYo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "YYYoyyyoYYYoyyyo",
    "bbbbbbbbbbbbbbbb",
]

FLOOR_ART = [
    "ccCcccdccCcccccd",
    "cccccCccdcccCccc",
    "cdcccccccCcccccc",
    "cccCcdcccccccCcc",
    "CcccccccdcccccCc",
    "cccdcccCcccccccc",
    "ccccccccccCcdccc",
    "cCccdcccccccccCc",
    "cccccccCcdcccccc",
    "dcccCccccccdcccc",
    "ccccccccCccccdcc",
    "ccCcdccccccCcccc",
    "cccccccccdccCccc",
    "cCcccccCcccccccd",
    "ccccdcccccCccccc",
    "cccccccccccdcCcc",
]

PLAYER_ART = [
    "................",
    "................",
    "....kkkkkkkk....",
    "...kRRRRRRRRk...",
    "...kRRRRRRRRk...",
    "...kNNNNNNNNk...",
    "...kNENNNNENk...",
    "...kNNNNNNNNk...",
    "....kNNNNNNNk...",
    "..kkBBBBBBBBkk..",
    "..kNBBBBBBBBNk..",
    "..kNBBLLLLBBNk..",
    "...kBBBBBBBBk...",
    "...kPPPPPPPPk...",
    "...kPPP..PPPk...",
    "...kOO....OOk...",
]

PLAYER_CROUCH_ART = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "....kkkkkkkk....",
    "...kRRRRRRRRk...",
    "...kNENNNNENk...",
    "...kNNNNNNNNk...",
    "..kkBBBBBBBBkk..",
    "..kNBBBBBBBBNk..",
    "..kNBBLLLLBBNk..",
    "...kBBBBBBBBk...",
    "...kPPPPPPPPk...",
    "...kPPPPPPPPk...",
    "...kOOOOOOOOk...",
]

CARD_ART = [
    "................",
    "................",
    "................",
    "...kkkkkkkkkk...",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQkkkkkkkkQk..",
    "..kQkkkkkkkkQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "...kkkkkkkkkk...",
    "................",
    "................",
    "................",
]

MONSTER_ONE_HEAD = [
    "..X..........X..",
    "..XHX......XHX..",
    "...XXXAAAAXXX...",
    "...XAAAAAAAAX...",
    "..XAAeeAAeeAAX..",
    "..XAAzzAAzzAAX..",
    "..XAAAVVVVAAAX..",
    "...XAAAAAAAAX...",
]

MONSTER_ONE_BODY = [
    "..XXAAAAAAAAXX..",
    "..XAXAAAAAAXAX..",
    "..XAXAAAAAAXAX..",
    "...XXAAAAAAXX...",
]

MONSTER_ONE_LEGS_STEP = [
    "...XAAX..XAAX...",
    "..XAAX...XAAX...",
    "..XAAX....XAX...",
    ".XXXX.......XX..",
]

MONSTER_ONE_LEGS_PASS = [
    "...XAAX..XAAX...",
    "...XAAX..XAAX...",
    "....XAX..XAX....",
    "...XXX...XXX....",
]

MONSTER_TWO_HEAD = [
    ".....kkkkkk.....",
    "....kppppppk....",
    "....kppppppk....",
    "....kppppppk....",
    "....khhpphhk....",
    "....khtppthk....",
    "....khhpphhk....",
    "....kppppppk....",
    "....kppppppk....",
    "....kprrrrpk....",
    "....kptrtrpk....",
    "....kprtrtpk....",
    "....kprrrrpk....",
    "....kkppppkk....",
]

MONSTER_TWO_BODY = [
    ".....kppppk.....",
    ".....kppppk.....",
    "..kksppppppskk..",
    "..kskppppppksk..",
    "..kskpsppspksk..",
    "..kskppppppksk..",
    "..kskpsppspksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "..kskppppppksk..",
    "....kppppppk....",
    "....kppppppk....",
    "....kppppppk....",
    "...kkppppppkk...",
    "...kkppppppkk...",
]

MONSTER_TWO_LEGS_STEP = [
    "...kppk..kppk...",
    "...kppk..kppk...",
    "..kppk...kppk...",
    "..kppk...kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    ".kppk....kppk...",
    "kkkkkk..kkkkkk..",
]

MONSTER_TWO_LEGS_PASS = [
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "...kppk..kppk...",
    "..kkkkk..kkkkk..",
]

STATION_ART = [
    "................",
    "................",
    "..kkkkkkkkkkkk..",
    "..kUUUUUUUUUUk..",
    "..kU22222222Uk..",
    "..kU21111112Uk..",
    "..kU21111112Uk..",
    "..kU21111112Uk..",
    "..kU22222222Uk..",
    "..kUUUUUUUUUUk..",
    "..kkkkkkkkkkkk..",
    "....kUUUUUUk....",
    "....kUUUUUUk....",
    "..kkkkkkkkkkkk..",
    "..kUUUUUUUUUUk..",
    "..kkkkkkkkkkkk..",
]

PLUG_ART = [
    "................",
    "................",
    "...kkkkkkkkkk...",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "..kQQQQQQQQQQk..",
    "...kkkkkkkkkk...",
    "................",
    "................",
]

DIGIT_ART = {
    1: [".#.", "##.", ".#.", ".#.", "###"],
    2: ["###", "..#", "###", "#..", "###"],
    3: ["###", "..#", "###", "..#", "###"],
    4: ["#.#", "#.#", "###", "..#", "..#"],
    5: ["###", "#..", "###", "..#", "###"],
    6: ["###", "#..", "###", "#.#", "###"],
}


def mirror_art(art):
    mirrored = []
    for art_row in art:
        mirrored.append(art_row[::-1])
    return mirrored


def make_walk_frames(head, body, legs_step, legs_pass):
    frames = []
    frames.append(head + body + legs_step)
    frames.append(head + body + legs_pass)
    frames.append(head + body + mirror_art(legs_step))
    frames.append(head + body + legs_pass)
    return frames


MORPH_TO_RED = {"p": "A", "s": "V", "k": "X", "h": "z", "r": "V", "t": "e"}
MORPH_TO_MIX = {"p": "m", "s": "n"}


def recolor_art(art, replacements):
    new_art = []
    for art_row in art:
        new_row = ""
        for symbol in art_row:
            if symbol in replacements:
                new_row = new_row + replacements[symbol]
            else:
                new_row = new_row + symbol
        new_art.append(new_row)
    return new_art


def make_morph_frames():
    head = MONSTER_TWO_HEAD
    body = MONSTER_TWO_BODY
    legs = MONSTER_TWO_LEGS_PASS

    short = head + body[0:6] + legs[-4:]
    middle = head + body[0:10] + legs[-8:]
    tall = head + body[0:14] + legs[-12:]

    frames = []
    frames.append(recolor_art(short, MORPH_TO_RED))
    frames.append(recolor_art(middle, MORPH_TO_MIX))
    frames.append(tall)
    return frames


def make_station_done_art():
    done_art = []
    for art_row in STATION_ART:
        new_row = ""
        for symbol in art_row:
            if symbol == "3":
                new_row = new_row + "1"
            elif symbol == "4":
                new_row = new_row + "2"
            else:
                new_row = new_row + symbol
        done_art.append(new_row)
    return done_art


def make_station_open_art():
    open_art = []
    for art_row in STATION_ART:
        new_row = ""
        for symbol in art_row:
            if symbol == "1":
                new_row = new_row + "3"
            elif symbol == "2":
                new_row = new_row + "4"
            else:
                new_row = new_row + symbol
        open_art.append(new_row)
    return open_art


def make_number_art(digit):
    grid = []
    for y in range(TEXTURE_SIZE):
        row = []
        for x in range(TEXTURE_SIZE):
            on_outer_edge = x == 0 or y == 0 or x == TEXTURE_SIZE - 1 or y == TEXTURE_SIZE - 1
            on_inner_edge = x == 1 or y == 1 or x == TEXTURE_SIZE - 2 or y == TEXTURE_SIZE - 2
            if on_outer_edge:
                row.append("k")
            elif on_inner_edge:
                row.append("T")
            else:
                row.append("U")
        grid.append(row)

    digit_rows = DIGIT_ART[digit]
    for digit_y in range(len(digit_rows)):
        for digit_x in range(len(digit_rows[digit_y])):
            if digit_rows[digit_y][digit_x] == "#":
                for inside_y in range(2):
                    for inside_x in range(2):
                        grid[3 + digit_y * 2 + inside_y][5 + digit_x * 2 + inside_x] = "Q"

    art = []
    for row in grid:
        art.append("".join(row))
    return art


def save_texture(name, art):
    height = len(art)
    width = len(art[0])
    image = Image.new("RGBA", (width, height))

    for y in range(height):
        if len(art[y]) != width:
            raise ValueError(name + ": Zeile " + str(y) + " ist unterschiedlich lang")
        for x in range(width):
            symbol = art[y][x]
            image.putpixel((x, y), COLORS[symbol])

    path = ASSETS_FOLDER / (name + ".png")
    image.save(path)
    return path


def save_darkness():
    center = DARKNESS_SIZE / 2
    image = Image.new("RGBA", (DARKNESS_SIZE, DARKNESS_SIZE))

    for y in range(DARKNESS_SIZE):
        for x in range(DARKNESS_SIZE):
            distance = math.hypot(x + 0.5 - center, y + 0.5 - center)
            if distance <= DARKNESS_CLEAR_RADIUS:
                alpha = 0
            elif distance >= DARKNESS_DARK_RADIUS:
                alpha = DARKNESS_MAX_ALPHA
            else:
                span = DARKNESS_DARK_RADIUS - DARKNESS_CLEAR_RADIUS
                fade = (distance - DARKNESS_CLEAR_RADIUS) / span
                alpha = int(fade * DARKNESS_MAX_ALPHA)
            image.putpixel((x, y), (0, 0, 0, alpha))

    path = ASSETS_FOLDER / "darkness.png"
    image.save(path)
    return path


def generate_all():
    ASSETS_FOLDER.mkdir(exist_ok=True)
    paths = {}

    paths["wall"] = save_texture("wall", WALL_ART)
    paths["floor"] = save_texture("floor", FLOOR_ART)
    paths["player"] = save_texture("player", PLAYER_ART)
    paths["player_crouch"] = save_texture("player_crouch", PLAYER_CROUCH_ART)
    paths["card"] = save_texture("card", CARD_ART)

    morph_frames = make_morph_frames()
    for number in range(len(morph_frames)):
        name = "monster_morph_" + str(number)
        paths[name] = save_texture(name, morph_frames[number])
    monster_one_frames = make_walk_frames(
        MONSTER_ONE_HEAD, MONSTER_ONE_BODY, MONSTER_ONE_LEGS_STEP, MONSTER_ONE_LEGS_PASS
    )
    monster_two_frames = make_walk_frames(
        MONSTER_TWO_HEAD, MONSTER_TWO_BODY, MONSTER_TWO_LEGS_STEP, MONSTER_TWO_LEGS_PASS
    )

    for number in range(len(monster_one_frames)):
        name = "monster_1_walk_" + str(number)
        paths[name] = save_texture(name, monster_one_frames[number])

    for number in range(len(monster_two_frames)):
        name = "monster_2_walk_" + str(number)
        paths[name] = save_texture(name, monster_two_frames[number])
    paths["station"] = save_texture("station", make_station_open_art())
    paths["station_done"] = save_texture("station_done", make_station_done_art())
    paths["plug"] = save_texture("plug", PLUG_ART)

    for digit in DIGIT_ART:
        name = "number_" + str(digit)
        paths[name] = save_texture(name, make_number_art(digit))

    paths["darkness"] = save_darkness()
    return paths


if __name__ == "__main__":
    for name, path in generate_all().items():
        print(name, "->", path)
