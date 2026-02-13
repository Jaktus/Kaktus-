import arcade
import time
import random
import math

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800
SCREEN_TITLE = "td"

class Balloon(arcade.Sprite):
    def __init__(self):
        super().__init__("btballon.png")
        self.center_x = 75
        self.center_y = 770
        self.change_y = -1
        self.spawn_time = time.time()
        self.hp = 20

class Bullet(arcade.Sprite):
    def __init__(self, texture, speed, dx, dy, damage, pierce, lifetime):
        super().__init__(texture, 0.6)
        self.change_x = dx * speed
        self.change_y = dy * speed
        self.damage = damage
        self.pierce = pierce
        self.lifetime = lifetime
        self.spawn_time = time.time()

class Tower(arcade.Sprite):
    def __init__(self, texture, level, tower_type, cost, shoot_speed):
        super().__init__(texture, 1)
        self.level = level
        self.tower_type = tower_type
        self.cost = cost
        self.shoot_speed = shoot_speed
        self.last_shot = 0

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.blist = arcade.SpriteList()
        self.tower_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.money = 1000
        self.start_time = time.time()
        self.spawn_rate = 100

    def spawn_balloon(self):
        if random.randint(1, self.spawn_rate) == 1:
            self.blist.append(Balloon())

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.money >= 300:
            tower = Tower("norm_lvl_1.png", 1, "norm", 300, 1)
            tower.center_x = x
            tower.center_y = y
            self.money -= 300
            self.tower_list.append(tower)

        elif button == arcade.MOUSE_BUTTON_RIGHT and self.money >= 500:
            tower = Tower("tack_lvl_1.png", 1, "tack", 500, 1)
            tower.center_x = x
            tower.center_y = y
            self.money -= 500
            self.tower_list.append(tower)

    def shoot_norm(self, tower):
        if len(self.blist) == 0:
            return

        target = min(self.blist, key=lambda b: arcade.get_distance_between_sprites(tower, b))
        dx = target.center_x - tower.center_x
        dy = target.center_y - tower.center_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx /= dist
        dy /= dist

        if tower.level == 1:
            bullet = Bullet("red.png", 5, dx, dy, 1, 1, 3)
        elif tower.level == 2:
            bullet = Bullet("red.png", 6, dx, dy, 3, 3, 4)
        else:
            bullet = Bullet("red.png", 7, dx, dy, 50, 10, 5)

        bullet.center_x = tower.center_x
        bullet.center_y = tower.center_y
        self.bullet_list.append(bullet)

    def shoot_tack(self, tower):
        directions = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]

        for dx, dy in directions:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            if tower.level == 1:
                bullet = Bullet("red.png", 6, dx, dy, 2, 1, 1)
            elif tower.level == 2:
                bullet = Bullet("red.png", 7, dx, dy, 4, 2, 1.5)
            else:
                bullet = Bullet("red.png", 8, dx, dy, 10, 5, 3)

            bullet.center_x = tower.center_x
            bullet.center_y = tower.center_y
            self.bullet_list.append(bullet)

    def on_update(self, delta_time):
        elapsed = time.time() - self.start_time
        self.spawn_rate = max(10, 100 - int(elapsed // 5))
        self.spawn_balloon()

        for tower in self.tower_list:
            if time.time() - tower.last_shot > tower.shoot_speed:
                if tower.tower_type == "norm":
                    self.shoot_norm(tower)
                else:
                    self.shoot_tack(tower)
                tower.last_shot = time.time()

        for bullet in self.bullet_list:
            if time.time() - bullet.spawn_time > bullet.lifetime:
                bullet.remove_from_sprite_lists()
                continue

            hits = arcade.check_for_collision_with_list(bullet, self.blist)
            for balloon in hits:
                balloon.hp -= bullet.damage
                bullet.pierce -= 1

                if balloon.hp <= 0:
                    balloon.remove_from_sprite_lists()
                    self.money += 5

                if bullet.pierce <= 0:
                    bullet.remove_from_sprite_lists()
                    break

        for balloon in self.blist:
            if time.time() - balloon.spawn_time > 3:
                balloon.remove_from_sprite_lists()

        self.blist.update()
        self.bullet_list.update()

    def on_draw(self):
        self.clear()
        self.blist.draw()
        self.tower_list.draw()
        self.bullet_list.draw()
        arcade.draw_text(f"Money: {self.money}", 20, SCREEN_HEIGHT-40, arcade.color.WHITE, 20)

if __name__ == "__main__":
    game = MyGame()
    arcade.run()

#sachen zum hinzufügen: 
#tack_lvl_1.png mit tack_lvl_2.png und tack_lvl_3.png 
#bullet: lvl.1. leb time=1 sek und schaden =2 und pirce = 1 lvl.2. leb time =1,5 sek und schaden= 4 und pirce=2 lvl.3. leb time = 3 sek und schaden = 10 und pirce =5
#er schießt in 8 richtungen ohne die ballons zu tracken
#norm_lvl_1.png mit norm_lvl_2.png und norm_lvl_3.png 
#bullet: lvl.1. leb time=3 sek und schaden =1 und pirce = 1 lvl.2. leb time = 4 sek und schaden= 3 und pirce=3 lvl.3. leb time = 5 sek und schaden = 50 und pirce = 10
#er tracket die ballons und hat nur ein schuß
#überlege dir bei allen die kosten und die schnelichkeit