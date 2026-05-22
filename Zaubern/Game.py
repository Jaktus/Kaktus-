import arcade

# Konstanten
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Frog Jumper"

class FrogJumper(arcade.Window):
	def __init__(self):
		super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
		self.frog_sprite = None
		self.all_sprites = arcade.SpriteList()
		self.platforms = arcade.SpriteList()
		self.frog_speed_y = 0
		self.frog_speed_x = 0
		self.gravity = 0.5
		self.jump_speed = 15
		self.move_speed = 5
		self.on_ground = True

	def setup(self):
		# Frosch-Sprite laden (einfacher grüner Kreis als Platzhalter)
		self.frog_sprite = arcade.SpriteSolidColor(20, 20, arcade.color.GREEN)
		self.frog_sprite.center_x = SCREEN_WIDTH // 2
		self.frog_sprite.center_y = 100
		self.all_sprites.append(self.frog_sprite)

		# Plattformen erstellen
		platform1 = arcade.SpriteSolidColor(100, 20, arcade.color.BROWN)
		platform1.center_x = 300
		platform1.center_y = 200
		self.platforms.append(platform1)
		self.all_sprites.append(platform1)

		platform2 = arcade.SpriteSolidColor(100, 20, arcade.color.BROWN)
		platform2.center_x = 500
		platform2.center_y = 300
		self.platforms.append(platform2)
		self.all_sprites.append(platform2)

	def on_draw(self):
		arcade.start_render()
		self.all_sprites.draw()

	def update(self, delta_time):
		# Horizontale Bewegung
		self.frog_sprite.center_x += self.frog_speed_x

		# Gravitation anwenden
		self.frog_speed_y -= self.gravity
		self.frog_sprite.center_y += self.frog_speed_y

		# Kollision mit Plattformen
		hit_list = arcade.check_for_collision_with_list(self.frog_sprite, self.platforms)
		if hit_list and self.frog_speed_y < 0:
			# Landen auf Plattform
			self.frog_sprite.center_y = hit_list[0].center_y + hit_list[0].height // 2 + self.frog_sprite.height // 2
			self.frog_speed_y = 0
			self.on_ground = True

		# Boden-Kollision
		if self.frog_sprite.center_y <= 100:
			self.frog_sprite.center_y = 100
			self.frog_speed_y = 0
			self.on_ground = True

	def on_key_press(self, key, modifiers):
		if key == arcade.key.SPACE and self.on_ground:
			self.frog_speed_y = self.jump_speed
			self.on_ground = False
		elif key == arcade.key.LEFT:
			self.frog_speed_x = -self.move_speed
		elif key == arcade.key.RIGHT:
			self.frog_speed_x = self.move_speed

	def on_key_release(self, key, modifiers):
		if key == arcade.key.LEFT or key == arcade.key.RIGHT:
			self.frog_speed_x = 0

def main():
	window = FrogJumper()
	window.setup()
	arcade.run()

