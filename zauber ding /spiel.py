import arcade
import math

class Frosch(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("frosch.png", 1.5)
        self.center_x = x
        self.center_y = y
        
        # Bewegung
        self.vx = 0
        self.vy = 0
        self.speed = 200  # px/s horizontal
        self.jump_power = 500  # px/s vertical
        self.gravity = 800  # px/s^2
        
        # Zustand
        self.is_jumping = False
        self.is_grounded = False

class Zauberstab(arcade.Sprite):
    def __init__(self, frosch):
        super().__init__("zauberstab_s.png", 1.5)
        self.frosch = frosch
        self.angle_offset = 0  # Rotationswinkel
        self.rotation_speed = 3  # rad/s
        self.radius = 60  # Abstand vom Frosch
        
    def update(self, delta_time):
        # Rotiere um den Frosch
        self.angle_offset += self.rotation_speed * delta_time
        
        # Berechne kreisende Position
        x = self.frosch.center_x + self.radius * math.cos(self.angle_offset)
        y = self.frosch.center_y + self.radius * math.sin(self.angle_offset)
        
        self.center_x = x
        self.center_y = y
        
        # Rotation zum Stab-Sprite
        self.angle = -math.degrees(self.angle_offset)

class Spiel(arcade.View):
    def __init__(self):
        super().__init__()
        
        # Hintergrundfarbe
        self.bg_color = (20, 20, 40)
        
        # Sprite-Listen
        self.spieler_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        
        # Frosch erstellen
        self.frosch = Frosch(200, 300)
        self.spieler_list.append(self.frosch)
        
        # Zauberstab erstellen
        self.zauberstab = Zauberstab(self.frosch)
        self.spieler_list.append(self.zauberstab)
        
        # Plattformen erstellen (body.png)
        self.create_platforms()
        
        # Maus-Position
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Tasten-Status
        self.keys_pressed = set()
        
    def create_platforms(self):
        """Erstelle Plattformen aus body.png"""
        
        # Bodenplattform
        platforms_data = [
            (400, 50, 3.0),
            (600, 250, 2.5),
            (200, 400, 2.0),
        ]
        
        for x, y, scale in platforms_data:
            platform = arcade.Sprite("body.png", scale)
            platform.center_x = x
            platform.center_y = y
            self.platform_list.append(platform)
            self.spieler_list.append(platform)
    
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x = x
        self.mouse_y = y
    
    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
        # Sprung (SPACE oder W)
        if key in (arcade.key.SPACE, arcade.key.W) and self.frosch.is_grounded:
            self.frosch.vy = self.frosch.jump_power
            self.frosch.is_jumping = True
            self.frosch.is_grounded = False
    
    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def check_collisions(self):
        """Überprüfe Kollisionen mit Plattformen"""
        self.frosch.is_grounded = False
        
        for platform in self.platform_list:
            # Vereinfachte AABB-Kollision
            frosch_bottom = self.frosch.center_y - self.frosch.height / 2
            frosch_top = self.frosch.center_y + self.frosch.height / 2
            frosch_left = self.frosch.center_x - self.frosch.width / 2
            frosch_right = self.frosch.center_x + self.frosch.width / 2
            
            platform_bottom = platform.center_y - platform.height / 2
            platform_top = platform.center_y + platform.height / 2
            platform_left = platform.center_x - platform.width / 2
            platform_right = platform.center_x + platform.width / 2
            
            # Prüfe Überlappung
            if (frosch_right > platform_left and frosch_left < platform_right and
                frosch_bottom <= platform_top + 5 and frosch_top >= platform_bottom):
                
                # Prüfe auf Landung von oben
                if self.frosch.vy <= 0 and frosch_bottom > platform_bottom:
                    self.frosch.center_y = platform_top + self.frosch.height / 2
                    self.frosch.vy = 0
                    self.frosch.is_grounded = True
                    self.frosch.is_jumping = False
    
    def on_update(self, delta_time: float):
        # Spieler-Eingabe verarbeiten
        if arcade.key.A in self.keys_pressed:
            self.frosch.vx = -self.frosch.speed
        elif arcade.key.D in self.keys_pressed:
            self.frosch.vx = self.frosch.speed
        else:
            self.frosch.vx = 0
        
        # Gravity anwenden
        self.frosch.vy -= self.frosch.gravity * delta_time
        
        # Position aktualisieren
        self.frosch.center_x += self.frosch.vx * delta_time
        self.frosch.center_y += self.frosch.vy * delta_time
        
        # Kollisionen überprüfen
        self.check_collisions()
        
        # Zauberstab aktualisieren
        self.zauberstab.update(delta_time)
    
    def on_draw(self):
        self.clear(self.bg_color)
        
        # Zeichne Plattformen und Sprites
        self.platform_list.draw(pixelated=True)
        self.spieler_list.draw(pixelated=True)
        
        # Hinweise
        arcade.draw_text("A/D - Move", 10, 580, arcade.color.WHITE, 12)
        arcade.draw_text("SPACE/W - Jump", 10, 560, arcade.color.WHITE, 12)


# Hauptfenster
window = arcade.Window(800, 600, "Frosch und Zauberstab")
spiel_view = Spiel()
window.show_view(spiel_view)
arcade.run()
