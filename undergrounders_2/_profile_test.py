import arcade, random, time, statistics

WORLD_WIDTH = 8000
WORLD_HEIGHT = 8000

win = arcade.Window(800, 600, "t")

stone_list = arcade.SpriteList(use_spatial_hash=True)
t0 = time.perf_counter()
for x in range(0, WORLD_WIDTH, 32):
    for y in range(0, WORLD_HEIGHT, 32):
        in_spawn = (WORLD_WIDTH / 2 - 100 < x < WORLD_WIDTH / 2 + 100 and
                    WORLD_HEIGHT / 2 - 100 < y < WORLD_HEIGHT / 2 + 100)
        if in_spawn:
            continue
        s = arcade.Sprite("stone.png", 1)
        s.center_x = x
        s.center_y = y
        stone_list.append(s)
print("build", time.perf_counter() - t0, "count", len(stone_list))

times = []
for i in range(30):
    b = arcade.Sprite("crafting_block.png", 0.5)
    b.center_x = random.uniform(0, 8000)
    b.center_y = random.uniform(0, 8000)
    t0 = time.perf_counter()
    stone_list.append(b)
    times.append(time.perf_counter() - t0)
print("append times (ms)", [round(t*1000, 2) for t in times])
print("avg ms", statistics.mean(times) * 1000)

player = arcade.Sprite("player.png", 1)
player.center_x = WORLD_WIDTH / 2
player.center_y = WORLD_HEIGHT / 2
phys = arcade.PhysicsEngineSimple(player, stone_list)
t0 = time.perf_counter()
for i in range(60):
    phys.update()
print("60 physics updates", time.perf_counter() - t0)
