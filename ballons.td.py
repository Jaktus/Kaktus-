import arcade
import random

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 800
SCREEN_TITLE = "td"
VIEWPORT_MARGIN = 200

class MyGame(arcade.Window):
    """ Main Game Window """

    def __init__(self, width, height, title):
        """ Set up the class. """
        super().__init__(width, height, title, resizable=True, update_rate=1/390)

        self.tdlist = arcade.SpriteList()

        self.warum = arcade.Sprite("btFeld.png")
        self.warum.center_x = 550
        self.warum.center_y = 400
        
        wie = arcade.Sprite("btballon.png")
        wie.center_x = 75
        wie.center_y = 770
        self.tdlist.append(wie)
        wie.change_y = -1

        self.turmlist = arcade.SpriteList()
        self.kugellist = arcade.SpriteList()

        self.schusszeit = 0

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        over = arcade.Sprite("over.png", 0.6)
        over.center_x = x
        over.center_y = y+0
        self.turmlist.append(over)


    def on_update(self, delta_time):

        
        self.schusszeit = self.schusszeit + delta_time

        if self.schusszeit >= 2:
            kugel = arcade.Sprite("ice.png")
            kugel.position = over.position
            kugel.change_y = 1
            self.kugellist.append(kugel)


        if random.randint(1, 200) == 1: 
            wie = arcade.Sprite("btballon.png")
            wie.center_x = 75
            wie.center_y = 770
            self.tdlist.append(wie)
            wie.change_y = -1  


        #if random.randint(1, 100) == 1: 
            #wie = arcade.Sprite("ice.png")
            #wie.center_x = 75
            #wie.center_y = 75
            #self.tdlist.append(wie)
            #wie.change_y = -1  


        for ballon in self.tdlist:
            if ballon.center_x == 75 and ballon.center_y == 675:
                ballon.change_x = 1
                ballon.change_y = 0
            if ballon.center_x == 275 and ballon.center_y == 675:
                ballon.change_x = 0
                ballon.change_y = -1
            if ballon.center_x == 275 and ballon.center_y == 525:
                ballon.change_x = -1
                ballon.change_y = 0
            if ballon.center_x == 75 and ballon.center_y == 525:   
                ballon.change_x = 0
                ballon.change_y = -1
            if ballon.center_x == 75 and ballon.center_y ==  375:   
                ballon.change_x = 1
                ballon.change_y = 0
            if ballon.center_x == 275 and ballon.center_y == 375:   
                ballon.change_x = 0
                ballon.change_y = -1
            if ballon.center_x == 275 and ballon.center_y == 225:   
                ballon.change_x = -1
                ballon.change_y = 0
            if ballon.center_x == 75 and ballon.center_y == 225:   
                ballon.change_x = 0
                ballon.change_y = -1
            if ballon.center_x == 75 and ballon.center_y == 75:   
                ballon.change_x = 1
                ballon.change_y = 0
            if ballon.center_x == 475 and ballon.center_y == 75:   
                ballon.change_x = 0
                ballon.change_y = 1
            if ballon.center_x == 475 and ballon.center_y == 725:   
                ballon.change_x = 1
                ballon.change_y = 0
            if ballon.center_x == 1025 and ballon.center_y == 725:   
                ballon.change_x = 0
                ballon.change_y = 1
                
        self.tdlist.update()
        self.kugellist.update()
        # print("x: " + str(ballon.center_x) + ", y: " + str(ballon.center_y))

        for over in self.overlist:
            kugel = arcade.Sprite("ice.png")
            kugel.position = over.position
            kugel.change_y = 1
            self.kugellist.append(kugel)
    
    def on_draw(self):
        self.clear()
        self.warum.draw()
        self.tdlist.draw()
        self.overlist.draw()
        self.kugellist.draw()

if __name__ == "__main__":
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()