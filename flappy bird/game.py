import arcade, random

W, H = 400, 600
GAP = 160

class Game(arcade.Window):
    def __init__(self):
        super().__init__(W, H, "Flappy")
        self.bird = arcade.Sprite("bird.png", center_x=80, center_y=H / 2)
        self.reset()

    def reset(self):
        self.bird.center_y = H / 2
        self.vy = 0
        self.pipes = arcade.SpriteList()
        for i in range(3):
            self.spawn(W + i * 220)

    def spawn(self, x):
        y = random.randint(120, H - 120)
        bottom = arcade.Sprite("pipe.png", center_x=x)
        bottom.top = y - GAP / 2
        top = arcade.Sprite("pipe.png", center_x=x, flipped_vertically=True)
        top.bottom = y + GAP / 2
        self.pipes.append(bottom)
        self.pipes.append(top)

    def on_key_press(self, key, mod):
        if key == arcade.key.SPACE:
            self.vy = 7

    def on_update(self, dt):
        self.vy -= 0.4
        self.bird.center_y += self.vy
        self.pipes.move(-3, 0)
        if self.pipes[0].right < 0:
            for _ in range(2):
                self.pipes.pop(0)
            self.spawn(self.pipes[-1].center_x + 220)
        if self.bird.top < 0 or self.bird.bottom > H or self.bird.collides_with_list(self.pipes):
            self.reset()

    def on_draw(self):
        self.clear(arcade.color.SKY_BLUE)
        self.pipes.draw()
        arcade.draw_sprite(self.bird)

Game()
arcade.run()
