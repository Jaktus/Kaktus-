import arcade
import random

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Procedural Supermarket Generation (No Walls)"

CELL_WIDTH = 20
CELL_HEIGHT = 20
SHELF_TILE = '-'
EMPTY_TILE = '.'

BASE_LAYOUT_TEXT = '''
----------              ----------
  -  .     -              -  .  .  -
  -        -              -        -
  ----------              ----------
  .  .  .  .  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .  .  .  .  .
                  ----------
                  -        -
                  -     .  -
                  ----------
  .  .  .  .  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .  .  .  .  .
  ----------
  -     .  -              ----------
  -  .     -              -  .  .  -
  ----------
'''


def parse_base_layout(text):
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    grid = []
    max_len = 0
    for line in lines:
        row = ''.join(c for c in line if c in (SHELF_TILE, EMPTY_TILE))
        max_len = max(max_len, len(row))
        grid.append(row)
    # Padding to square/rectangular
    return [row.ljust(max_len, EMPTY_TILE) for row in grid]


def generate_supermarket_layout(remove_probability=0.2):
    base = parse_base_layout(BASE_LAYOUT_TEXT)
    grid = []
    for row in base:
        new_row = ''.join(
            EMPTY_TILE if c == SHELF_TILE and random.random() < remove_probability else c
            for c in row
        )
        grid.append(new_row)
    return grid


def layout_to_ascii(grid):
    return '\n'.join(' '.join(char for char in row) for row in grid)


class SupermarketGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.shelf_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.layout = []

    def setup(self):
        self.shelf_list.clear()
        self.floor_list.clear()

        # Layout aus vorgegebenem Grundriss + einige zufällige Regale entfernt
        self.layout = generate_supermarket_layout(remove_probability=0.22)

        # Konsolenausgabe
        print("\n=== Zufälliges Supermarkt-Layout ===")
        print(layout_to_ascii(self.layout))

        # Sprite-Grid aus Layout erzeugen
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                x = 50 + col_index * (CELL_WIDTH + 5)
                y = SCREEN_HEIGHT - 50 - row_index * (CELL_HEIGHT + 5)

                if tile == SHELF_TILE:
                    shelf = arcade.SpriteSolidColor(CELL_WIDTH, CELL_HEIGHT, arcade.color.BROWN)
                    shelf.center_x = x
                    shelf.center_y = y
                    self.shelf_list.append(shelf)
                else:
                    floor = arcade.SpriteSolidColor(CELL_WIDTH, CELL_HEIGHT, arcade.color.LIGHT_GRAY)
                    floor.center_x = x
                    floor.center_y = y
                    self.floor_list.append(floor)

    def on_update(self, delta_time):
        # Keine wiederholte Neugenerierung pro Frame
        pass

    def on_draw(self):
        self.clear()
        self.floor_list.draw()
        self.shelf_list.draw()


def main():
    game = SupermarketGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
