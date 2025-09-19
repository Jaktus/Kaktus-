import arcade

arcade.open_window(600, 600, "Koordinatensystem")


arcade.set_background_color(arcade.color.LIGHT_GRAY)

arcade.start_render()






arcade.draw_line(60, 0, 60, 600, arcade.color.BLACK)
arcade.draw_line(120, 0, 120, 600, arcade.color.BLACK)
arcade.draw_line(180, 0, 180, 600, arcade.color.BLACK)
arcade.draw_line(240, 0, 240, 600, arcade.color.BLACK)
arcade.draw_line(300, 0, 300, 580, arcade.color.BLACK, 5)
arcade.draw_line(360, 0, 360, 600, arcade.color.BLACK)
arcade.draw_line(420, 0, 420, 600, arcade.color.BLACK)
arcade.draw_line(480, 0, 480, 600, arcade.color.BLACK)
arcade.draw_line(540, 0, 540, 600, arcade.color.BLACK)


arcade.draw_line(0, 60, 600, 60, arcade.color.BLACK)
arcade.draw_line(0, 120, 600, 120, arcade.color.BLACK)
arcade.draw_line(0, 180, 600, 180, arcade.color.BLACK)
arcade.draw_line(0, 240, 600, 240, arcade.color.BLACK)
arcade.draw_line(0, 300, 580, 300, arcade.color.BLACK, 5)
arcade.draw_line(0, 360, 600, 360, arcade.color.BLACK)
arcade.draw_line(0, 420, 600, 420, arcade.color.BLACK)
arcade.draw_line(0, 480, 600, 480, arcade.color.BLACK)
arcade.draw_line(0, 540, 600, 540, arcade.color.BLACK)


arcade.draw_triangle_filled(600, 300, 575, 280, 575, 320, arcade.color.BLACK)
arcade.draw_triangle_filled(280, 575, 300, 600, 320, 575, arcade.color.BLACK)

arcade.draw_line(60, 315, 60, 285, arcade.color.BLACK, 5)
arcade.draw_line(120, 315, 120, 285, arcade.color.BLACK, 5)
arcade.draw_line(180, 315, 180, 285, arcade.color.BLACK, 5)
arcade.draw_line(240, 315, 240, 285, arcade.color.BLACK, 5)
arcade.draw_line(300, 315, 300, 285, arcade.color.BLACK, 5)
arcade.draw_line(360, 315, 360, 285, arcade.color.BLACK, 5)
arcade.draw_line(420, 315, 420, 285, arcade.color.BLACK, 5)
arcade.draw_line(480, 315, 480, 285, arcade.color.BLACK, 5)
arcade.draw_line(540, 315, 540, 285, arcade.color.BLACK, 5)
arcade.draw_line(285, 60, 315, 60, arcade.color.BLACK, 5)
arcade.draw_line(285, 120, 315, 120, arcade.color.BLACK, 5)
arcade.draw_line(285, 180, 315, 180, arcade.color.BLACK, 5)
arcade.draw_line(285, 240, 315, 240, arcade.color.BLACK, 5)
arcade.draw_line(285, 300, 315, 300, arcade.color.BLACK, 5)
arcade.draw_line(285, 360, 315, 360, arcade.color.BLACK, 5)
arcade.draw_line(285, 420, 315, 420, arcade.color.BLACK, 5)
arcade.draw_line(285, 480, 315, 480, arcade.color.BLACK, 5)
arcade.draw_line(285, 540, 315, 540, arcade.color.BLACK, 5)


arcade.draw_text(-4, 60, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(-3, 120, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(-2, 180, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(-1, 240, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(1, 360, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(2, 420, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(3, 480, 255, arcade.color.BLACK, 20, anchor_x="center")
arcade.draw_text(4, 540, 255, arcade.color.BLACK, 20, anchor_x="center")

arcade.draw_text(4, 325, 50, arcade.color.BLACK, 20, anchor_x="center")



arcade.finish_render()



