import arcade
import random
from pathlib import Path

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Procedural Supermarket Generation (No Walls)"

TILE_SIZE = 64
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Get directory where this script is located
BASE_DIR = Path(__file__).parent

# Build absolute paths to textures
FLOOR_TEXTURE = BASE_DIR / "t..png"
SHELF_TEXTURE = BASE_DIR / "s..png"


class SupermarketGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.shelf_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()

    def setup(self):
        self.shelf_list.clear()
        self.floor_list.clear()

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                floor = arcade.Sprite(str(FLOOR_TEXTURE), scale=TILE_SIZE / 64)
                floor.center_x = x * TILE_SIZE + TILE_SIZE // 2
                floor.center_y = y * TILE_SIZE + TILE_SIZE // 2
                self.floor_list.append(floor)

        aisle_spacing = 3
        for x in range(2, GRID_WIDTH - 2, aisle_spacing):
            for y in range(2, GRID_HEIGHT - 2):
                if random.random() > 0.1:
                    shelf = arcade.Sprite(str(SHELF_TEXTURE), scale=TILE_SIZE / 64)
                    shelf.center_x = x * TILE_SIZE + TILE_SIZE // 0.5
                    shelf.center_y = y * TILE_SIZE + TILE_SIZE // 0.5
                    
                    self.shelf_list.append(shelf)

    def on_draw(self):
        arcade.start_render
        self.floor_list.draw()
        self.shelf_list.draw()


def main():
    game = SupermarketGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
