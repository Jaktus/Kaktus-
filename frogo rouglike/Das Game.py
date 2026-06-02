import arcade
from arcade.future.light import Light, LightLayer
import random, os, math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# ────────────────────────────────────────────────────────────────────────────
# CARD SYSTEM - Erweitertes Karten-, Runen- und Kombinationssystem
# ────────────────────────────────────────────────────────────────────────────

class RuneType(Enum):
    """Alle verfügbaren Runentypen"""
    ICE = "ice"
    FIRE = "fire"
    BLOOD = "blood"
    THUNDER = "thunder"
    POISON = "poison"
    WIND = "wind"
    EXPLOSION = "explosion"
    SHADOW = "shadow"


class CardType(Enum):
    """Alle verfügbaren Kartentypen"""
    NORMAL_SHOT = "normal_shot"
    SHOTGUN = "shotgun"
    SPIN = "spin"
    SHIELD = "shield"
    INVINCIBILITY = "invincibility"
    LIFE_UP = "life_up"



@dataclass
class Rune:
    """Einzelne Rune mit Effektbeschreibungen"""
    rune_type: RuneType
    stack_level: int = 1
  
    @property
    def rarity(self) -> str:
        if self.stack_level == 1:
            return "uncommon"
        elif self.stack_level == 2:
            return "rare"
        elif self.stack_level >= 3:
            return "epic"
        return "uncommon"
    
    @property
    def display_name(self) -> str:
        names = {
            RuneType.ICE: "Eis-Rune",
            RuneType.FIRE: "Feuer-Rune",
            RuneType.BLOOD: "Blut-Rune",
            RuneType.THUNDER: "Donner-Rune",
            RuneType.POISON: "Gift-Rune",
            RuneType.WIND: "Wind-Rune",
            RuneType.EXPLOSION: "Explosions-Rune",
            RuneType.SHADOW: "Schatten-Rune",
        }
        name = names.get(self.rune_type, "Unbekannte Rune")
        if self.stack_level > 1:
            name += f" x{self.stack_level}"
        return name
    
    def get_effect_description(self, card_type: CardType) -> str:
        descriptions = {
            CardType.NORMAL_SHOT: {
                RuneType.ICE: "Schüsse verlangsamen oder frieren Gegner ein",
                RuneType.FIRE: "Gegner brennen über Zeit",
                RuneType.BLOOD: "Schüsse stehlen Leben von Gegnern",
                RuneType.THUNDER: "Blitze springen zwischen Gegnern",
                RuneType.POISON: "Gegner werden vergiftet",
                RuneType.WIND: "Schüsse fliegen schneller und stoßen Gegner zurück",
                RuneType.EXPLOSION: "Projektile explodieren beim Treffer",
                RuneType.SHADOW: "Kleine Chance auf kritischen Schaden oder Teleport-Schüsse",
            },
            CardType.SHOTGUN: {
                RuneType.ICE: "Mehrere Frost-Projektile frieren Gruppen ein",
                RuneType.FIRE: "Streuschüsse verursachen Feuerschaden",
                RuneType.BLOOD: "Jeder Treffer heilt den Spieler leicht",
                RuneType.THUNDER: "Schüsse erzeugen Kettenblitze",
                RuneType.POISON: "Gegner hinterlassen Giftwolken",
                RuneType.WIND: "Schüsse stoßen Gegner stark zurück",
                RuneType.EXPLOSION: "Jede Kugel explodiert",
                RuneType.SHADOW: "Projektile können durch Gegner fliegen",
            },
            CardType.SPIN: {
                RuneType.ICE: "Gegner frieren bei Kontakt ein",
                RuneType.FIRE: "Feuerkreis um den Spieler",
                RuneType.BLOOD: "Spin heilt bei Treffern",
                RuneType.THUNDER: "Blitze erscheinen während des Spins",
                RuneType.POISON: "Giftwolke während der Drehung",
                RuneType.WIND: "Gegner werden angezogen oder weggeschleudert",
                RuneType.EXPLOSION: "Kleine Explosionen während der Drehung",
                RuneType.SHADOW: "Spieler wird während des Spins schneller oder unsichtbar",
            },
            CardType.SHIELD: {
                RuneType.ICE: "Gegner frieren bei Berührung ein",
                RuneType.FIRE: "Gegner brennen bei Kontakt",
                RuneType.BLOOD: "Kontakt heilt den Spieler",
                RuneType.THUNDER: "Schild erzeugt elektrische Schocks",
                RuneType.POISON: "Gegner werden vergiftet",
                RuneType.WIND: "Projektile werden abgelenkt",
                RuneType.EXPLOSION: "Schild explodiert bei Treffer",
                RuneType.SHADOW: "Chance Schaden komplett zu negieren",
            },
            CardType.INVINCIBILITY: {
                RuneType.ICE: "Gegner werden während Invincibility langsamer",
                RuneType.FIRE: "Feuer-Aura während Unverwundbarkeit",
                RuneType.BLOOD: "Gegner verlieren dauerhaft Leben in der Nähe",
                RuneType.THUNDER: "Permanente Blitzschläge um den Spieler",
                RuneType.POISON: "Giftfeld um den Spieler",
                RuneType.WIND: "Massive Bewegungsgeschwindigkeit",
                RuneType.EXPLOSION: "Explosionen bei Bewegung",
                RuneType.SHADOW: "Spieler wird halb unsichtbar",
            },
            CardType.LIFE_UP: {
                RuneType.ICE: "Mehr HP und langsame Gegner",
                RuneType.FIRE: "Mehr Schaden bei niedrigem Leben",
                RuneType.BLOOD: "Lebensraub dauerhaft aktiv",
                RuneType.THUNDER: "Treffer laden Blitzenergie auf",
                RuneType.POISON: "Gegner vergiften sich beim Treffer",
                RuneType.WIND: "Mehr Geschwindigkeit und HP",
                RuneType.EXPLOSION: "Explosion beim Schadennehmen",
                RuneType.SHADOW: "Mehr Crit-Chance aber weniger Max HP",
            },
        }
        card_desc = descriptions.get(card_type, {})
        return card_desc.get(self.rune_type, "Unbekannter Effekt")


@dataclass
class Combination:
    """Eine Kombination aus Karte + Runen"""
    card_type: CardType
    runes: List[RuneType] = field(default_factory=list)
    
    @property
    def fusion_name(self) -> str:
        combinations = {
            (CardType.NORMAL_SHOT, RuneType.ICE): "Frost Shot",
            (CardType.NORMAL_SHOT, RuneType.FIRE): "Flame Shot",
            (CardType.NORMAL_SHOT, RuneType.BLOOD): "Vampire Shot",
            (CardType.NORMAL_SHOT, RuneType.THUNDER): "Shock Shot",
            (CardType.NORMAL_SHOT, RuneType.POISON): "Toxic Shot",
            (CardType.NORMAL_SHOT, RuneType.WIND): "Wind Shot",
            (CardType.NORMAL_SHOT, RuneType.EXPLOSION): "Blast Shot",
            (CardType.NORMAL_SHOT, RuneType.SHADOW): "Shadow Shot",
            (CardType.SHOTGUN, RuneType.ICE): "Frost Shotgun",
            (CardType.SHOTGUN, RuneType.FIRE): "Dragon Breath",
            (CardType.SHOTGUN, RuneType.BLOOD): "Blood Scatter",
            (CardType.SHOTGUN, RuneType.THUNDER): "Storm Shotgun",
            (CardType.SHOTGUN, RuneType.POISON): "Venom Spread",
            (CardType.SHOTGUN, RuneType.WIND): "Hurricane Shotgun",
            (CardType.SHOTGUN, RuneType.EXPLOSION): "Bomb Shell",
            (CardType.SHOTGUN, RuneType.SHADOW): "Phantom Shotgun",
            (CardType.SPIN, RuneType.ICE): "Ice Spin",
            (CardType.SPIN, RuneType.FIRE): "Flame Spin",
            (CardType.SPIN, RuneType.BLOOD): "Blood Spin",
            (CardType.SPIN, RuneType.THUNDER): "Storm Spin",
            (CardType.SPIN, RuneType.POISON): "Toxic Spin",
            (CardType.SPIN, RuneType.WIND): "Tornado Spin",
            (CardType.SPIN, RuneType.EXPLOSION): "Blast Spin",
            (CardType.SPIN, RuneType.SHADOW): "Shadow Spin",
            (CardType.SHIELD, RuneType.ICE): "Ice Shield",
            (CardType.SHIELD, RuneType.FIRE): "Flame Shield",
            (CardType.SHIELD, RuneType.BLOOD): "Vampire Shield",
            (CardType.SHIELD, RuneType.THUNDER): "Thunder Shield",
            (CardType.SHIELD, RuneType.POISON): "Toxic Shield",
            (CardType.SHIELD, RuneType.WIND): "Wind Barrier",
            (CardType.SHIELD, RuneType.EXPLOSION): "Blast Barrier",
            (CardType.SHIELD, RuneType.SHADOW): "Phantom Shield",
            (CardType.INVINCIBILITY, RuneType.ICE): "Frozen Time",
            (CardType.INVINCIBILITY, RuneType.FIRE): "Inferno Form",
            (CardType.INVINCIBILITY, RuneType.BLOOD): "Blood God",
            (CardType.INVINCIBILITY, RuneType.THUNDER): "Thunder Core",
            (CardType.INVINCIBILITY, RuneType.POISON): "Toxic Aura",
            (CardType.INVINCIBILITY, RuneType.WIND): "Speed Form",
            (CardType.INVINCIBILITY, RuneType.EXPLOSION): "Chaos Form",
            (CardType.INVINCIBILITY, RuneType.SHADOW): "Void Form",
            (CardType.LIFE_UP, RuneType.ICE): "Frozen Heart",
            (CardType.LIFE_UP, RuneType.BLOOD): "Vampire Heart",
            (CardType.LIFE_UP, RuneType.THUNDER): "Charged Heart",
            (CardType.LIFE_UP, RuneType.POISON): "Toxic Blood",
            (CardType.LIFE_UP, RuneType.WIND): "Light Body",
            (CardType.LIFE_UP, RuneType.EXPLOSION): "Unstable Core",
            (CardType.LIFE_UP, RuneType.SHADOW): "Dark Heart",
        }
        if self.runes:
            key = (self.card_type, self.runes[0])
            return combinations.get(key, "Mystery Fusion")
        return "Unknown Fusion"
    
    @property
    def rarity(self) -> str:
        if not self.runes:
            return "common"
        rarity_levels = {"uncommon": 0, "rare": 1, "epic": 2, "legendary": 3}
        total_level = sum([rarity_levels.get(self._get_rune_rarity(r), 0) for r in self.runes])
        if total_level >= 4:
            return "legendary"
        elif total_level >= 3:
            return "epic"
        elif total_level >= 2:
            return "rare"
        else:
            return "uncommon"
    
    def _get_rune_rarity(self, rune_type: RuneType) -> str:
        return "uncommon"
    
    def is_valid(self) -> bool:
        return len(self.runes) > 0 and len(self.runes) <= 3
    
    def get_summary(self) -> str:
        rune_names = [r.value.capitalize() for r in self.runes]
        return f"{self.card_type.value} + {', '.join(rune_names)}"

    def rune_counts(self) -> Dict[RuneType, int]:
        counts: Dict[RuneType, int] = {}
        for rune in self.runes:
            counts[rune] = counts.get(rune, 0) + 1
        return counts

    @property
    def primary_rune(self) -> Optional[RuneType]:
        return self.runes[0] if self.runes else None

    @property
    def power_level(self) -> int:
        return max(1, len(self.runes))


@dataclass
class CraftingSlot:
    card_type: Optional[CardType] = None
    card_id: Optional[str] = None
    runes: List[RuneType] = field(default_factory=list)
    
    def clear(self):
        self.card_type = None
        self.card_id = None
        self.runes = []
    
    def is_empty(self) -> bool:
        return self.card_type is None and len(self.runes) == 0
    
    def is_valid(self) -> bool:
        return self.card_type is not None and len(self.runes) > 0


class CraftingStation:
    def __init__(self):
        self.slot = CraftingSlot()
        self.fusion_in_progress = False
        self.fusion_timer = 0.0
        self.current_fusion: Optional[Combination] = None
        self.ready_after_boss = False
    
    def add_card(self, card_type: CardType, card_id: Optional[str] = None):
        self.slot.card_type = card_type
        self.slot.card_id = card_id
    
    def add_rune(self, rune_type: RuneType):
        if len(self.slot.runes) < 3:
            self.slot.runes.append(rune_type)
    
    def remove_rune(self, index: int):
        if 0 <= index < len(self.slot.runes):
            del self.slot.runes[index]
    
    def clear(self):
        self.slot.clear()
        self.fusion_in_progress = False
        self.current_fusion = None
        self.fusion_timer = 0.0
        self.ready_after_boss = False
    
    def start_crafting(self) -> bool:
        if not self.slot.is_valid():
            return False
        self.current_fusion = Combination(card_type=self.slot.card_type, runes=self.slot.runes.copy())
        self.fusion_in_progress = True
        self.fusion_timer = 0.0
        self.ready_after_boss = False
        self.slot.clear()
        return True
    
    def update(self, delta_time: float):
        if self.fusion_in_progress:
            self.fusion_timer += delta_time
    
    def is_ready(self) -> bool:
        return self.current_fusion is not None and self.ready_after_boss

    def complete_after_boss(self):
        if self.current_fusion is not None:
            self.ready_after_boss = True
    
    def claim_fusion(self) -> Optional[Combination]:
        if self.is_ready():
            fusion = self.current_fusion
            self.clear()
            return fusion
        return None


class SkillTreeNode:
    def __init__(self, combination: Combination, x: float, y: float):
        self.combination = combination
        self.x = x
        self.y = y
        self.unlocked = True
        self.discovered = False
        self.connections: List['SkillTreeNode'] = []
    
    def get_display_text(self) -> str:
        return self.combination.fusion_name if self.discovered else "?"


class SkillTree:
    def __init__(self):
        self.nodes: Dict[str, SkillTreeNode] = {}
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0
    
    def add_combination(self, combination: Combination) -> bool:
        key = self._combination_key(combination)
        if key in self.nodes:
            self.nodes[key].discovered = True
            return False
        x = float(len(self.nodes) % 8) * 150
        y = float(len(self.nodes) // 8) * 150
        node = SkillTreeNode(combination, x, y)
        node.discovered = True
        self.nodes[key] = node
        self._connect_similar_nodes(node, combination)
        return True

    def add_unknown_combination(self, combination: Combination) -> bool:
        key = self._combination_key(combination)
        if key in self.nodes:
            return False
        x = float(len(self.nodes) % 8) * 150
        y = float(len(self.nodes) // 8) * 150
        node = SkillTreeNode(combination, x, y)
        node.discovered = False
        self.nodes[key] = node
        self._connect_similar_nodes(node, combination)
        return True

    def populate_unknown_combinations(self):
        for card_type in CardType:
            for rune_type in RuneType:
                self.add_unknown_combination(Combination(card_type, [rune_type]))
    
    def _combination_key(self, combination: Combination) -> str:
        rune_str = "_".join(sorted([r.value for r in combination.runes]))
        return f"{combination.card_type.value}_{rune_str}"
    
    def _connect_similar_nodes(self, new_node: SkillTreeNode, combination: Combination):
        for key, node in self.nodes.items():
            if node is new_node:
                continue
            if node.combination.card_type == combination.card_type:
                if new_node not in node.connections:
                    node.connections.append(new_node)
                if node not in new_node.connections:
                    new_node.connections.append(node)
    
    def pan(self, dx: float, dy: float):
        self.camera_x += dx
        self.camera_y += dy
    
    def zoom_in(self):
        self.zoom = min(3.0, self.zoom * 1.2)
    
    def zoom_out(self):
        self.zoom = max(0.3, self.zoom / 1.2)
    
    def get_all_nodes(self) -> List[SkillTreeNode]:
        return list(self.nodes.values())


class MiniMap:
    def __init__(self):
        self.width = 150
        self.height = 150
        self.x = 1024 - self.width - 10
        self.y = 768 - self.height - 10
        self.rooms: Dict[Tuple[int, int], str] = {}
    
    def explore_room(self, grid_x: int, grid_y: int, room_type: str = "normal"):
        self.rooms[(grid_x, grid_y)] = room_type
    
    def is_explored(self, grid_x: int, grid_y: int) -> bool:
        return (grid_x, grid_y) in self.rooms
    
    def get_room_type(self, grid_x: int, grid_y: int) -> str:
        return self.rooms.get((grid_x, grid_y), "unknown")


class TreasureRoom:
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.is_treasure_room = True
        self.has_enemies = False
        self.rare_runes: List[Rune] = []
        self.special_rewards: List[str] = []
        self.secret_fusion: Optional[Combination] = None
        self._generate_loot()
    
    def _generate_loot(self):
        if random.random() < 0.3:
            rune_type = random.choice(list(RuneType))
            self.rare_runes.append(Rune(rune_type, stack_level=random.randint(1, 2)))
        self.special_rewards = ["coin", "hp_restore", "damage_boost"][:random.randint(1, 2)]
        if random.random() < 0.1:
            card_type = random.choice(list(CardType))
            num_runes = random.randint(1, 2)
            rune_types = random.sample(list(RuneType), num_runes)
            self.secret_fusion = Combination(card_type, rune_types)


class RuneInventory:
    def __init__(self):
        self.runes: List[Rune] = []
    
    def add_rune(self, rune: Rune):
        for existing in self.runes:
            if existing.rune_type == rune.rune_type:
                existing.stack_level += 1
                return
        self.runes.append(rune)
    
    def remove_rune(self, index: int) -> Optional[Rune]:
        if 0 <= index < len(self.runes):
            return self.runes.pop(index)
        return None

    def consume_rune(self, rune_type: RuneType) -> bool:
        for rune in list(self.runes):
            if rune.rune_type == rune_type and rune.stack_level > 0:
                rune.stack_level -= 1
                if rune.stack_level <= 0:
                    self.runes.remove(rune)
                return True
        return False
    
    def get_rune(self, rune_type: RuneType) -> Optional[Rune]:
        for rune in self.runes:
            if rune.rune_type == rune_type:
                return rune
        return None
    
    def has_rune(self, rune_type: RuneType) -> bool:
        return self.get_rune(rune_type) is not None


# ────────────────────────────────────────────────────────────────────────────
# UI SYSTEM - Rendering für Skill Tree, Mini-Map, Crafting
# ────────────────────────────────────────────────────────────────────────────

class SkillTreeUI:
    def __init__(self, skill_tree: SkillTree):
        self.skill_tree = skill_tree
        self.visible = False
        self.selected_node: Optional[SkillTreeNode] = None
    
    def toggle_visibility(self):
        self.visible = not self.visible
    
    def draw(self, screen_width: int, screen_height: int):
        if not self.visible:
            return
        arcade.draw_rect_filled(arcade.XYWH(screen_width / 2, screen_height / 2, screen_width, screen_height), (0, 0, 0, 160))
        arcade.draw_rect_filled(arcade.XYWH(screen_width / 2, screen_height / 2, screen_width - 120, screen_height - 100), (120, 70, 35, 235))
        arcade.draw_rect_outline(arcade.XYWH(screen_width / 2, screen_height / 2, screen_width - 120, screen_height - 100), (60, 35, 20, 255), 8)
        arcade.draw_text("SKILL TREE", screen_width // 2, screen_height - 70, color=arcade.color.BEIGE, anchor_x="center", font_size=24, bold=True)
        for node in self.skill_tree.get_all_nodes():
            self._draw_node(node, screen_width, screen_height)
        for node in self.skill_tree.get_all_nodes():
            for connection in node.connections:
                self._draw_connection(node, connection, screen_width, screen_height)
        if self.selected_node:
            self._draw_info_panel(self.selected_node, screen_width, screen_height)
        arcade.draw_text("WASD: Bewegen | Scroll: Zoomen | ESC: Schliessen | Click: Auswahl", screen_width // 2, 42, color=arcade.color.LIGHT_GRAY, anchor_x="center", font_size=10)
    
    def _draw_node(self, node: SkillTreeNode, screen_width: int, screen_height: int):
        x = (node.x - self.skill_tree.camera_x) * self.skill_tree.zoom + screen_width // 2
        y = (node.y - self.skill_tree.camera_y) * self.skill_tree.zoom + screen_height // 2
        radius = 20 * self.skill_tree.zoom
        color_map = {"common": (200, 200, 200), "uncommon": (80, 200, 80), "rare": (80, 140, 220), "epic": (180, 80, 200), "legendary": (220, 190, 60)}
        color = color_map.get(node.combination.rarity, (200, 200, 200)) if node.discovered else (70, 60, 55)
        if node is self.selected_node:
            arcade.draw_circle_outline(x, y, radius + 5, arcade.color.WHITE, 3)
        arcade.draw_circle_filled(x, y, radius, color)
        arcade.draw_circle_outline(x, y, radius, arcade.color.WHITE, 2)
        if self.skill_tree.zoom > 0.5:
            arcade.draw_text(node.get_display_text()[:15], x, y, color=arcade.color.BLACK, anchor_x="center", anchor_y="center", font_size=max(8, int(10 * self.skill_tree.zoom)))
    
    def _draw_connection(self, node1: SkillTreeNode, node2: SkillTreeNode, screen_width: int, screen_height: int):
        x1 = (node1.x - self.skill_tree.camera_x) * self.skill_tree.zoom + screen_width // 2
        y1 = (node1.y - self.skill_tree.camera_y) * self.skill_tree.zoom + screen_height // 2
        x2 = (node2.x - self.skill_tree.camera_x) * self.skill_tree.zoom + screen_width // 2
        y2 = (node2.y - self.skill_tree.camera_y) * self.skill_tree.zoom + screen_height // 2
        arcade.draw_line(x1, y1, x2, y2, arcade.color.LIGHT_GRAY, 2)
    
    def _draw_info_panel(self, node: SkillTreeNode, screen_width: int, screen_height: int):
        panel_x = screen_width - 270
        panel_y = screen_height - 230
        panel_width = 200
        panel_height = 180
        arcade.draw_rect_filled(arcade.XYWH(panel_x, panel_y, panel_width, panel_height), (95, 55, 28, 240))
        arcade.draw_rect_outline(arcade.XYWH(panel_x, panel_y, panel_width, panel_height), (60, 35, 20, 255), 4)
        if not node.discovered:
            arcade.draw_text("?", panel_x + 10, panel_y + 150, color=arcade.color.WHITE, font_size=22, bold=True)
            arcade.draw_text("Unentdeckte Fusion", panel_x + 10, panel_y + 122, color=arcade.color.LIGHT_GRAY, font_size=10)
            arcade.draw_text("Crafting im Boss-Shop", panel_x + 10, panel_y + 102, color=arcade.color.LIGHT_GRAY, font_size=9)
            return
        arcade.draw_text(node.combination.fusion_name, panel_x + 10, panel_y + 150, color=arcade.color.WHITE, font_size=12, bold=True)
        arcade.draw_text(f"Card: {node.combination.card_type.value}", panel_x + 10, panel_y + 130, color=arcade.color.LIGHT_GRAY, font_size=9)
        rune_text = ", ".join([r.value for r in node.combination.runes])
        arcade.draw_text(f"Runes: {rune_text}", panel_x + 10, panel_y + 115, color=arcade.color.LIGHT_CYAN, font_size=8)
        rarity_colors = {"common": arcade.color.LIGHT_GRAY, "uncommon": arcade.color.LIGHT_GREEN, "rare": arcade.color.LIGHT_BLUE, "epic": arcade.color.LIGHT_MAGENTA, "legendary": arcade.color.YELLOW}
        rarity_color = rarity_colors.get(node.combination.rarity, arcade.color.WHITE)
        arcade.draw_text(f"Rarity: {node.combination.rarity.upper()}", panel_x + 10, panel_y + 95, color=rarity_color, font_size=9, bold=True)


class MiniMapUI:
    def __init__(self, mini_map: MiniMap):
        self.mini_map = mini_map
        self.visible = False

    def toggle_visibility(self):
        self.visible = not self.visible
    
    def draw(self, screen_width: int, screen_height: int, current_room_grid: Tuple[int, int] = (0, 0), compact: bool = False):
        if not self.visible and not compact:
            return
        if compact:
            x = self.mini_map.x
            y = self.mini_map.y
            w = self.mini_map.width
            h = self.mini_map.height
            title = "MAP"
            room_size = min(w // 5, h // 5)
        else:
            w = int(screen_width * 0.72)
            h = int(screen_height * 0.68)
            x = int((screen_width - w) // 2)
            y = int((screen_height - h) // 2)
            title = "DUNGEON MAP"
            room_size = min(w // 9, h // 7)
            arcade.draw_rect_filled(arcade.XYWH(screen_width / 2, screen_height / 2, screen_width, screen_height), (0, 0, 0, 160))
        arcade.draw_rect_filled(arcade.XYWH(x, y, w, h), (120, 70, 35, 235))
        arcade.draw_rect_outline(arcade.XYWH(x, y, w, h), (60, 35, 20, 255), 8 if not compact else 3)
        center_x = x + w // 2
        center_y = y + h // 2
        for (grid_x, grid_y), room_type in self.mini_map.rooms.items():
            rel_x = (grid_x - current_room_grid[0]) * room_size
            rel_y = (grid_y - current_room_grid[1]) * room_size
            room_x = center_x + rel_x
            room_y = center_y + rel_y
            if abs(rel_x) <= w // 2 and abs(rel_y) <= h // 2:
                self._draw_room(room_x, room_y, room_size, room_type, grid_x == current_room_grid[0] and grid_y == current_room_grid[1])
        arcade.draw_text(title, x + w // 2, y + h - 36 if not compact else y + h + 5, color=arcade.color.BEIGE, anchor_x="center", font_size=22 if not compact else 10, bold=True)
        if not compact:
            arcade.draw_text("M / ESC: Schliessen", x + w // 2, y + 24, color=arcade.color.LIGHT_GRAY, anchor_x="center", font_size=12)
    
    def _draw_room(self, x: float, y: float, size: float, room_type: str, is_current: bool):
        color_map = {"normal": (100, 100, 120), "boss": (220, 40, 40), "treasure": (220, 190, 60), "shop": (80, 200, 80), "escape": (200, 100, 200)}
        color = color_map.get(room_type, (100, 100, 100))
        if is_current:
            arcade.draw_rect_filled(arcade.XYWH(x - size//2, y - size//2, size, size), (100, 200, 255))
            arcade.draw_rect_outline(arcade.XYWH(x - size//2, y - size//2, size, size), arcade.color.WHITE, 2)
        else:
            arcade.draw_rect_filled(arcade.XYWH(x - size//2, y - size//2, size, size), color)
            arcade.draw_rect_outline(arcade.XYWH(x - size//2, y - size//2, size, size), (150, 150, 150), 1)


class CraftingStationUI:
    # Runen-Farben fuer die Slots
    RUNE_COLORS = {
        RuneType.ICE:       (100, 200, 255, 255),
        RuneType.FIRE:      (255, 110, 40,  255),
        RuneType.BLOOD:     (210, 30,  60,  255),
        RuneType.THUNDER:   (245, 235, 50,  255),
        RuneType.POISON:    (80,  220, 80,  255),
        RuneType.WIND:      (180, 245, 255, 255),
        RuneType.EXPLOSION: (255, 165, 30,  255),
        RuneType.SHADOW:    (160, 90,  225, 255),
    }

    def __init__(self, crafting_station: CraftingStation, rune_inventory: RuneInventory, game=None):
        self.crafting_station = crafting_station
        self.rune_inventory = rune_inventory
        self.game = game
        self.visible = False
        self.card_inventory_rects = []
        self.rune_inventory_rects = []
        self.card_slot_rect = None
        self.rune_slot_rect = None
        self.start_claim_rect = None

    def toggle_visibility(self):
        self.visible = not self.visible

    # ── Haupt-Draw ────────────────────────────────────────────────────────
    def draw(self, screen_width: int, screen_height: int):
        if not self.visible:
            return
        self.card_inventory_rects = []
        self.rune_inventory_rects = []
        self.start_claim_rect = None

        pw = int(screen_width * 0.90)
        ph = int(screen_height * 0.87)
        cx = screen_width // 2
        cy = screen_height // 2
        px = cx - pw // 2
        py = cy - ph // 2

        # Hintergrund-Overlay
        arcade.draw_rect_filled(arcade.XYWH(cx, cy, screen_width, screen_height), (0, 0, 0, 180))

        # Panel-Hintergrund mit innerer Borduere
        arcade.draw_rect_filled(arcade.XYWH(cx, cy, pw, ph), (45, 26, 12, 252))
        arcade.draw_rect_outline(arcade.XYWH(cx, cy, pw, ph), (215, 165, 65, 255), 5)
        arcade.draw_rect_outline(arcade.XYWH(cx, cy, pw - 14, ph - 14), (140, 100, 45, 100), 2)

        # Titelleiste
        arcade.draw_rect_filled(arcade.XYWH(cx, py + ph - 26, pw - 10, 46), (75, 45, 18, 220))
        arcade.draw_rect_outline(arcade.XYWH(cx, py + ph - 26, pw - 10, 46), (200, 155, 60, 180), 2)
        arcade.draw_text("FUSION STATION", cx, py + ph - 26,
                         (255, 225, 100, 255), font_size=22, bold=True,
                         anchor_x="center", anchor_y="center")

        # Drei Spalten-Layout
        gap = 10
        left_w  = 230
        right_w = 230
        mid_w   = pw - left_w - right_w - gap * 4

        left_x  = px + gap
        mid_x   = left_x + left_w + gap
        right_x = mid_x + mid_w + gap

        top_y    = py + ph - 62
        bottom_y = py + 44

        # Spalten-Trennlinien
        for lx in (mid_x - gap // 2, right_x - gap // 2):
            arcade.draw_line(lx, top_y, lx, bottom_y, (120, 90, 40, 120), 1)

        # Spalten-Ueberschriften
        for sx, sw, title, col in [
            (left_x,  left_w,  "KARTEN-INVENTAR", (220, 185, 80, 255)),
            (mid_x,   mid_w,   "FUSION WERKZEUG", (255, 220, 100, 255)),
            (right_x, right_w, "RUNEN-INVENTAR",  (180, 240, 255, 255)),
        ]:
            hdr_cx = sx + sw // 2
            arcade.draw_rect_filled(arcade.XYWH(hdr_cx, top_y + 15, sw - 4, 28), (90, 58, 22, 210))
            arcade.draw_rect_outline(arcade.XYWH(hdr_cx, top_y + 15, sw - 4, 28), col[:3] + (150,), 1)
            arcade.draw_text(title, hdr_cx, top_y + 15, col,
                             font_size=10, bold=True, anchor_x="center", anchor_y="center")

        col_h = top_y - bottom_y - 28
        self._draw_card_column(left_x,  top_y - 14, left_w,  col_h)
        self._draw_workshop(   mid_x,   top_y - 14, mid_w,   col_h, cy)
        self._draw_rune_column(right_x, top_y - 14, right_w, col_h)

        # Fusszeile
        arcade.draw_text(
            "Karte/Rune anklicken zum Hinzufuegen  |  Slot anklicken zum Zurueckgeben  |  ESC: Schliessen",
            cx, py + 16, (145, 140, 130, 200), font_size=9, anchor_x="center")

    # ── Linke Spalte: Karten-Inventar ────────────────────────────────────
    def _draw_card_column(self, col_x: float, top_y: float, col_w: float, col_h: float):
        if not self.game:
            return
        items = list(self.game.inventory.cards.items())
        card_h = 34
        pad = 5
        col_cx = col_x + col_w // 2
        for i, (card_id, count) in enumerate(items[:12]):
            card = self.game.cards_db.get(card_id)
            if not card:
                continue
            cy = top_y - i * (card_h + pad) - card_h // 2
            if cy < top_y - col_h:
                break
            rect = (col_x + 3, cy - card_h // 2, col_x + col_w - 3, cy + card_h // 2)
            self.card_inventory_rects.append((rect[0], rect[1], rect[2], rect[3], card_id))
            selected = (self.crafting_station.slot.card_id == card_id)
            bg  = (165, 115, 50, 245) if selected else (85, 55, 25, 220)
            brd = (255, 225, 95, 255) if selected else (130, 90, 38, 180)
            arcade.draw_rect_filled(arcade.XYWH(col_cx, cy, col_w - 6, card_h), bg)
            arcade.draw_rect_outline(arcade.XYWH(col_cx, cy, col_w - 6, card_h), brd, 2)
            rarity_col = {
                "common": (200, 200, 200, 255), "uncommon": (80, 210, 80, 255),
                "rare": (80, 145, 230, 255), "epic": (185, 80, 205, 255),
                "legendary": (225, 195, 55, 255),
            }.get(card.rarity, (200, 200, 200, 255))
            arcade.draw_rect_filled(arcade.XYWH(col_x + 5, cy, 4, card_h - 4), rarity_col)
            arcade.draw_text(f"{card.name[:17]}  x{count}", col_cx + 3, cy,
                             (255, 245, 210, 255), font_size=9,
                             anchor_x="center", anchor_y="center")

    # ── Rechte Spalte: Runen-Inventar ─────────────────────────────────────
    def _draw_rune_column(self, col_x: float, top_y: float, col_w: float, col_h: float):
        rune_h = 34
        pad = 5
        col_cx = col_x + col_w // 2
        for i, rune in enumerate(self.rune_inventory.runes):
            cy = top_y - i * (rune_h + pad) - rune_h // 2
            if cy < top_y - col_h:
                break
            rect = (col_x + 3, cy - rune_h // 2, col_x + col_w - 3, cy + rune_h // 2)
            self.rune_inventory_rects.append((rect[0], rect[1], rect[2], rect[3], rune.rune_type))
            rc = self.RUNE_COLORS.get(rune.rune_type, (180, 180, 180, 255))
            bg  = (rc[0] // 4, rc[1] // 4, rc[2] // 4, 220)
            brd = rc
            arcade.draw_rect_filled(arcade.XYWH(col_cx, cy, col_w - 6, rune_h), bg)
            arcade.draw_rect_outline(arcade.XYWH(col_cx, cy, col_w - 6, rune_h), brd, 2)
            arcade.draw_rect_filled(arcade.XYWH(col_x + 5, cy, 4, rune_h - 4), rc)
            arcade.draw_text(rune.display_name, col_cx + 3, cy, rc,
                             font_size=9, anchor_x="center", anchor_y="center")

    # ── Mittlere Spalte: Fusion-Werkzeug ──────────────────────────────────
    def _draw_workshop(self, col_x: float, top_y: float, col_w: float, col_h: float, screen_cy: float):
        col_cx = col_x + col_w // 2
        y = top_y

        # --- Karten-Slot ---
        slot_w = col_w - 20
        slot_h = 58
        y -= slot_h // 2
        self.card_slot_rect = (col_cx - slot_w // 2, y - slot_h // 2,
                               col_cx + slot_w // 2, y + slot_h // 2)
        has_card = self.crafting_station.slot.card_type is not None
        bg_card  = (110, 70, 28, 240) if has_card else (55, 35, 15, 210)
        brd_card = (230, 180, 65, 255) if has_card else (130, 95, 42, 180)
        arcade.draw_rect_filled(arcade.XYWH(col_cx, y, slot_w, slot_h), bg_card)
        arcade.draw_rect_outline(arcade.XYWH(col_cx, y, slot_w, slot_h), brd_card, 2)
        arcade.draw_text("KARTE", col_cx, y + slot_h // 2 - 9,
                         (180, 150, 55, 200), font_size=8, anchor_x="center")
        if has_card:
            cname = self.crafting_station.slot.card_type.value.replace("_", " ").title()
            arcade.draw_text(cname, col_cx, y - 5,
                             (255, 255, 200, 255), font_size=12, bold=True,
                             anchor_x="center", anchor_y="center")
        else:
            arcade.draw_text("Leer  (Klick = Zurueck)", col_cx, y - 5,
                             (130, 115, 85, 180), font_size=8,
                             anchor_x="center", anchor_y="center")
        y -= slot_h // 2 + 10

        # --- Verbindungs-Plus ---
        arcade.draw_text("+", col_cx, y - 8,
                         (200, 185, 100, 200), font_size=16, anchor_x="center", anchor_y="center")
        y -= 22

        # --- 3 Runen-Slots ---
        rs = 46
        total_rw = rs * 3 + 10 * 2
        base_rx  = col_cx - total_rw // 2 + rs // 2
        rune_y   = y - rs // 2
        self.rune_slot_rect = (col_cx - total_rw // 2, rune_y - rs // 2,
                               col_cx + total_rw // 2, rune_y + rs // 2)
        for ri in range(3):
            rx = base_rx + ri * (rs + 10)
            filled = ri < len(self.crafting_station.slot.runes)
            if filled:
                rt = self.crafting_station.slot.runes[ri]
                rc = self.RUNE_COLORS.get(rt, (180, 180, 180, 255))
                bg_r  = (rc[0] // 3, rc[1] // 3, rc[2] // 3, 230)
                brd_r = rc
                lbl   = rt.value[:3].upper()
                lbl_c = rc
            else:
                bg_r  = (50, 32, 14, 200)
                brd_r = (110, 80, 35, 180)
                lbl   = str(ri + 1)
                lbl_c = (110, 95, 65, 170)
            arcade.draw_rect_filled(arcade.XYWH(rx, rune_y, rs, rs), bg_r)
            arcade.draw_rect_outline(arcade.XYWH(rx, rune_y, rs, rs), brd_r, 2)
            arcade.draw_text(lbl, rx, rune_y,
                             lbl_c, font_size=10, bold=filled,
                             anchor_x="center", anchor_y="center")
        y -= rs // 2 + 14

        # --- Fusion-Vorschau ---
        if self.crafting_station.fusion_in_progress and self.crafting_station.current_fusion:
            fname = self.crafting_station.current_fusion.fusion_name
            arcade.draw_text(f"Fusion: {fname}", col_cx, y - 8,
                             (255, 215, 60, 255), font_size=11, bold=True,
                             anchor_x="center", anchor_y="center")
        elif self.crafting_station.slot.is_valid():
            combo = Combination(
                card_type=self.crafting_station.slot.card_type,
                runes=self.crafting_station.slot.runes.copy()
            )
            arcade.draw_text(f"-> {combo.fusion_name}", col_cx, y - 8,
                             (255, 220, 80, 255), font_size=11, bold=True,
                             anchor_x="center", anchor_y="center")
        else:
            arcade.draw_text("Karte + Rune einlegen", col_cx, y - 8,
                             (130, 115, 85, 185), font_size=9,
                             anchor_x="center", anchor_y="center")
        y -= 30

        # --- Haupt-Button ---
        btn_w, btn_h = col_w - 20, 46
        btn_y = y - btn_h // 2
        self._draw_action_button(col_cx, btn_y, btn_w, btn_h)

    def _draw_action_button(self, cx: float, cy: float, bw: float, bh: float):
        cs = self.crafting_station
        if cs.fusion_in_progress:
            ready = cs.is_ready()
            if ready:
                self.start_claim_rect = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
                arcade.draw_rect_filled(arcade.XYWH(cx, cy, bw, bh), (45, 165, 55, 245))
                arcade.draw_rect_outline(arcade.XYWH(cx, cy, bw, bh), (100, 255, 110, 255), 3)
                arcade.draw_text("FUSION ABHOLEN!", cx, cy,
                                 (255, 255, 255, 255), font_size=13, bold=True,
                                 anchor_x="center", anchor_y="center")
            else:
                arcade.draw_rect_filled(arcade.XYWH(cx, cy, bw, bh), (55, 55, 80, 210))
                arcade.draw_rect_outline(arcade.XYWH(cx, cy, bw, bh), (90, 90, 130, 200), 2)
                arcade.draw_text("Boss besiegen...", cx, cy + 8,
                                 (170, 170, 210, 200), font_size=10,
                                 anchor_x="center", anchor_y="center")
                # Fortschrittsbalken
                bar_y = cy - 12
                arcade.draw_rect_filled(arcade.XYWH(cx, bar_y, bw - 16, 12), (38, 38, 55, 220))
                arcade.draw_rect_filled(arcade.XYWH(cx - (bw - 16) / 2 + (bw - 16) * 0.25,
                                                     bar_y, (bw - 16) * 0.5, 12),
                                        (75, 130, 195, 220))
                arcade.draw_rect_outline(arcade.XYWH(cx, bar_y, bw - 16, 12), (90, 90, 130, 180), 1)
        else:
            active = cs.slot.is_valid()
            self.start_claim_rect = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
            bg  = (155, 98, 32, 245) if active else (65, 45, 25, 200)
            brd = (255, 205, 75, 255) if active else (115, 85, 40, 180)
            arcade.draw_rect_filled(arcade.XYWH(cx, cy, bw, bh), bg)
            arcade.draw_rect_outline(arcade.XYWH(cx, cy, bw, bh), brd, 3)
            lbl   = "FUSION STARTEN" if active else "Karte + Rune einlegen"
            lc    = (255, 245, 185, 255) if active else (145, 128, 100, 200)
            fsize = 13 if active else 10
            arcade.draw_text(lbl, cx, cy, lc, font_size=fsize, bold=active,
                             anchor_x="center", anchor_y="center")


CARD_SYSTEM_AVAILABLE = True

# ─── Einstellungen ────────────────────────────────────────────────────────
SCREEN_WIDTH,  SCREEN_HEIGHT = 1024, 768
SCREEN_TITLE   = "Frog Roguelike"
TILE_SIZE      = 16
ROOM_WIDTH,  ROOM_HEIGHT = 12, 10

PLAYER_SPEED      = 1.5
PLAYER_MAX_HP     = 8      # mehr Leben am Anfang
DAMAGE_COOLDOWN   = 0.9
SPAWN_PROTECTION  = 1.0      # Sekunden Unverwundbarkeit nach Raum-Eintritt

SHARD_SPEED       = 7.0
SHARD_COOLDOWN    = 0.35
SHARD_LIFETIME    = 3.0      # Sekunden bis Shard despawnt
ENEMY_BASE_SPEED  = 30.0
ORBIT_RADIUS      = 30.0
SHIELD_FORWARD = 16.0
DASH_DISTANCE = 64.0
DASH_DURATION = 0.12
DASH_COOLDOWN = 0.75
HIT_KNOCKBACK = 4.0
DAMAGE_FLASH_DURATION = 0.22
SHIELD_RADIUS = 18.0
SHIELD_KNOCKBACK = 22.0
SHIELD_TICK_INTERVAL = 0.2

CAMERA_ZOOM  = 3.5
CAMERA_LERP  = 0.14
AMBIENT_COLOR = (10, 10, 20, 255)

# Retro-Pixel-Font
PIXEL_FONT = "Courier New"

def draw_rectangle_filled(center_x, center_y, width, height, color):
    left = center_x - width / 2
    right = center_x + width / 2
    bottom = center_y - height / 2
    top = center_y + height / 2
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)


def draw_rectangle_outline(center_x, center_y, width, height, color, border_width=1):
    left = center_x - width / 2
    right = center_x + width / 2
    bottom = center_y - height / 2
    top = center_y + height / 2
    arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, border_width)

# HP-Herzen Positionen
HP_W, HP_H, HP_GAP = 18, 18, 5
HP_X, HP_Y = 20, SCREEN_HEIGHT - 30

# Farbkarten für Seltenheit
RARITY_COLORS = {
    "common": (200, 200, 200, 220),
    "uncommon": (80, 200, 80, 220),
    "rare": (80, 140, 220, 220),
    "epic": (180, 80, 200, 220),
    "legendary": (220, 190, 60, 220),
}
COIN_COSTS = {
    "common": 5,
    "uncommon": 12,
    "rare": 25,
    "epic": 55,
    "legendary": 110,
}

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────
def split_every_n_words(text: str, n: int):
    """Split text into lines with n words each."""
    words = text.split()
    lines = []
    for i in range(0, len(words), n):
        lines.append(" ".join(words[i:i+n]))
    return "\n".join(lines)

# ─── Card / Inventory System ──────────────────────────────────────────────
class Card:
    def __init__(self, id, name, desc, rarity, kind, apply_fn, bad_fn,
                 buff_text="", bad_text="", icon=None, price=0, shop_enabled=True):
        self.id = id
        self.name = name
        self.desc = desc
        self.rarity = rarity        # "common","uncommon","rare","epic","legendary"
        self.kind = kind            # "shot" or "buff"
        self.apply_fn = apply_fn    # called when used (LMB/RMB)
        self.bad_fn = bad_fn        # called when bought (permanent for run)
        self.buff_text = buff_text  # short human text for buff (shown green)
        self.bad_text = bad_text    # short human text for bad (shown red)
        self.icon = icon
        self.price = price
        self.shop_enabled = shop_enabled

class Inventory:
    def __init__(self):
        self.cards = {}  # id -> count

    def add(self, card_id, n=1):
        self.cards[card_id] = self.cards.get(card_id, 0) + n

    def remove(self, card_id, n=1):
        if card_id in self.cards:
            self.cards[card_id] = max(0, self.cards[card_id] - n)
            if self.cards[card_id] == 0:
                del self.cards[card_id]

    def count(self, card_id):
        return self.cards.get(card_id, 0)

class EquipSlot:
    def __init__(self):
        self.card_id = None
        self.charges = 0

    def is_empty(self):
        return self.card_id is None

    def use_charge(self):
        if self.charges > 0:
            self.charges -= 1

# ─── Shard (Spieler-Projektil) ─────────────────────────────────────────────
class Shard(arcade.Sprite):
    def __init__(self, texture, angle_rad, speed, is_piercing,
                 lifetime=SHARD_LIFETIME):
        super().__init__(texture, scale=1.0)
        self.angle      = math.degrees(angle_rad)
        self.change_x   = math.cos(angle_rad) * speed
        self.change_y   = math.sin(angle_rad) * speed
        self.is_piercing = is_piercing
        self.lifetime   = lifetime
        self.timer      = 0.0
        self.light      = None   # wird im View zugewiesen
        self.is_fragment = False

# ─── Raum ─────────────────────────────────────────────────────────────────
class Room:
    def __init__(self, grid_x, grid_y):
        self.grid_x, self.grid_y = grid_x, grid_y
        self.width, self.height  = ROOM_WIDTH, ROOM_HEIGHT
        self.passages  = []
        self.cleared   = False
        self.visited   = False
        self.is_boss_room = False
        self.is_escape_room = False
        self.is_shop_room = False
        self.tiles = [["floor"] * self.width for _ in range(self.height)]
        for y in range(self.height):
            self.tiles[y][0] = self.tiles[y][self.width - 1] = "wall"
        for x in range(self.width):
            self.tiles[0][x] = self.tiles[self.height - 1][x] = "wall"

    def get_pixel_pos(self):
        return self.grid_x * self.width * TILE_SIZE, self.grid_y * self.height * TILE_SIZE

    def center_world(self):
        px, py = self.get_pixel_pos()
        return px + self.width * TILE_SIZE / 2, py + self.height * TILE_SIZE / 2

    def contains(self, wx, wy):
        px, py = self.get_pixel_pos()
        return (px <= wx <= px + self.width  * TILE_SIZE and
                py <= wy <= py + self.height * TILE_SIZE)

    def create_passages(self, other):
        dx, dy = other.grid_x - self.grid_x, other.grid_y - self.grid_y
        my, mx  = self.height // 2, self.width // 2
        if   dx ==  1: self.tiles[my][self.width - 1] = "floor"; self.passages.append((self.width - 1, my))
        elif dx == -1: self.tiles[my][0]              = "floor"; self.passages.append((0, my))
        elif dy ==  1: self.tiles[self.height - 1][mx]= "floor"; self.passages.append((mx, self.height - 1))
        elif dy == -1: self.tiles[0][mx]              = "floor"; self.passages.append((mx, 0))

# ─── Gegner ────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y, body_tex, attack_tex, room, light_layer, is_boss=False):
        self.room = room
        self.body = arcade.Sprite(body_tex, scale=1.0)
        self.body.center_x = x
        self.body.center_y = y
        self.hp = 20 if not is_boss else 80
        self.max_hp = self.hp
        self.is_boss = is_boss
        self.behavior = random.choice(["chaser", "ravager", "circler", "blocker"])
        self.wander_t = random.random() * 10
        self.circle_dir = random.choice([1, -1])
        self.frenzy = False
        self.speed_multiplier = 1.0
        self.hit_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_timer = 0.0
        self.dash_dir = (0.0, 0.0)
        self.dash_warning_timer = 0.0
        self.dash_target = None
        self.is_dashing = False
        self.block_side = random.choice([-1, 1])
        self.base_color = (255, 255, 255)
        if self.behavior == "blocker":
            self.base_color = (160, 220, 255)
        self.body.color = self.base_color

        n_orb = 6 if is_boss else 3
        self.orbiters = arcade.SpriteList()
        for _ in range(n_orb):
            self.orbiters.append(arcade.Sprite(attack_tex, scale=1.0))

        self.orbit_angle = random.uniform(0, 6.28)

        l_col = (255, 0, 0) if is_boss else (200, 60, 60)
        self.light = Light(x, y, radius=110 if is_boss else 55,
                           color=l_col, mode="soft")
        light_layer.add(self.light)

    # ── Lebensleiste über dem Kopf (in Weltkoordinaten) ──────────────────
    def draw_health_bar(self):
        w = 30 if self.is_boss else 20
        h = 4
        x = self.body.center_x
        y = self.body.top + 7

        arcade.draw_rect_filled(arcade.XYWH(x, y, w, h), (40, 0, 0, 230))
        fill_w = w * (self.hp / self.max_hp)
        if fill_w > 0:
            col = (60, 220, 60) if self.hp > self.max_hp // 2 else (220, 40, 40)
            arcade.draw_rect_filled(
                arcade.XYWH(x - w / 2 + fill_w / 2, y, fill_w, h), col)
        arcade.draw_rect_outline(arcade.XYWH(x, y, w, h), (255, 255, 255, 130), 1)

    # ── KI-Update ───────────────────────────────────────────────────────
    def update(self, delta_time, px, py, pvx=0.0, pvy=0.0):
        dx = px - self.body.center_x
        dy = py - self.body.center_y
        dist = math.hypot(dx, dy)

        # Frenzy bei halber HP
        if self.hp <= self.max_hp // 2 and not self.frenzy:
            self.frenzy = True
            self.base_color = (255, 110, 110)
            self.body.color = self.base_color
            self.light.color = (255, 30, 30)

        if self.hit_timer > 0.0:
            self.hit_timer = max(0.0, self.hit_timer - delta_time)
            if self.hit_timer == 0.0:
                self.body.color = self.base_color

        speed = (ENEMY_BASE_SPEED * delta_time
                 * (1.7 if self.frenzy else 1.0)
                 * (1.5 if self.is_boss else 1.0)
                 * self.speed_multiplier)

        if dist > 1 and dist < 650:
            angle = math.atan2(dy, dx)

            if self.behavior == "chaser":
                self.body.center_x += math.cos(angle) * speed
                self.body.center_y += math.sin(angle) * speed

            elif self.behavior == "ravager":
                self.wander_t += delta_time * 4.0
                zigzag = math.sin(self.wander_t) * 0.55
                a = angle + zigzag
                self.body.center_x += math.cos(a) * speed
                self.body.center_y += math.sin(a) * speed

            elif self.behavior == "circler":
                perp = angle + self.circle_dir * math.pi / 2
                mx_ = math.cos(angle) * 0.3 + math.cos(perp) * 0.7
                my_ = math.sin(angle) * 0.3 + math.sin(perp) * 0.7
                length = math.hypot(mx_, my_) or 1
                self.body.center_x += (mx_ / length) * speed
                self.body.center_y += (my_ / length) * speed
                if random.random() < 0.004:
                    self.circle_dir *= -1

            elif self.behavior == "blocker":
                if self.dash_warning_timer > 0.0:
                    self.dash_warning_timer -= delta_time
                    if self.dash_warning_timer <= 0.0 and self.dash_target is not None:
                        desired_distance = 128.0
                        self.dash_speed = 640.0 if not self.frenzy else 800.0
                        self.dash_timer = desired_distance / self.dash_speed
                        self.dash_dir = ((self.dash_target[0] - self.body.center_x) / max(1e-6, math.hypot(self.dash_target[0] - self.body.center_x, self.dash_target[1] - self.body.center_y)),
                                         (self.dash_target[1] - self.body.center_y) / max(1e-6, math.hypot(self.dash_target[0] - self.body.center_x, self.dash_target[1] - self.body.center_y)))
                        self.dash_target = None
                        self.is_dashing = True
                elif self.dash_timer > 0.0:
                    self.is_dashing = True
                    self.body.center_x += self.dash_dir[0] * self.dash_speed * delta_time
                    self.body.center_y += self.dash_dir[1] * self.dash_speed * delta_time
                    self.dash_timer -= delta_time
                    if self.dash_timer <= 0.0:
                        self.dash_timer = 0.0
                        self.dash_cooldown = 1.6 if not self.frenzy else 1.0
                        self.is_dashing = False
                else:
                    self.is_dashing = False
                    if self.dash_cooldown > 0.0:
                        self.dash_cooldown -= delta_time

                    # Block the player's path by moving just ahead of them and flanking.
                    perp = angle + self.block_side * math.pi / 2
                    block_x = px - math.cos(angle) * 40 + math.cos(perp) * 18
                    block_y = py - math.sin(angle) * 40 + math.sin(perp) * 18
                    move_angle = math.atan2(block_y - self.body.center_y,
                                            block_x - self.body.center_x)
                    self.body.center_x += math.cos(move_angle) * speed * 1.15
                    self.body.center_y += math.sin(move_angle) * speed * 1.15

                    if dist < 160.0 and self.dash_cooldown <= 0.0:
                        self.dash_warning_timer = 0.45
                        lookahead = 0.4
                        predicted_x = px + (pvx / max(1e-6, delta_time)) * lookahead
                        predicted_y = py + (pvy / max(1e-6, delta_time)) * lookahead
                        self.dash_target = (predicted_x, predicted_y)

        # Innerhalb Raumgrenzen halten
        rx, ry = self.room.get_pixel_pos()
        m = TILE_SIZE + 2
        self.body.left   = max(self.body.left,   rx + m)
        self.body.right  = min(self.body.right,  rx + self.room.width  * TILE_SIZE - m)
        self.body.bottom = max(self.body.bottom, ry + m)
        self.body.top    = min(self.body.top,    ry + self.room.height * TILE_SIZE - m)

        # Licht + Orbiters
        self.light.position = self.body.position
        self.orbit_angle   += (8.0 if self.frenzy else 3.5) * delta_time
        r = ORBIT_RADIUS * (1.8 if self.is_boss else 1.0)
        n = len(self.orbiters)
        for i, spr in enumerate(self.orbiters):
            a = self.orbit_angle + i * (2 * math.pi / n)
            spr.center_x = self.body.center_x + math.cos(a) * r
            spr.center_y = self.body.center_y + math.sin(a) * r

class HandEnemy:
    def __init__(self, x, y, body_tex, room, light_layer, is_boss=False):
        self.room = room
        self.body = arcade.Sprite(body_tex, scale=1.0)
        self.body.center_x = x
        self.body.center_y = y
        self.hp = 3
        self.max_hp = 3
        self.is_boss = is_boss
        self.behavior = "hand"
        self.orbiters = arcade.SpriteList()
        self.hit_timer = 0.0
        self.base_color = (220, 220, 255)
        self.body.color = self.base_color
        self.light = Light(x, y, radius=60, color=(200, 180, 240), mode="soft")
        light_layer.add(self.light)
        self.immune_in_air = True
        self.hover_height = 80.0
        self.hover_x_offset = random.uniform(-14, 14)
        self.prep_timer = 0.0
        self.hold_timer = 0.0
        self.on_ground_timer = 0.0
        self.stomp_fall_timer = 0.0
        self.stomp_fall_duration = 0.18
        self.stomp_start = (x, y)
        self.stomp_target = (x, y)
        self.stomp_cooldown = random.uniform(1.5, 3.0)
        self.pending_stomp = False
        self.shake_center = (x, y)

    def draw_health_bar(self):
        w = 20
        h = 4
        x = self.body.center_x
        y = self.body.top + 7
        arcade.draw_rect_filled(arcade.XYWH(x, y, w, h), (40, 0, 0, 230))
        fill_w = w * (self.hp / self.max_hp)
        if fill_w > 0:
            col = (60, 220, 60) if self.hp > self.max_hp // 2 else (220, 40, 40)
            arcade.draw_rect_filled(arcade.XYWH(x - w / 2 + fill_w / 2, y, fill_w, h), col)
        arcade.draw_rect_outline(arcade.XYWH(x, y, w, h), (255, 255, 255, 130), 1)

    def update(self, delta_time, px, py, pvx=0.0, pvy=0.0):
        # timers
        if self.hit_timer > 0.0:
            self.hit_timer = max(0.0, self.hit_timer - delta_time)
            if self.hit_timer == 0.0:
                self.body.color = self.base_color

        if self.on_ground_timer > 0.0:
            # stay on ground vulnerable
            self.on_ground_timer -= delta_time
            if self.on_ground_timer <= 0.0:
                self.on_ground_timer = 0.0
                self.immune_in_air = True
                self.stomp_cooldown = 2.5
        elif self.prep_timer > 0.0:
            # trembling before stomp
            self.prep_timer -= delta_time
            shake = math.sin(self.prep_timer * 50.0) * 2.5
            self.body.center_x = self.shake_center[0] + shake
            self.body.center_y = self.shake_center[1]
            if self.prep_timer <= 0.0:
                self.prep_timer = 0.0
                self.body.center_x, self.body.center_y = self.shake_center
                self.hold_timer = 0.2
        elif self.hold_timer > 0.0:
            self.hold_timer -= delta_time
            self.body.center_x, self.body.center_y = self.shake_center
            if self.hold_timer <= 0.0:
                self.hold_timer = 0.0
                self.stomp_start = self.shake_center
                self.stomp_target = (self.shake_center[0], self.shake_center[1] - self.hover_height)
                self.stomp_fall_timer = self.stomp_fall_duration
                self.immune_in_air = True
        elif self.stomp_fall_timer > 0.0:
            self.stomp_fall_timer -= delta_time
            t = 1.0 - max(0.0, self.stomp_fall_timer) / self.stomp_fall_duration
            self.body.center_x = self.stomp_start[0] + (self.stomp_target[0] - self.stomp_start[0]) * t
            self.body.center_y = self.stomp_start[1] + (self.stomp_target[1] - self.stomp_start[1]) * t
            if self.stomp_fall_timer <= 0.0:
                self.stomp_fall_timer = 0.0
                self.pending_stomp = True
                self.on_ground_timer = 4.0
                self.immune_in_air = False
        else:
            # hovering above the player
            self.stomp_cooldown = max(0.0, self.stomp_cooldown - delta_time)
            target_x = px + self.hover_x_offset
            target_y = py + self.hover_height
            # smooth follow
            self.body.center_x += (target_x - self.body.center_x) * min(8.0 * delta_time, 1.0)
            self.body.center_y += (target_y - self.body.center_y) * min(8.0 * delta_time, 1.0)
            # occasionally prepare stomp
            if self.stomp_cooldown <= 0.0 and random.random() < 0.012:
                self.prep_timer = 0.5
                self.hold_timer = 0.0
                self.stomp_cooldown = 3.0
                self.shake_center = (self.body.center_x, self.body.center_y)
                self.ahpx = px
                self.ahpy = py
                self.stomp_target = (self.ahpx, self.ahpy)

# ─── Karten-Datenbank (Beispiele) ────────────────────────────────────────
def make_cards_db():
    db = {}

    def apply_normal_shot(game):
        game.player_shot_mode = "normal"

    def bad_none(game):
        pass

    db["normal_shot"] = Card(
        "normal_shot", "Normal Shot",
        "Gezielter Schuss ohne Nachteile.",
        "common", "shot", apply_normal_shot, bad_none,
        buff_text="Zuverlässig präzise", bad_text="Keine",
        icon="normal shot.png", price=10)

    def apply_shotgun(game):
        game.player_shot_mode = "shotgun"

    def bad_shotgun(game):
        game.player_speed_multiplier *= 0.95

    db["shotgun"] = Card(
        "shotgun", "Splitter Shot",
        "Feuert mehrere Shards fächerförmig. Hoher Schaden.",
        "rare", "shot", apply_shotgun, bad_shotgun,
        buff_text="5 Projektil-Spread", bad_text="-5% Bewegung",
        icon="shotgun.png", price=18)

    def apply_cluster(game):
        game.player_shot_mode = "cluster"
        game.cluster_timer = 0.0

    def bad_cluster(game):
        game.player_max_hp = max(1, game.player_max_hp - 10)

    db["cluster"] = Card(
        "cluster", "Spin Shot",
        "Projketile spinnen um dich herum und treffen Gegner im Nahbereich.",
        "epic", "shot", apply_cluster, bad_cluster,
        buff_text="Proj. drehen um dich", bad_text="-10 Max HP",
        icon="spin.png", price=28)

    def apply_shockwave(game):
        game.do_shockwave()

    def bad_shockwave(game):
        game.attack_speed_multiplier *= 1.15

    db["shockwave"] = Card(
        "shockwave", "Shockwave",
        "8 Projektile in alle Richtungen. 5s Cooldown.",
        "epic", "shot", apply_shockwave, bad_shockwave,
        buff_text="8-way radial", bad_text="-15% Angriffsgeschw.",
        icon=None, price=45, shop_enabled=False)

    def apply_invinc(game):
        game.activate_invincibility(12.0)

    def bad_invinc(game):
        game.player_max_hp = max(1, game.player_max_hp - 3)

    db["invinc"] = Card(
        "invinc", "Invincibility",
        "12s Unverwundbarkeit (RMB). Teure Strafe.",
        "legendary", "buff", apply_invinc, bad_invinc,
        buff_text="12s Schutzschild", bad_text="-3 Max HP",
        icon="invincibilyti.png", price=55)

    def apply_shield(game):
        pass

    def bad_shield(game):
        game.player_speed_multiplier *= 0.95

    db["shield"] = Card(
        "shield", "Shield",
        "Aktiviert einen Energieschild 30 Pixel vor dir. Drückt Gegner zurück, verursacht keinen Schaden.",
        "epic", "buff", apply_shield, bad_shield,
        buff_text="Schützt und stößt zurück", bad_text="-5% Bewegung",
        icon="shield.png", price=40)

    def apply_lifeup(game):
        game.hp = min(game.player_max_hp, game.hp + 2)
        game.player_max_hp = game.player_max_hp + 1

    def bad_lifeup(game):
        game.cooldown_multiplier *= 1.02

    db["lifeup"] = Card(
        "lifeup", "Life Up",
        "Heilt dich und erhöht deine maximale Gesundheit.",
        "common", "buff", apply_lifeup, bad_lifeup,
        buff_text="+1 Max HP, +2 Heal", bad_text="+2% Cooldown",
        icon="life up.png", price=12)

    return db

# ─── Hauptspiel-View ───────────────────────────────────────────────────────
class GameView(arcade.View):
    def __init__(self, difficulty=1):
        super().__init__()
        self.difficulty = difficulty
        self.setup()

    def setup(self):
        # Automatischer Basispfad direkt in den "assets"-Ordner
        bp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

        def load(n):
            return arcade.load_texture(os.path.join(bp, n))

        def load_safe(n, fallback_color):
            try:
                return load(n)
            except Exception:
                return arcade.Texture.create_empty(n, (TILE_SIZE, TILE_SIZE), color=fallback_color)

        # Sicheres Laden der Texturen
        self.tex_floor  = load_safe("floor.png", (40, 40, 50))
        self.tex_wall   = load_safe("wall.png", (20, 20, 30))
        self.tex_p      = {"up":   load_safe("frog_w.png", (40, 180, 40)),
                           "down": load_safe("frog_s.png", (40, 180, 40)),
                           "side": load_safe("frog_l_r.png", (40, 180, 40))}
        self.tex_eye    = load_safe("eye.png", (200, 40, 40))
        self.tex_atk    = load_safe("attack.png", (220, 60, 60))
        self.tex_staff  = load_safe("staff.png", (130, 90, 40))
        self.tex_shard  = load_safe("shard.png", (100, 200, 255))
        self.tex_shield = load_safe("shield.png", (180, 180, 220))
        self.tex_brain  = load_safe("brain.png", (160, 220, 255))
        self.tex_hand   = load_safe("hand.png", (220, 200, 160))

        # Sprite-Listen
        self.wall_list       = arcade.SpriteList(use_spatial_hash=True)
        self.floor_list      = arcade.SpriteList()
        self.blocker_list    = arcade.SpriteList()
        self.player_list     = arcade.SpriteList()
        self.staff_list      = arcade.SpriteList()
        self.shard_list      = arcade.SpriteList()
        self.shield_list     = arcade.SpriteList()
        self.particle_list   = arcade.SpriteList()
        self.enemy_sprites   = arcade.SpriteList()
        self.orbiter_sprites = arcade.SpriteList()
        self.enemy_shockwaves = []

        # Kamera
        self.camera    = arcade.camera.Camera2D()
        self.camera.zoom = CAMERA_ZOOM
        self.ui_camera = arcade.camera.Camera2D()

        # Beleuchtung
        self.light_layer  = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_light = Light(0, 0, radius=130,
                                  color=(200, 150, 255), mode="soft")
        self.light_layer.add(self.player_light)

        # Spieler-Sprite
        self.player = arcade.Sprite(self.tex_p["down"], scale=1.0)
        if hasattr(self.player, "set_hit_box"):
            self.player.set_hit_box([(-6, -6), (6, -6), (6, 6), (-6, 6)])
        self.player_list.append(self.player)

        # Staff-Sprite
        self.staff = arcade.Sprite(self.tex_staff, scale=1.0)
        self.staff_list.append(self.staff)

        # Shield-Visual
        self.shield_sprite = arcade.Sprite(self.tex_shield, scale=1.0)
        self.shield_sprite.visible = False
        self.shield_list.append(self.shield_sprite)

        # Spieler-Zustand
        if self.difficulty == 1:
            self.player_max_hp = 10
        elif self.difficulty == 2:
            self.player_max_hp = 8
        else:
            self.player_max_hp = 5
        self.hp        = self.player_max_hp
        self.player_shot_mode = "normal"
        self.shot_count = 1
        self.game_over = False
        self.win       = False

        # Multiplikatoren
        self.enemy_speed_multiplier = 1.0
        self.cooldown_multiplier = 1.0
        self.attack_speed_multiplier = 1.0
        self.player_speed_multiplier = 1.0

        # Steuerung
        self.mx, self.my  = 0, 0
        self.fire_mode    = 0
        self.shoot_timer  = 0.0
        self.dmg_timer    = 0.0
        self.protection_timer = 0.0
        self.shockwave_timer = 0.0
        self.shield_active = False
        self.shield_timer = 0.0
        self.dash_active = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_dir = (0.0, 0.0)
        self.screen_shake_timer = 0.0
        self._collision_probe = arcade.SpriteSolidColor(2, 2, (255, 255, 255))

        # Bewegung
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        # Dungeon-Daten
        self.rooms        = []
        self.enemies      = []
        self.current_room = None
        self.regen_timer  = 0.0

        # Card system
        self.cards_db = make_cards_db()
        self.inventory = Inventory()
        self.slot_primary = EquipSlot()   # LMB
        self.slot_secondary = EquipSlot() # RMB

        # Font + card textures
        font_path = os.path.join(bp, "BoldPixels.ttf")
        if os.path.exists(font_path):
            arcade.load_font(font_path)
            self.font = os.path.splitext(os.path.basename(font_path))[0]
        else:
            self.font = PIXEL_FONT

        self.card_textures = {}
        for card in self.cards_db.values():
            if card.icon:
                try:
                    self.card_textures[card.id] = load(os.path.join("cards", card.icon))
                except Exception:
                    self.card_textures[card.id] = arcade.Texture.create_empty(card.id, (TILE_SIZE, TILE_SIZE), color=(100, 100, 100))

        # UI state
        self.showing_shop = False
        self.shop_choices = []
        self.showing_inventory = False
        self.selected_inventory_card = None
        self.inv_page = 0          # 0=Karten  1=Runen  2=Fusionen
        self.inv_card_rects: List[tuple] = []
        self.inv_tab_rects:  List[tuple] = []
        self.shop_area = None
        self.inventory_area = None
        self.in_shop_hub = False
        self.hub_wait_timer = 0.0
        self.hub_wait_min = 2.0
        self.hub_can_return = False
        self.hub_shop_menu2 = False
        self.hub_shop_card_rects = []
        self.hub_shop_button_rect = None
        self.hub_craft_button_rect = None
        self.hub_skilltree_button_rect = None
        self.hub_inventory_button_rect = None
        self.hub_return_button_rect = None
        self.hub_refresh_button_rect = None
        self.hub_training_button_rect = None
        self.hub_inventory_open = False
        self.hub_inv_card_rects = []
        self.hub_inv_slot_rects = []
        self.hub_inv_selected_card = None
        self.teleport_boss_button_rect = None
        self.teleport_room_button_rect = None
        self.showing_dev_menu = False
        self.dev_menu_button_rect = None
        self.dev_menu_close_rect = None
        self.dev_menu_category: Optional[str] = None
        self.dev_menu_category_rects: List[tuple] = []
        self.dev_menu_sub_rects: List[tuple] = []
        self.dev_menu_button_pressed = None
        self.in_training_cage = False
        self.training_enemy_menu_open = False
        self.training_enemy_option_rects = []
        self.training_enemy_button_rect = None
        self.training_exit_rect = None

        self.start_difficulty = self.difficulty
        if self.start_difficulty == 1:
            self.player_max_hp = 10
        elif self.start_difficulty == 2:
            self.player_max_hp = 8
        else:
            self.player_max_hp = 5

        self.difficulty = self.start_difficulty
        self.boss_defeated = False
        self.coins = 20
        self.map_timer = 60.0
        self.minute_counter = 0
        self.first_shop_done = False
        self.timer_shop_opened = False
        self.pending_dungeon_after_shop = False

        # ─── Neues Card System Integration ────────────────────────────────
        if CARD_SYSTEM_AVAILABLE:
            # Crafting Station
            self.crafting_station = CraftingStation()
            self.rune_inventory = RuneInventory()
            
            # Skill Tree
            self.skill_tree = SkillTree()
            self.skill_tree.populate_unknown_combinations()
            self.skill_tree_ui = SkillTreeUI(self.skill_tree)
            
            # Mini-Map
            self.mini_map = MiniMap()
            self.mini_map_ui = MiniMapUI(self.mini_map)
            
            # Crafting Station UI
            self.crafting_station_ui = CraftingStationUI(self.crafting_station, self.rune_inventory, self)
            
            # Entdeckte Fusionen (für Skill Tree)
            self.discovered_combinations: Dict[str, Combination] = {}
            self.active_fusions: List[Combination] = []
            self.card_type_by_id = {
                "normal_shot": CardType.NORMAL_SHOT,
                "shotgun": CardType.SHOTGUN,
                "cluster": CardType.SPIN,
                "shield": CardType.SHIELD,
                "invinc": CardType.INVINCIBILITY,
                "lifeup": CardType.LIFE_UP,
            }
            self.card_id_by_type = {v: k for k, v in self.card_type_by_id.items()}
        else:
            self.crafting_station = None
            self.rune_inventory = None
            self.skill_tree = None
            self.skill_tree_ui = None
            self.mini_map = None
            self.mini_map_ui = None
            self.crafting_station_ui = None
            self.discovered_combinations = {}
            self.active_fusions = []
            self.card_type_by_id = {}
            self.card_id_by_type = {}

        self._generate_dungeon()
        self._build_world()

        # Startraum betreten
        start = self.rooms[0]
        self.player.position  = start.center_world()
        self.camera.position  = start.center_world()
        self.enter_room(start)

    def _build_training_room(self, room):
        px, py = room.get_pixel_pos()
        for y in range(room.height):
            for x in range(room.width):
                is_wall = x == 0 or x == room.width - 1 or y == 0 or y == room.height - 1
                spr = arcade.Sprite(self.tex_wall if is_wall else self.tex_floor)
                spr.left, spr.bottom = px + x * TILE_SIZE, py + y * TILE_SIZE
                (self.wall_list if is_wall else self.floor_list).append(spr)

    def _spawn_training_enemy(self, enemy_type):
        room = self.current_room
        if not room:
            return

        cx, cy = room.center_world()
        spawn_x = cx + random.uniform(-120, 120)
        spawn_y = cy + random.uniform(-60, 60)
        if enemy_type == "hand":
            e = HandEnemy(spawn_x, spawn_y, self.tex_hand, room, self.light_layer, False)
        elif enemy_type == "blocker":
            e = Enemy(spawn_x, spawn_y, self.tex_brain, self.tex_atk, room, self.light_layer, False)
            e.behavior = "blocker"
            e.base_color = (160, 220, 255)
            e.body.color = e.base_color
            e.orbiters = arcade.SpriteList()
        else:
            e = Enemy(spawn_x, spawn_y, self.tex_eye, self.tex_atk, room, self.light_layer, False)
            e.behavior = enemy_type
        e.natural_speed_multiplier = getattr(e, "speed_multiplier", 1.0)
        self.enemies.append(e)
        self.enemy_sprites.append(e.body)
        for o in e.orbiters:
            self.orbiter_sprites.append(o)

    def _clear_enemies(self):
        for e in list(self.enemies):
            if e.light in self.light_layer:
                self.light_layer.remove(e.light)
            e.body.remove_from_sprite_lists()
            for o in e.orbiters:
                o.remove_from_sprite_lists()
        self.enemies = []
        self.enemy_sprites = arcade.SpriteList()
        self.orbiter_sprites = arcade.SpriteList()

    # ─── Card System Helper Methods ────────────────────────────────────────
    def discover_combination(self, combination: Optional['Combination']):
        """Registriere eine entdeckte Kombination im Skill Tree"""
        if not CARD_SYSTEM_AVAILABLE or not combination or not self.skill_tree:
            return
        
        # Erstelle einen eindeutigen Schlüssel
        key = self.skill_tree._combination_key(combination)
        
        # Prüfe ob bereits entdeckt
        if key in self.discovered_combinations:
            return
        
        # Registriere als entdeckt
        self.discovered_combinations[key] = combination
        
        # Füge zum Skill Tree hinzu
        self.skill_tree.add_combination(combination)
        
        # Optional: Spieler-Feedback
        print(f"🎴 Neue Fusion entdeckt: {combination.fusion_name}!")
    
    def add_rune_to_inventory(self, rune_type: 'RuneType', stack_level: int = 1):
        """Füge eine Rune zum Inventar hinzu"""
        if not CARD_SYSTEM_AVAILABLE or not self.rune_inventory:
            return
        
        rune = Rune(rune_type, stack_level=stack_level)
        self.rune_inventory.add_rune(rune)
    
    def get_discovered_combinations_count(self) -> int:
        """Gebe die Anzahl entdeckter Kombinationen zurück"""
        return len(self.discovered_combinations)

    def active_fusions_for(self, card_type: 'CardType') -> List['Combination']:
        if not CARD_SYSTEM_AVAILABLE:
            return []
        return [fusion for fusion in self.active_fusions if fusion.card_type == card_type]

    def apply_claimed_fusion(self, combination: Optional['Combination']):
        if not CARD_SYSTEM_AVAILABLE or not combination:
            return
        key = self.skill_tree._combination_key(combination)
        if all(self.skill_tree._combination_key(f) != key for f in self.active_fusions):
            self.active_fusions.append(combination)
        self.discover_combination(combination)
        card_id = self.card_id_by_type.get(combination.card_type)
        if card_id:
            self.inventory.add(card_id)
        if combination.card_type == CardType.LIFE_UP:
            primary = combination.primary_rune
            power = combination.power_level
            if primary == RuneType.SHADOW:
                self.player_max_hp = max(1, self.player_max_hp - 1)
                self.attack_speed_multiplier *= 0.9
            else:
                self.player_max_hp += 1 + power
                self.hp = min(self.player_max_hp, self.hp + 1 + power)
            if primary == RuneType.WIND:
                self.player_speed_multiplier *= 1.0 + 0.08 * power
            elif primary == RuneType.FIRE:
                self.attack_speed_multiplier *= 0.95
            elif primary == RuneType.BLOOD:
                self.hp = min(self.player_max_hp, self.hp + power)

    def add_card_to_crafting(self, card_type: 'CardType'):
        if self.crafting_station and not self.crafting_station.fusion_in_progress:
            self.crafting_station.add_card(card_type)

    def add_card_id_to_crafting(self, card_id: str):
        if not self.crafting_station or self.crafting_station.fusion_in_progress:
            return
        card_type = self.card_type_by_id.get(card_id)
        if not card_type or self.inventory.count(card_id) <= 0:
            return
        if self.crafting_station.slot.card_id:
            self.inventory.add(self.crafting_station.slot.card_id)
        self.inventory.remove(card_id)
        self.crafting_station.add_card(card_type, card_id)

    def return_crafting_card(self):
        if not self.crafting_station or self.crafting_station.fusion_in_progress:
            return
        if self.crafting_station.slot.card_id:
            self.inventory.add(self.crafting_station.slot.card_id)
            self.crafting_station.slot.card_id = None
            self.crafting_station.slot.card_type = None

    def add_rune_to_crafting(self, rune_type: 'RuneType'):
        if not self.crafting_station or not self.rune_inventory:
            return
        if self.crafting_station.fusion_in_progress or len(self.crafting_station.slot.runes) >= 3:
            return
        if self.rune_inventory.consume_rune(rune_type):
            self.crafting_station.add_rune(rune_type)

    def return_crafting_runes(self):
        if not self.crafting_station or self.crafting_station.fusion_in_progress:
            return
        for rune_type in self.crafting_station.slot.runes:
            self.rune_inventory.add_rune(Rune(rune_type))
        self.crafting_station.slot.runes = []

    def complete_pending_fusion_after_boss(self):
        if self.crafting_station and self.crafting_station.fusion_in_progress:
            self.crafting_station.complete_after_boss()

    def handle_crafting_key(self, symbol) -> bool:
        if not CARD_SYSTEM_AVAILABLE or not self.crafting_station_ui or not self.crafting_station_ui.visible:
            return False
        if not self.in_shop_hub:
            return True
        card_keys = {
            arcade.key.KEY_1: CardType.NORMAL_SHOT,
            arcade.key.KEY_2: CardType.SHOTGUN,
            arcade.key.KEY_3: CardType.SPIN,
            arcade.key.KEY_4: CardType.SHIELD,
            arcade.key.KEY_5: CardType.INVINCIBILITY,
            arcade.key.KEY_6: CardType.LIFE_UP,
        }
        rune_keys = [arcade.key.F1, arcade.key.F2, arcade.key.F3, arcade.key.F4,
                     arcade.key.F5, arcade.key.F6, arcade.key.F7, arcade.key.F8]
        if symbol in card_keys:
            card_id = self.card_id_by_type.get(card_keys[symbol])
            if card_id:
                self.add_card_id_to_crafting(card_id)
            return True
        if symbol in rune_keys:
            idx = rune_keys.index(symbol)
            if self.rune_inventory and idx < len(self.rune_inventory.runes):
                self.add_rune_to_crafting(self.rune_inventory.runes[idx].rune_type)
            return True
        if symbol == arcade.key.BACKSPACE:
            if self.crafting_station and not self.crafting_station.fusion_in_progress:
                self.return_crafting_card()
                self.return_crafting_runes()
            return True
        if symbol == arcade.key.ENTER:
            if self.crafting_station.is_ready():
                self.apply_claimed_fusion(self.crafting_station.claim_fusion())
            elif not self.crafting_station.fusion_in_progress:
                self.crafting_station.start_crafting()
            return True
        return True

    def handle_crafting_click(self, x: float, y: float) -> bool:
        if not CARD_SYSTEM_AVAILABLE or not self.crafting_station_ui or not self.crafting_station_ui.visible:
            return False
        if not self.in_shop_hub:
            return True
        ui = self.crafting_station_ui
        if ui.card_slot_rect and self._rect_contains(ui.card_slot_rect, x, y):
            self.return_crafting_card()
            return True
        if ui.rune_slot_rect and self._rect_contains(ui.rune_slot_rect, x, y):
            self.return_crafting_runes()
            return True
        if ui.start_claim_rect and self._rect_contains(ui.start_claim_rect, x, y):
            if self.crafting_station.is_ready():
                self.apply_claimed_fusion(self.crafting_station.claim_fusion())
            elif not self.crafting_station.fusion_in_progress:
                self.crafting_station.start_crafting()
            return True
        for left, bottom, right, top, card_id in ui.card_inventory_rects:
            if left <= x <= right and bottom <= y <= top:
                self.add_card_id_to_crafting(card_id)
                return True
        for left, bottom, right, top, rune_type in ui.rune_inventory_rects:
            if left <= x <= right and bottom <= y <= top:
                self.add_rune_to_crafting(rune_type)
                return True
        return True

    def fusion_rune_counts(self, card_type: 'CardType') -> Dict['RuneType', int]:
        counts: Dict[RuneType, int] = {}
        for fusion in self.active_fusions_for(card_type):
            for rune, amount in fusion.rune_counts().items():
                counts[rune] = max(counts.get(rune, 0), amount)
        return counts

    def attach_fusion_to_shard(self, shard: Shard, card_type: 'CardType'):
        counts = self.fusion_rune_counts(card_type)
        shard.rune_counts = counts
        shard.damage_bonus = 0
        if not counts:
            return
        shard.damage_bonus = max(counts.values()) - 1
        if RuneType.WIND in counts:
            speedup = 1.0 + 0.18 * counts[RuneType.WIND]
            shard.change_x *= speedup
            shard.change_y *= speedup
        if RuneType.SHADOW in counts and random.random() < 0.18 * counts[RuneType.SHADOW]:
            shard.is_piercing = True
        if RuneType.ICE in counts:
            shard.color = (150, 220, 255)
        elif RuneType.FIRE in counts:
            shard.color = (255, 120, 60)
        elif RuneType.POISON in counts:
            shard.color = (120, 255, 120)
        elif RuneType.THUNDER in counts:
            shard.color = (240, 240, 90)
        elif RuneType.BLOOD in counts:
            shard.color = (220, 40, 80)
        elif RuneType.EXPLOSION in counts:
            shard.color = (255, 170, 60)
        elif RuneType.SHADOW in counts:
            shard.color = (170, 100, 230)

    def set_enemy_status(self, enemy, name: str, duration: float):
        if not hasattr(enemy, "status_timers"):
            enemy.status_timers = {}
            enemy.status_ticks = {}
        enemy.status_timers[name] = max(enemy.status_timers.get(name, 0.0), duration)

    def update_enemy_statuses(self, delta_time: float, dead_enemies: set):
        for e in list(self.enemies):
            timers = getattr(e, "status_timers", None)
            if not timers:
                continue
            for name in list(timers.keys()):
                timers[name] = max(0.0, timers[name] - delta_time)
                if name in ("burn", "poison"):
                    ticks = getattr(e, "status_ticks", {})
                    ticks[name] = ticks.get(name, 0.0) + delta_time
                    e.status_ticks = ticks
                    tick_time = 0.55 if name == "burn" else 0.75
                    if ticks[name] >= tick_time:
                        ticks[name] = 0.0
                        e.hp -= 1
                        e.hit_timer = DAMAGE_FLASH_DURATION
                        e.body.color = (255, 120, 80) if name == "burn" else (120, 255, 120)
                        if e.hp <= 0:
                            dead_enemies.add(id(e))
                if timers[name] <= 0.0:
                    del timers[name]
                    if name in ("slow", "frozen"):
                        e.speed_multiplier = getattr(e, "natural_speed_multiplier", 1.0)

    def damage_enemies_near(self, x: float, y: float, radius: float, damage: int, dead_enemies: set, exclude=None):
        for other in self.enemies:
            if other is exclude or other.room is not self.current_room:
                continue
            if math.hypot(other.body.center_x - x, other.body.center_y - y) <= radius:
                other.hp -= damage
                other.hit_timer = DAMAGE_FLASH_DURATION
                other.body.color = (255, 190, 90)
                if other.hp <= 0:
                    dead_enemies.add(id(other))

    def apply_rune_hit_effects(self, shard: Shard, enemy, dead_enemies: set):
        counts = getattr(shard, "rune_counts", {})
        if not counts:
            return
        if RuneType.ICE in counts:
            level = counts[RuneType.ICE]
            self.set_enemy_status(enemy, "frozen" if level >= 2 else "slow", 0.8 + level * 0.7)
            enemy.speed_multiplier = 0.0 if level >= 2 else min(enemy.speed_multiplier, 0.45)
        if RuneType.FIRE in counts:
            self.set_enemy_status(enemy, "burn", 1.5 + counts[RuneType.FIRE])
        if RuneType.POISON in counts:
            self.set_enemy_status(enemy, "poison", 2.0 + counts[RuneType.POISON])
        if RuneType.BLOOD in counts:
            if random.random() < 0.35 + 0.15 * counts[RuneType.BLOOD]:
                self.hp = min(self.player_max_hp, self.hp + 1)
        if RuneType.WIND in counts:
            length = math.hypot(shard.change_x, shard.change_y) or 1.0
            enemy.body.center_x += (shard.change_x / length) * 16 * counts[RuneType.WIND]
            enemy.body.center_y += (shard.change_y / length) * 16 * counts[RuneType.WIND]
        if RuneType.THUNDER in counts:
            jumps = 1 + counts[RuneType.THUNDER]
            nearby = sorted(
                [o for o in self.enemies if o is not enemy and o.room is self.current_room],
                key=lambda o: math.hypot(o.body.center_x - enemy.body.center_x, o.body.center_y - enemy.body.center_y)
            )[:jumps]
            for other in nearby:
                if math.hypot(other.body.center_x - enemy.body.center_x, other.body.center_y - enemy.body.center_y) < 95:
                    other.hp -= 1
                    other.hit_timer = DAMAGE_FLASH_DURATION
                    other.body.color = (240, 240, 100)
                    if other.hp <= 0:
                        dead_enemies.add(id(other))
        if RuneType.EXPLOSION in counts:
            self.damage_enemies_near(enemy.body.center_x, enemy.body.center_y, 34 + 14 * counts[RuneType.EXPLOSION], counts[RuneType.EXPLOSION], dead_enemies, exclude=enemy)
            self.screen_shake_timer = max(self.screen_shake_timer, 0.18)
        if RuneType.SHADOW in counts and random.random() < 0.18 * counts[RuneType.SHADOW]:
            enemy.hp -= 1 + counts[RuneType.SHADOW]
            if enemy.hp <= 0:
                dead_enemies.add(id(enemy))

    def apply_aura_fusions(self, delta_time: float, dead_enemies: set):
        inv_counts = self.fusion_rune_counts(CardType.INVINCIBILITY) if self.protection_timer > 0 else {}
        spin_counts = self.fusion_rune_counts(CardType.SPIN)
        aura_counts = inv_counts or spin_counts
        if not aura_counts:
            return
        radius = 46 if inv_counts else 34
        for e in self.enemies:
            if e.room is not self.current_room:
                continue
            dist = math.hypot(e.body.center_x - self.player.center_x, e.body.center_y - self.player.center_y)
            if dist > radius:
                continue
            if RuneType.ICE in aura_counts:
                self.set_enemy_status(e, "frozen", 0.7 + 0.5 * aura_counts[RuneType.ICE])
                e.speed_multiplier = 0.0 if aura_counts[RuneType.ICE] >= 2 else min(e.speed_multiplier, 0.5)
            if RuneType.FIRE in aura_counts:
                self.set_enemy_status(e, "burn", 1.0 + aura_counts[RuneType.FIRE])
            if RuneType.POISON in aura_counts:
                self.set_enemy_status(e, "poison", 1.5 + aura_counts[RuneType.POISON])
            if RuneType.BLOOD in aura_counts and random.random() < 0.015 * aura_counts[RuneType.BLOOD]:
                e.hp -= 1
                self.hp = min(self.player_max_hp, self.hp + 1)
            if RuneType.THUNDER in aura_counts and random.random() < 0.02 * aura_counts[RuneType.THUNDER]:
                e.hp -= 1
                e.body.color = (240, 240, 100)
            if RuneType.EXPLOSION in aura_counts and random.random() < 0.012 * aura_counts[RuneType.EXPLOSION]:
                self.damage_enemies_near(e.body.center_x, e.body.center_y, 42, 1, dead_enemies)
            if RuneType.WIND in aura_counts:
                # Tornado Spin: Gegner vom Spieler wegdrücken
                if dist > 0:
                    push = 2.5 * aura_counts[RuneType.WIND]
                    nx = (e.body.center_x - self.player.center_x) / dist
                    ny = (e.body.center_y - self.player.center_y) / dist
                    e.body.center_x += nx * push
                    e.body.center_y += ny * push
            if RuneType.SHADOW in aura_counts and random.random() < 0.008 * aura_counts[RuneType.SHADOW]:
                e.hp -= 2
            if e.hp <= 0:
                dead_enemies.add(id(e))

        # Vampire Heart (LIFE UP + BLOOD): passiver Lebensraub-Tick
        life_blood = self.fusion_rune_counts(CardType.LIFE_UP).get(RuneType.BLOOD, 0)
        if life_blood > 0 and random.random() < 0.006 * life_blood * delta_time * 60:
            if any(e.room is self.current_room for e in self.enemies):
                self.hp = min(self.player_max_hp, self.hp + 1)

    def start_training_cage(self):
        self._clear_enemies()
        self.in_training_cage = True
        self.training_enemy_menu_open = False
        self.training_enemy_option_rects = []
        self.training_exit_rect = None

        training_room = Room(999, 999)
        training_room.width = 30
        training_room.height = 30
        training_room.tiles = [["wall" if x == 0 or x == training_room.width - 1 or y == 0 or y == training_room.height - 1 else "floor"
                                for x in range(training_room.width)]
                               for y in range(training_room.height)]
        training_room.visited = True
        training_room.cleared = True
        self.current_room = training_room
        self.training_room = training_room
        self._build_training_room(training_room)
        self.player.position = training_room.center_world()
        self.camera.position = training_room.center_world()
        self.showing_dev_menu = False

    def exit_training_cage(self):
        self._clear_enemies()
        self.in_training_cage = False
        self.training_enemy_menu_open = False
        self.training_enemy_option_rects = []
        self.training_enemy_button_rect = None
        self.training_exit_rect = None
        if self.rooms:
            self.enter_room(self.rooms[0])

    def draw_training_cage_ui(self):
        base_x = 90
        button_w = 160
        button_h = 38
        top_y = SCREEN_HEIGHT - 70

        self.training_enemy_button_rect = (
            base_x - button_w / 2,
            top_y - button_h / 2,
            base_x + button_w / 2,
            top_y + button_h / 2,
        )
        draw_rectangle_filled(base_x, top_y, button_w, button_h,
                              (160, 120, 80, 220) if self.training_enemy_menu_open else (100, 100, 140, 220))
        draw_rectangle_outline(base_x, top_y, button_w, button_h, arcade.color.WHITE, border_width=2)
        arcade.draw_text("Gegner", base_x, top_y, arcade.color.WHITE, 14,
                         font_name=self.font, anchor_x="center", anchor_y="center")

        self.training_enemy_option_rects = []
        if self.training_enemy_menu_open:
            enemy_types = [
                ("Chaser", "chaser"),
                ("Ravager", "ravager"),
                ("Circler", "circler"),
                ("Brain", "blocker"),
                ("Hand", "hand"),
            ]
            for i, (label, enemy_type) in enumerate(enemy_types):
                by = top_y - (i + 1) * (button_h + 12)
                rect = (base_x - button_w / 2, by - button_h / 2,
                        base_x + button_w / 2, by + button_h / 2)
                self.training_enemy_option_rects.append((rect[0], rect[1], rect[2], rect[3], enemy_type))
                draw_rectangle_filled(base_x, by, button_w, button_h, (90, 140, 90, 220))
                draw_rectangle_outline(base_x, by, button_w, button_h, arcade.color.WHITE, border_width=2)
                arcade.draw_text(label, base_x, by, arcade.color.WHITE, 12,
                                 font_name=self.font, anchor_x="center", anchor_y="center")

        leave_y = top_y - (len(self.training_enemy_option_rects) + 1) * (button_h + 12)
        self.training_exit_rect = (
            base_x - button_w / 2,
            leave_y - button_h / 2,
            base_x + button_w / 2,
            leave_y + button_h / 2,
        )
        draw_rectangle_filled(base_x, leave_y, button_w, button_h, (180, 80, 80, 220))
        draw_rectangle_outline(base_x, leave_y, button_w, button_h, arcade.color.WHITE, border_width=2)
        arcade.draw_text("Verlassen", base_x, leave_y, arcade.color.WHITE, 12,
                         font_name=self.font, anchor_x="center", anchor_y="center")

    # ── Dungeon-Generierung ──────────────────────────────────────────────
    def _generate_dungeon(self):
        placed = {(0, 0)}
        self.rooms.append(Room(0, 0))
        for _ in range(12):
            base = random.choice(self.rooms)
            for dx, dy in random.sample([(0,1),(0,-1),(1,0),(-1,0)], 4):
                nx, ny = base.grid_x + dx, base.grid_y + dy
                if (nx, ny) not in placed:
                    nr = Room(nx, ny)
                    self.rooms.append(nr)
                    placed.add((nx, ny))
                    base.create_passages(nr)
                    nr.create_passages(base)
                    break
        self.boss_room = max(self.rooms,
                             key=lambda r: abs(r.grid_x) + abs(r.grid_y))
        self.boss_room.is_boss_room = True
        candidates = [r for r in self.rooms if r is not self.rooms[0] and r is not self.boss_room]
        for room in random.sample(candidates, k=min(2, len(candidates))):
            room.is_treasure_room = True
            room.treasure_room = TreasureRoom(room.grid_x, room.grid_y)

    def _build_world(self):
        for r in self.rooms:
            px, py = r.get_pixel_pos()
            for y in range(r.height):
                for x in range(r.width):
                    is_wall = r.tiles[y][x] == "wall"
                    spr = arcade.Sprite(self.tex_wall if is_wall else self.tex_floor)
                    spr.left, spr.bottom = px + x * TILE_SIZE, py + y * TILE_SIZE
                    (self.wall_list if is_wall else self.floor_list).append(spr)

    # ── Raum betreten ────────────────────────────────────────────────────
    def enter_room(self, room):
        # ─── Update Mini-Map ──────────────────────────────────────────────
        if CARD_SYSTEM_AVAILABLE and self.mini_map:
            room_type = "normal"
            if room.is_boss_room:
                room_type = "boss"
            elif room.is_shop_room:
                room_type = "shop"
            elif getattr(room, 'is_treasure_room', False):
                room_type = "treasure"
            elif room.is_escape_room:
                room_type = "escape"
            self.mini_map.explore_room(room.grid_x, room.grid_y, room_type)
        
        self.protection_timer = SPAWN_PROTECTION
        self.current_room     = room

        cx, cy = room.center_world()
        self.player.position = (cx, cy)
        self.camera.position = (cx, cy)

        if not room.visited:
            room.visited = True
            if room is self.rooms[0]:
                room.cleared = True
            elif room.is_shop_room:
                room.cleared = True
                self.showing_shop = False
                self.showing_inventory = False
                self.selected_inventory_card = None
                if self.boss_defeated:
                    self.open_shop()
                return
            elif getattr(room, 'is_treasure_room', False):
                room.cleared = True
                treasure = getattr(room, "treasure_room", None)
                if treasure and not getattr(room, "treasure_claimed", False):
                    room.treasure_claimed = True
                    for rune in treasure.rare_runes:
                        self.add_rune_to_inventory(rune.rune_type, rune.stack_level)
                    if not treasure.rare_runes:
                        self.add_rune_to_inventory(random.choice(list(RuneType)), 1)
                    for reward in treasure.special_rewards:
                        if reward == "coin":
                            self.coins += 18
                        elif reward == "hp_restore":
                            self.hp = min(self.player_max_hp, self.hp + 2)
                        elif reward == "damage_boost":
                            self.attack_speed_multiplier *= 0.97
                    if treasure.secret_fusion:
                        self.discover_combination(treasure.secret_fusion)
                return
            else:
                if room.is_boss_room:
                    count = 1
                elif self.difficulty == 1:
                    count = random.randint(1, 2)
                elif self.difficulty == 2:
                    count = random.randint(1, 3)
                else:
                    count = random.randint(2, 4)
                for i in range(count):
                    angle = i * (2 * math.pi / count)
                    ex = cx + math.cos(angle) * TILE_SIZE * 3
                    ey = cy + math.sin(angle) * TILE_SIZE * 3
                    r = random.random()
                    if r < 0.12:
                        # Hand stomper (hover + stomp)
                        e = HandEnemy(ex, ey, self.tex_hand, room, self.light_layer, room.is_boss_room)
                    elif r < 0.40:
                        # Brain blocker: uses brain texture and blocks/dashes
                        e = Enemy(ex, ey, self.tex_brain, self.tex_atk, room, self.light_layer, room.is_boss_room)
                        e.behavior = "blocker"
                        e.base_color = (160, 220, 255)
                        e.body.color = e.base_color
                        # remove orbiters for brain
                        e.orbiters = arcade.SpriteList()
                    else:
                        e = Enemy(ex, ey, self.tex_eye, self.tex_atk, room, self.light_layer, room.is_boss_room)
                        e.behavior = random.choice(["chaser", "ravager", "circler"])
                    if room.is_boss_room:
                        if self.difficulty == 1:
                            difficulty_factor = 0.65
                            speed_factor = 0.8
                        elif self.difficulty == 2:
                            difficulty_factor = 0.8
                            speed_factor = 0.9
                        else:
                            difficulty_factor = 1.0
                            speed_factor = 1.0
                    else:
                        if self.difficulty == 1:
                            difficulty_factor = 0.75
                            speed_factor = 0.85
                        elif self.difficulty == 2:
                            difficulty_factor = 1.0
                            speed_factor = 1.0
                        else:
                            difficulty_factor = 1.35
                            speed_factor = 1.15
                    e.hp = max(1, int(e.hp * difficulty_factor))
                    e.max_hp = max(1, int(e.max_hp * difficulty_factor))
                    e.speed_multiplier = speed_factor
                    e.natural_speed_multiplier = speed_factor
                    self.enemies.append(e)
                    self.enemy_sprites.append(e.body)
                    for o in e.orbiters:
                        self.orbiter_sprites.append(o)

        self._update_doors()

    def _new_dungeon(self):
        self.difficulty += 1
        self.boss_defeated = False
        self.timer_shop_opened = False
        self.pending_dungeon_after_shop = False
        self.map_timer = 60.0
        if CARD_SYSTEM_AVAILABLE:
            if self.skill_tree_ui:
                self.skill_tree_ui.visible = False
            if self.crafting_station_ui:
                self.crafting_station_ui.visible = False
            if self.mini_map_ui:
                self.mini_map_ui.visible = False
        self.hub_inventory_open = False

        self.rooms = []
        self.enemies = []
        self.current_room = None

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.floor_list = arcade.SpriteList()
        self.blocker_list = arcade.SpriteList()
        self.enemy_sprites = arcade.SpriteList()
        self.orbiter_sprites = arcade.SpriteList()

        self._generate_dungeon()
        self._build_world()

        start = self.rooms[0]
        self.player.position = start.center_world()
        self.camera.position = start.center_world()
        self.enter_room(start)

    def _update_doors(self):
        for s in self.blocker_list:
            self.wall_list.remove(s)
        self.blocker_list = arcade.SpriteList()

        if not self.current_room or self.current_room.cleared:
            return
        rx, ry = self.current_room.get_pixel_pos()
        for tx, ty in self.current_room.passages:
            b = arcade.SpriteSolidColor(TILE_SIZE, TILE_SIZE,
                                        color=(120, 10, 10, 255))
            b.left, b.bottom = rx + tx * TILE_SIZE, ry + ty * TILE_SIZE
            self.blocker_list.append(b)
            self.wall_list.append(b)

    def enter_boss_hub(self):
        self.in_shop_hub = True
        self.hub_wait_timer = 0.0
        self.hub_can_return = False
        self.hub_shop_menu2 = False
        self.hub_shop_card_rects = []
        self.hub_shop_button_rect = None
        self.hub_craft_button_rect = None
        self.hub_skilltree_button_rect = None
        self.hub_inventory_button_rect = None
        self.hub_return_button_rect = None
        self.hub_refresh_button_rect = None
        self.hub_training_button_rect = None
        self.hub_inventory_open = False
        self.hub_inv_card_rects: List[tuple] = []
        self.hub_inv_slot_rects: List[tuple] = []
        self.hub_inv_selected_card: Optional[str] = None

    # ── HUD ─────────────────────────────────────────────────────────────
    def draw_hud(self):
        arcade.draw_text(
            f"HP: {self.hp}/{self.player_max_hp}",
            20, SCREEN_HEIGHT - 32, arcade.color.RED, 16, bold=True, font_name=self.font
        )
        arcade.draw_text(
            f"Coins: {self.coins}",
            20, SCREEN_HEIGHT - 55, arcade.color.GOLD, 14, bold=True, font_name=self.font
        )
        if CARD_SYSTEM_AVAILABLE:
            rune_count = sum(r.stack_level for r in self.rune_inventory.runes) if self.rune_inventory else 0
            arcade.draw_text(
                f"Runen: {rune_count}   Fusionen: {len(self.active_fusions)}",
                20, SCREEN_HEIGHT - 76, arcade.color.LIGHT_CYAN, 11, font_name=self.font
            )

        # Hacks-Button klein oben rechts
        hack_w, hack_h = 90, 28
        hx = SCREEN_WIDTH - 52
        hy = SCREEN_HEIGHT - 20
        self.dev_menu_button_rect = (hx - hack_w / 2, hy - hack_h / 2,
                                     hx + hack_w / 2, hy + hack_h / 2)
        draw_rectangle_filled(hx, hy, hack_w, hack_h, (60, 60, 110, 200))
        draw_rectangle_outline(hx, hy, hack_w, hack_h, (40, 40, 80, 255), border_width=2)
        arcade.draw_text("Hacks", hx, hy, arcade.color.WHITE, 12,
                         font_name=self.font, anchor_x="center", anchor_y="center")

        # Teleport-Buttons wurden ins Dev-Menu verschoben
        self.teleport_boss_button_rect = None
        self.teleport_room_button_rect = None

    # ── Shop / Inventory UI ───────────────────────────────────────────────
    def _dev_menu_items(self, category: str) -> list:
        if category == "player":
            return [
                ("Full HP",          "full_hp"),
                ("+5 Max HP",        "hp_up"),
                ("+100 Coins",       "coins_100"),
                ("999 Coins",        "coins_999"),
                ("Invincibility 30s","invincible"),
            ]
        if category == "teleport":
            return [
                ("Boss Room",      "teleport_boss"),
                ("Training Area",  "training_cage"),
                ("Spawn Room",     "teleport_room"),
                ("Treasure Room",  "teleport_treasure"),
            ]
        if category == "dungeon":
            return [
                ("Kill All Enemies", "kill_enemies"),
                ("Skip Boss Kill",   "skip_boss_kill"),
                ("Open Boss Shop",   "open_boss_shop"),
            ]
        if category == "cards":
            items = [(self.cards_db[cid].name, f"card:{cid}") for cid in self.cards_db]
            items.append(("Give All Cards", "unlock_all"))
            return items
        if category == "runes":
            return [
                ("Ice Rune",       "rune:ice"),
                ("Fire Rune",      "rune:fire"),
                ("Blood Rune",     "rune:blood"),
                ("Thunder Rune",   "rune:thunder"),
                ("Poison Rune",    "rune:poison"),
                ("Wind Rune",      "rune:wind"),
                ("Explosion Rune", "rune:explosion"),
                ("Shadow Rune",    "rune:shadow"),
                ("Give All Runes", "give_all_runes"),
            ]
        if category == "crafting":
            return [
                ("Finish Crafting",     "crafting_finish"),
                ("Unlock All Recipes",  "crafting_unlock_all"),
                ("Reset Crafting",      "crafting_reset"),
            ]
        if category == "skilltree":
            return [
                ("Unlock Selected Node", "st_unlock_selected"),
                ("Unlock All Nodes",     "st_unlock_all"),
                ("Reset Skill Tree",     "st_reset"),
                ("Reveal All Recipes",   "st_reveal_all"),
            ]
        return []

    def _execute_dev_action(self, action: str):
        if action == "coins_100":
            self.coins += 100
        elif action == "coins_999":
            self.coins += 999
        elif action == "full_hp":
            self.hp = self.player_max_hp
        elif action == "hp_up":
            self.player_max_hp += 5
            self.hp = min(self.player_max_hp, self.hp + 5)
        elif action == "invincible":
            self.protection_timer = max(self.protection_timer, 30.0)
        elif action == "unlock_all":
            for cid in self.cards_db:
                self.inventory.add(cid)
        elif action == "give_all_runes":
            for rune_type in RuneType:
                self.add_rune_to_inventory(rune_type, 1)
        elif action == "kill_enemies":
            for e in list(self.enemies):
                if e.room is not self.current_room:
                    continue
                if e.light in self.light_layer:
                    self.light_layer.remove(e.light)
                e.body.remove_from_sprite_lists()
                for o in e.orbiters:
                    o.remove_from_sprite_lists()
                if e.is_boss:
                    self.boss_defeated = True
                    self.complete_pending_fusion_after_boss()
                self.enemies.remove(e)
        elif action == "skip_boss_kill":
            self.boss_defeated = True
            self.complete_pending_fusion_after_boss()
        elif action == "open_boss_shop":
            self.boss_defeated = True
            self.showing_dev_menu = False
            self.dev_menu_category = None
            self.enter_boss_hub()
        elif action == "training_cage":
            self.showing_dev_menu = False
            self.dev_menu_category = None
            self.start_training_cage()
        elif action == "teleport_boss":
            if hasattr(self, 'boss_room') and self.boss_room:
                self.showing_dev_menu = False
                self.dev_menu_category = None
                self.enter_room(self.boss_room)
        elif action == "teleport_room":
            if self.rooms:
                self.showing_dev_menu = False
                self.dev_menu_category = None
                self.enter_room(self.rooms[0])
        elif action == "teleport_treasure":
            for r in self.rooms:
                if getattr(r, 'is_treasure_room', False):
                    self.showing_dev_menu = False
                    self.dev_menu_category = None
                    self.enter_room(r)
                    break
        elif action.startswith("card:"):
            self.inventory.add(action.split(":", 1)[1])
        elif action.startswith("rune:"):
            self.add_rune_to_inventory(RuneType(action.split(":", 1)[1]))
        elif action == "crafting_finish":
            if self.crafting_station and self.crafting_station.fusion_in_progress:
                self.crafting_station.complete_after_boss()
        elif action == "crafting_reset":
            if self.crafting_station:
                self.crafting_station.clear()
        elif action == "crafting_unlock_all":
            if self.skill_tree:
                self.skill_tree.populate_unknown_combinations()
        elif action == "st_unlock_selected":
            if self.skill_tree_ui and self.skill_tree_ui.selected_node:
                n = self.skill_tree_ui.selected_node
                n.discovered = True
                n.unlocked = True
        elif action == "st_unlock_all":
            if self.skill_tree:
                for node in self.skill_tree.get_all_nodes():
                    node.discovered = True
                    node.unlocked = True
        elif action == "st_reset":
            if self.skill_tree:
                for node in self.skill_tree.get_all_nodes():
                    node.discovered = False
            self.discovered_combinations = {}
            self.active_fusions = []
        elif action == "st_reveal_all":
            if self.skill_tree:
                for node in self.skill_tree.get_all_nodes():
                    node.discovered = True

    def draw_dev_menu(self):
        self.dev_menu_category_rects = []
        self.dev_menu_sub_rects = []
        self.dev_menu_close_rect = None
        # Dunkles Overlay über gesamten Bildschirm
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 190))
        if self.dev_menu_category:
            self._draw_dev_submenu()
        else:
            self._draw_dev_main_menu()

    def _draw_dev_main_menu(self):
        pw, ph = 560, 480
        px = SCREEN_WIDTH / 2
        py = SCREEN_HEIGHT / 2
        draw_rectangle_filled(px, py, pw, ph, (28, 18, 8, 250))
        draw_rectangle_outline(px, py, pw, ph, (200, 148, 52, 255), border_width=4)
        draw_rectangle_outline(px, py, pw - 12, ph - 12, (100, 68, 24, 100), border_width=2)
        arcade.draw_text("DEVELOPER MENU", px, py + ph / 2 - 32,
                         arcade.color.GOLD, 22, font_name=self.font,
                         anchor_x="center", anchor_y="center", bold=True)

        categories = [
            ("PLAYER",     "player"),
            ("TELEPORT",   "teleport"),
            ("DUNGEON",    "dungeon"),
            ("CARDS",      "cards"),
            ("RUNES",      "runes"),
            ("CRAFTING",   "crafting"),
            ("SKILL TREE", "skilltree"),
        ]
        btn_w, btn_h = 240, 52
        col_gap, row_gap = 18, 10
        cols = 2
        total_w = cols * btn_w + col_gap
        sx = px - total_w / 2
        sy = py + ph / 2 - 82
        for i, (label, cat_id) in enumerate(categories):
            col = i % cols
            row = i // cols
            cx = sx + col * (btn_w + col_gap) + btn_w / 2
            cy = sy - row * (btn_h + row_gap) - btn_h / 2
            if i == len(categories) - 1 and len(categories) % 2 == 1:
                cx = px  # letzter Button zentriert
            pressed = self.dev_menu_button_pressed == ("cat", cat_id)
            bg  = (68, 40, 14, 245) if pressed else (108, 65, 26, 238)
            brd = (200, 152, 52, 255)
            draw_rectangle_filled(cx, cy, btn_w, btn_h, bg)
            draw_rectangle_outline(cx, cy, btn_w, btn_h, brd, border_width=2)
            arcade.draw_text(label, cx, cy, arcade.color.WHITE, 15,
                             font_name=self.font, anchor_x="center",
                             anchor_y="center", bold=True)
            self.dev_menu_category_rects.append(
                (cx - btn_w / 2, cy - btn_h / 2, cx + btn_w / 2, cy + btn_h / 2, cat_id))

        # Schließen-Button
        close_x = px + pw / 2 - 38
        close_y = py + ph / 2 - 28
        self.dev_menu_close_rect = (close_x - 32, close_y - 20, close_x + 32, close_y + 20)
        pressed = self.dev_menu_button_pressed == ("close", None)
        draw_rectangle_filled(close_x, close_y, 64, 40,
                              (145, 32, 32, 235) if pressed else (195, 52, 52, 220))
        draw_rectangle_outline(close_x, close_y, 64, 40, (255, 80, 80, 255), border_width=2)
        arcade.draw_text("ESC", close_x, close_y, arcade.color.WHITE, 12,
                         font_name=self.font, anchor_x="center", anchor_y="center")

    def _draw_dev_submenu(self):
        cat = self.dev_menu_category
        cat_title = {
            "player":   "PLAYER",
            "teleport": "TELEPORT",
            "dungeon":  "DUNGEON",
            "cards":    "CARDS",
            "runes":    "RUNES",
            "crafting": "CRAFTING",
            "skilltree":"SKILL TREE",
        }.get(cat, cat.upper())
        items = self._dev_menu_items(cat)

        btn_w, btn_h = 400, 48
        row_gap = 10
        header_h = 68
        footer_h = 58
        ph = header_h + footer_h + len(items) * (btn_h + row_gap)
        ph = max(260, min(ph, SCREEN_HEIGHT - 60))
        pw = 460
        px = SCREEN_WIDTH / 2
        py = SCREEN_HEIGHT / 2

        draw_rectangle_filled(px, py, pw, ph, (22, 14, 6, 252))
        draw_rectangle_outline(px, py, pw, ph, (200, 148, 52, 255), border_width=4)
        draw_rectangle_outline(px, py, pw - 12, ph - 12, (100, 68, 24, 100), border_width=2)
        arcade.draw_text(cat_title, px, py + ph / 2 - 30,
                         arcade.color.GOLD, 20, font_name=self.font,
                         anchor_x="center", anchor_y="center", bold=True)

        area_top    = py + ph / 2 - header_h
        area_bottom = py - ph / 2 + footer_h
        start_y = area_top
        for i, (label, action) in enumerate(items):
            cy = start_y - i * (btn_h + row_gap) - btn_h / 2
            if cy + btn_h / 2 < area_bottom or cy - btn_h / 2 > area_top:
                continue
            is_special = action in ("unlock_all", "give_all_runes", "crafting_unlock_all",
                                    "st_unlock_all", "st_reveal_all")
            pressed = self.dev_menu_button_pressed == ("sub", action)
            if is_special:
                bg  = (42, 118, 42, 245) if not pressed else (30, 88, 30, 245)
                brd = (90, 215, 75, 255)
            else:
                bg  = (92, 58, 22, 240) if not pressed else (62, 38, 14, 240)
                brd = (168, 128, 48, 255)
            draw_rectangle_filled(px, cy, btn_w, btn_h, bg)
            draw_rectangle_outline(px, cy, btn_w, btn_h, brd, border_width=2)
            arcade.draw_text(label, px, cy, arcade.color.WHITE, 14,
                             font_name=self.font, anchor_x="center", anchor_y="center")
            self.dev_menu_sub_rects.append(
                (px - btn_w / 2, cy - btn_h / 2, px + btn_w / 2, cy + btn_h / 2, action))

        # Zurück-Button
        back_y = py - ph / 2 + 28
        self.dev_menu_close_rect = (px - 72, back_y - 22, px + 72, back_y + 22)
        pressed = self.dev_menu_button_pressed == ("back", None)
        draw_rectangle_filled(px, back_y, 144, 44,
                              (62, 38, 14, 240) if pressed else (92, 58, 22, 235))
        draw_rectangle_outline(px, back_y, 144, 44, (168, 128, 48, 255), border_width=2)
        arcade.draw_text("← ZURÜCK", px, back_y, arcade.color.WHITE, 13,
                         font_name=self.font, anchor_x="center", anchor_y="center")

    def draw_hub_scene(self):
        draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                              SCREEN_WIDTH, SCREEN_HEIGHT,
                              (90, 50, 20, 255))
        for x, y, radius, color in [
                (SCREEN_WIDTH * 0.25, SCREEN_HEIGHT * 0.75, 120, (190, 110, 60, 90)),
                (SCREEN_WIDTH * 0.82, SCREEN_HEIGHT * 0.78, 100, (220, 140, 70, 90)),
                (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.25, 140, (210, 130, 55, 90))]:
            arcade.draw_circle_filled(x, y, radius, color)

        draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
                              SCREEN_WIDTH - 220, SCREEN_HEIGHT - 260,
                              (120, 70, 30, 255))
        draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
                               SCREEN_WIDTH - 220, SCREEN_HEIGHT - 260,
                               (60, 35, 15, 255), border_width=10)
        arcade.draw_text("Boss-Hub", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 170,
                         arcade.color.BEIGE, 32, font_name=self.font,
                         anchor_x="center")
        arcade.draw_text("Wärme und Ruhe nach dem Kampf. Klicke oben links auf den Shop.",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 125,
                         arcade.color.LIGHT_GRAY, 16, font_name=self.font,
                         anchor_x="center")

        button_defs = [
            ("Shop", "Karten", "hub_shop_button_rect"),
            ("Crafting", "Fusionen", "hub_craft_button_rect"),
            ("Skilltree", "Builds", "hub_skilltree_button_rect"),
            ("Inventar", "Deck", "hub_inventory_button_rect"),
            ("Training", "Kampfzone", "hub_training_button_rect"),
        ]
        btn_gap = 8
        btn_w = (SCREEN_WIDTH - 20 - btn_gap * (len(button_defs) - 1)) // len(button_defs)
        for i, (title, sub, attr) in enumerate(button_defs):
            left = 10 + i * (btn_w + btn_gap)
            right = left + btn_w
            top, bottom = SCREEN_HEIGHT - 38, SCREEN_HEIGHT - 128
            setattr(self, attr, (left, bottom, right, top))
            is_training = (attr == "hub_training_button_rect")
            bg_color = (100, 60, 30, 255) if not is_training else (50, 100, 50, 255)
            draw_rectangle_filled((left + right) / 2, (bottom + top) / 2,
                                  right - left, top - bottom, bg_color)
            draw_rectangle_outline((left + right) / 2, (bottom + top) / 2,
                                   right - left, top - bottom,
                                   (70, 40, 20, 255) if not is_training else (40, 80, 40, 255),
                                   border_width=3)
            arcade.draw_text(title, (left + right) / 2, (bottom + top) / 2 + 10,
                             arcade.color.WHITE, 15, font_name=self.font,
                             anchor_x="center")
            arcade.draw_text(sub, (left + right) / 2, (bottom + top) / 2 - 14,
                             arcade.color.LIGHT_GRAY, 10, font_name=self.font,
                             anchor_x="center")

        bx, by = SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.15
        bw, bh = 420, 64
        self.hub_return_button_rect = (bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2)
        button_color = (180, 100, 50, 255) if self.hub_can_return else (110, 70, 40, 255)
        outline_color = (70, 45, 20, 255)
        draw_rectangle_filled(bx, by, bw, bh, button_color)
        draw_rectangle_outline(bx, by, bw, bh, outline_color, border_width=4)
        label = "Zurück zur Dungeon" if self.hub_can_return else "Warte kurz, bevor du zurückkehrst"
        arcade.draw_text(label, bx, by, arcade.color.WHITE, 16, font_name=self.font,
                         anchor_x="center", anchor_y="center")
        if not self.hub_can_return:
            wait_text = f"Noch {max(0.0, self.hub_wait_min - self.hub_wait_timer):.1f}s"
            arcade.draw_text(wait_text, bx, by - 26, arcade.color.LIGHT_GRAY, 12,
                             font_name=self.font, anchor_x="center")

        arcade.draw_text(f"Coins: {self.coins}", SCREEN_WIDTH - 130, SCREEN_HEIGHT - 40,
                         arcade.color.GOLD, 16, font_name=self.font, anchor_x="center")

    def draw_hub_inventory(self):
        # Gleiche Darstellung wie das Tab-Inventar
        self.draw_inventory_ui()
        # Fusionen als reine Info-Leiste (nicht klickbar)
        if self.active_fusions:
            names = "   |   ".join(f.fusion_name for f in self.active_fusions[:5])
            arcade.draw_text(f"Fusionen: {names}",
                             SCREEN_WIDTH / 2, 18,
                             arcade.color.LIGHT_CYAN, 9,
                             font_name=self.font, anchor_x="center")

    def draw_hub_shop_menu(self):
        draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                              SCREEN_WIDTH - 200, SCREEN_HEIGHT - 170,
                              (120, 70, 35, 230))
        draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                               SCREEN_WIDTH - 200, SCREEN_HEIGHT - 170,
                               (60, 35, 20, 255), border_width=10)
        arcade.draw_text("Karten-Shop 2.0", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120,
                         arcade.color.BEIGE, 28, font_name=self.font,
                         anchor_x="center")
        arcade.draw_text(f"Coins: {self.coins}", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150,
                         arcade.color.GOLD, 18, font_name=self.font,
                         anchor_x="center")

        self.hub_craft_button_rect = (80, SCREEN_HEIGHT - 190, 220, SCREEN_HEIGHT - 145)
        self.hub_skilltree_button_rect = (235, SCREEN_HEIGHT - 190, 395, SCREEN_HEIGHT - 145)
        for rect, label in [(self.hub_craft_button_rect, "Crafting"), (self.hub_skilltree_button_rect, "Skilltree")]:
            left, bottom, right, top = rect
            draw_rectangle_filled((left + right) / 2, (bottom + top) / 2,
                                  right - left, top - bottom, (140, 85, 45, 255))
            draw_rectangle_outline((left + right) / 2, (bottom + top) / 2,
                                   right - left, top - bottom, (70, 40, 15, 255), border_width=3)
            arcade.draw_text(label, (left + right) / 2, (bottom + top) / 2,
                             arcade.color.WHITE, 13, font_name=self.font,
                             anchor_x="center", anchor_y="center")

        self.hub_refresh_button_rect = (SCREEN_WIDTH - 180, SCREEN_HEIGHT - 180,
                                        SCREEN_WIDTH - 80, SCREEN_HEIGHT - 140)
        draw_rectangle_filled((SCREEN_WIDTH - 130), SCREEN_HEIGHT - 160,
                              90, 40, (140, 85, 45, 255))
        draw_rectangle_outline((SCREEN_WIDTH - 130), SCREEN_HEIGHT - 160,
                               90, 40, (70, 40, 15, 255), border_width=3)
        arcade.draw_text("Refresh", SCREEN_WIDTH - 130, SCREEN_HEIGHT - 160,
                         arcade.color.WHITE, 14, font_name=self.font,
                         anchor_x="center", anchor_y="center")

        card_start_x = SCREEN_WIDTH / 2 - 340
        card_y = SCREEN_HEIGHT / 2 + 20
        self.hub_shop_card_rects = []
        for i, cid in enumerate(self.shop_choices):
            card = self.cards_db[cid]
            x = card_start_x + i * 340
            left = x - 140
            right = x + 140
            bottom = card_y - 120
            top = card_y + 140
            self.hub_shop_card_rects.append((left, bottom, right, top, cid))
            draw_rectangle_filled(x, card_y, 260, 260, (140, 90, 45, 255))
            draw_rectangle_outline(x, card_y, 260, 260, (65, 40, 20, 255), border_width=6)
            texture = self.card_textures.get(card.id)
            if texture:
                arcade.draw_texture_rect(texture, arcade.XYWH(x, card_y + 20, texture.width, texture.height))
            arcade.draw_text(card.name, x, card_y + 130, arcade.color.WHITE, 16,
                             font_name=self.font, anchor_x="center")
            arcade.draw_text(f"{card.price} Coins", x, card_y - 100, arcade.color.GOLD, 12,
                             font_name=self.font, anchor_x="center")
            arcade.draw_text(card.buff_text, x, card_y - 72, arcade.color.LIGHT_GRAY, 10,
                             font_name=self.font, anchor_x="center")
            arcade.draw_text(card.bad_text, x, card_y - 52, arcade.color.LIGHT_GRAY, 10,
                             font_name=self.font, anchor_x="center")

        bx, by = SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.12
        bw, bh = 260, 56
        self.hub_shop_back_rect = (bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2)
        draw_rectangle_filled(bx, by, bw, bh, (140, 85, 45, 255))
        draw_rectangle_outline(bx, by, bw, bh, (70, 40, 15, 255), border_width=4)
        arcade.draw_text("Zurück", bx, by, arcade.color.WHITE, 16,
                         font_name=self.font, anchor_x="center", anchor_y="center")

    def open_shop(self, hub=False):
        rarities = {"common":70, "uncommon":20, "rare":8, "epic":2, "legendary":1}
        shop_ids = []
        weights = []
        for c in self.cards_db.values():
            if not c.shop_enabled:
                continue
            if not self.first_shop_done and c.rarity in ("epic", "legendary"):
                continue
            shop_ids.append(c.id)
            weights.append(rarities.get(c.rarity, 10))

        self.shop_choices = []
        available_ids = shop_ids[:]
        available_weights = weights[:]
        count = min(3, len(available_ids))
        for _ in range(count):
            choice = random.choices(available_ids, weights=available_weights, k=1)[0]
            self.shop_choices.append(choice)
            index = available_ids.index(choice)
            del available_ids[index]
            del available_weights[index]

        self.showing_inventory = False
        self.selected_inventory_card = None
        if hub:
            self.hub_shop_menu2 = True
            self.in_shop_hub = True
            self.hub_shop_card_rects = []
            self.showing_shop = False
        else:
            self.showing_shop = True
            self.first_shop_done = True

    def buy_card(self, card_id):
        card = self.cards_db[card_id]
        price = card.price
        if self.coins < price:
            return
        self.coins -= price
        if self.slot_primary.card_id == card_id:
            self.slot_primary.charges += 1
        elif self.slot_secondary.card_id == card_id:
            self.slot_secondary.charges += 1
        else:
            self.inventory.add(card_id)
        card.bad_fn(self)
        self.showing_shop = False

    def equip_card_from_inventory(self, card_id, slot_name):
        if card_id not in self.inventory.cards:
            return
        total_copies = self.inventory.count(card_id)
        if slot_name == "primary":
            self.slot_primary.card_id = card_id
            self.slot_primary.charges = total_copies
        else:
            self.slot_secondary.card_id = card_id
            self.slot_secondary.charges = total_copies
        self.inventory.remove(card_id)

    def unequip_slot(self, slot_name):
        """Gibt verbleibende Charges zurück ins Inventar und leert den Slot."""
        if slot_name == "primary":
            slot = self.slot_primary
        else:
            slot = self.slot_secondary

        if slot.card_id:
            if slot.charges > 0:
                self.inventory.add(slot.card_id, slot.charges)
            slot.card_id = None
            slot.charges = 0

    def do_shockwave(self):
        num = 8 + (self.slot_primary.charges - 1) * 4
        cx, cy = self.player.position
        for i in range(num):
            a = i * (2 * math.pi / num)
            s = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.5)
            s.position = (cx, cy)
            sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
            self.light_layer.add(sl)
            s.light = sl
            self.attach_fusion_to_shard(s, CardType.NORMAL_SHOT)
            self.shard_list.append(s)

    def activate_invincibility(self, duration):
        self.protection_timer = max(self.protection_timer, duration)

    def _rect_contains(self, rect, x, y):
        left, bottom, right, top = rect
        return left <= x <= right and bottom <= y <= top

    def draw_shop_room_markers(self):
        if not self.shop_area or not self.inventory_area:
            return
        left, bottom, right, top = self.shop_area
        draw_rectangle_filled((left + right) / 2, (bottom + top) / 2,
                                     right - left, top - bottom,
                                     (120, 70, 30, 180))
        draw_rectangle_outline((left + right) / 2, (bottom + top) / 2,
                                      right - left, top - bottom,
                                      arcade.color.BROWN, border_width=3)
        left, bottom, right, top = self.inventory_area
        draw_rectangle_filled((left + right) / 2, (bottom + top) / 2,
                                     right - left, top - bottom,
                                     (60, 140, 60, 180))
        draw_rectangle_outline((left + right) / 2, (bottom + top) / 2,
                                      right - left, top - bottom,
                                      arcade.color.DARK_GREEN, border_width=3)

    def on_draw(self):
        self.clear()
        self.camera.use()
        with self.light_layer:
            self.floor_list.draw(pixelated=True)
            self.wall_list.draw(pixelated=True)
            self.blocker_list.draw(pixelated=True)
            self.shard_list.draw(pixelated=True)
            self.particle_list.draw(pixelated=True)
            self.shield_list.draw(pixelated=True)
            self.orbiter_sprites.draw(pixelated=True)
            self.enemy_sprites.draw(pixelated=True)

            for e in self.enemies:
                if (e.room is self.current_room and getattr(e, "behavior", None) == "blocker"
                        and getattr(e, "dash_warning_timer", 0.0) > 0.0
                        and e.dash_target is not None):
                    alpha = int(180 * (e.dash_warning_timer / 0.45))
                    arcade.draw_circle_outline(e.dash_target[0], e.dash_target[1], 24,
                                               (255, 120, 50, alpha), border_width=3)
                    arcade.draw_line(e.body.center_x, e.body.center_y,
                                     e.dash_target[0], e.dash_target[1],
                                     (255, 180, 100, alpha), line_width=2)

            for ring in self.enemy_shockwaves:
                arcade.draw_circle_outline(ring["x"], ring["y"], ring["radius"],
                                           (240, 200, 120, ring["alpha"]), border_width=3)
                arcade.draw_circle_outline(ring["x"], ring["y"], ring["radius"] + ring["thickness"] * 0.4,
                                           (255, 240, 180, max(32, ring["alpha"] // 2)), border_width=1)

            blink_on = int(self.protection_timer / 0.15) % 2 == 0
            self.player.alpha = 60 if (self.protection_timer > 0 and blink_on) else 255
            self.player_list.draw(pixelated=True)
            self.staff_list.draw(pixelated=True)


        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        self.camera.use()
        for e in self.enemies:
            if e.room is self.current_room:
                e.draw_health_bar()

        self.ui_camera.use()
        if self.in_training_cage:
            self.draw_training_cage_ui()
        if self.in_shop_hub:
            if self.hub_shop_menu2:
                self.draw_hub_shop_menu()
            else:
                self.draw_hub_scene()
                if self.hub_inventory_open:
                    self.draw_hub_inventory()
            if CARD_SYSTEM_AVAILABLE and self.skill_tree_ui:
                self.skill_tree_ui.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
            if CARD_SYSTEM_AVAILABLE and self.crafting_station_ui:
                self.crafting_station_ui.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
        elif self.game_over:
            self.draw_pixel_screen(
                "GAME  OVER",
                "[  R  ] Nochmal versuchen   [  M  ] Menü",
                (220, 40, 40, 255))
        elif self.win:
            self.draw_pixel_screen(
                "VICTORY !",
                "Du hast den Dungeon verlassen!",
                (255, 215, 0, 255))
        else:
            if self.showing_shop:
                self.draw_shop_ui()
            elif self.showing_inventory:
                self.draw_inventory_ui()
            else:
                self.draw_hud()
                # ─── New Card System UI ───────────────────────────
                if CARD_SYSTEM_AVAILABLE and self.mini_map_ui:
                    self.mini_map_ui.draw(SCREEN_WIDTH, SCREEN_HEIGHT, 
                                         (self.current_room.grid_x, self.current_room.grid_y) if self.current_room else (0, 0),
                                         compact=False)
                if CARD_SYSTEM_AVAILABLE and self.skill_tree_ui:
                    self.skill_tree_ui.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
                if CARD_SYSTEM_AVAILABLE and self.crafting_station_ui:
                    self.crafting_station_ui.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
            if self.showing_dev_menu:
                self.draw_dev_menu()

    def draw_shop_ui(self):
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            SCREEN_WIDTH, SCREEN_HEIGHT),
                                (0, 0, 0, 220))
        arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                            SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120),
                                (18, 18, 28, 230))
        arcade.draw_text(f"Coins: {self.coins}", SCREEN_WIDTH - 120, SCREEN_HEIGHT - 80,
                         arcade.color.GOLD, 18, font_name=self.font, anchor_x="center")

        start_x = SCREEN_WIDTH / 2 - 300
        y_center = SCREEN_HEIGHT / 2 + 20
        for i, cid in enumerate(self.shop_choices):
            card = self.cards_db[cid]
            x = start_x + i * 300
            y = y_center
            texture = self.card_textures.get(card.id)
            if texture:
                arcade.draw_texture_rect(texture, arcade.XYWH(x, y + 10, texture.width, texture.height))
                border_col = RARITY_COLORS.get(card.rarity, (200, 200, 200, 220))
                arcade.draw_rect_outline(arcade.XYWH(x, y + 10, texture.width + 6, texture.height + 6), border_col, 4)
            else:
                border_col = RARITY_COLORS.get(card.rarity, (200, 200, 200, 220))
                arcade.draw_rect_outline(arcade.XYWH(x, y + 10, 226, 286), border_col, 4)

            arcade.draw_text(card.name, x, y + 170, arcade.color.WHITE, 18,
                             font_name=self.font, anchor_x="center")
            arcade.draw_text(f"Preis {card.price}", x - 80, y - 120,
                             arcade.color.GOLD, 12, font_name=self.font, anchor_x="left")
            arcade.draw_text(card.buff_text, x - 80, y - 100,
                             arcade.color.LIGHT_GREEN, 11, font_name=self.font, anchor_x="left")
            arcade.draw_text(card.bad_text, x - 80, y - 82,
                             arcade.color.RED, 11, font_name=self.font, anchor_x="left")
            arcade.draw_text("Kaufen", x + 80, y - 120,
                             arcade.color.LIGHT_GRAY, 12, font_name=self.font, anchor_x="right")
            arcade.draw_text(card.rarity.upper(), x + 80, y - 100,
                             arcade.color.LIGHT_BLUE, 10, font_name=self.font, anchor_x="right")

    # ── Runen-Farben (für Inventar-Seite 2) ──────────────────────────────
    _RUNE_UI_COLORS = {
        RuneType.ICE:       (100, 200, 255),
        RuneType.FIRE:      (255, 110, 40),
        RuneType.BLOOD:     (210, 30,  60),
        RuneType.THUNDER:   (245, 235, 50),
        RuneType.POISON:    (80,  220, 80),
        RuneType.WIND:      (180, 245, 255),
        RuneType.EXPLOSION: (255, 165, 30),
        RuneType.SHADOW:    (160, 90,  225),
    }

    def draw_inventory_ui(self):
        self.inv_card_rects = []
        self.inv_tab_rects  = []

        # Hintergrund
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 225))
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80),
            (14, 22, 14, 230))
        arcade.draw_rect_outline(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80),
            (50, 80, 50, 200), 2)

        # ── Tabs ─────────────────────────────────────────────────────────
        tab_defs = [("Karten", 0), ("Runen", 1), ("Fusionen", 2)]
        tw, th = 180, 38
        total_tw = len(tab_defs) * tw + (len(tab_defs) - 1) * 10
        tab_sx = SCREEN_WIDTH / 2 - total_tw / 2
        tab_ty = SCREEN_HEIGHT - 50
        for i, (lbl, page) in enumerate(tab_defs):
            tx = tab_sx + i * (tw + 10) + tw / 2
            active = (self.inv_page == page)
            bg  = (45, 110, 45, 245) if active else (22, 45, 22, 215)
            brd = (100, 220, 80, 255) if active else (40, 70, 40, 180)
            arcade.draw_rect_filled( arcade.XYWH(tx, tab_ty, tw, th), bg)
            arcade.draw_rect_outline(arcade.XYWH(tx, tab_ty, tw, th), brd, 2)
            arcade.draw_text(lbl, tx, tab_ty, arcade.color.WHITE if active else (160, 200, 160),
                             14, font_name=self.font, anchor_x="center",
                             anchor_y="center", bold=active)
            self.inv_tab_rects.append((tx - tw / 2, tab_ty - th / 2,
                                       tx + tw / 2, tab_ty + th / 2, page))

        # ── Seiteninhalt ─────────────────────────────────────────────────
        if self.inv_page == 0:
            self._draw_inv_page_cards()
        elif self.inv_page == 1:
            self._draw_inv_page_runes()
        else:
            self._draw_inv_page_fusions()

        # ── Fusszeile ────────────────────────────────────────────────────
        hints = {
            0: "Karte anklicken → auswählen | Slot anklicken → ausrüsten | ESC: Schließen",
            1: "Runen-Übersicht  –  ESC: Schließen",
            2: "Entdeckte Fusionen  –  ESC: Schließen",
        }
        arcade.draw_text(hints[self.inv_page], SCREEN_WIDTH / 2, 28,
                         arcade.color.LIGHT_GRAY, 11,
                         font_name=self.font, anchor_x="center")

    def _draw_inv_page_cards(self):
        SX, SY = 95, SCREEN_HEIGHT - 118
        COLS, STEP_X, STEP_Y = 5, 168, 178
        BOX = 120

        for i, (cid, count) in enumerate(self.inventory.cards.items()):
            card = self.cards_db.get(cid)
            if not card:
                continue
            cx = SX + (i % COLS) * STEP_X
            cy = SY - (i // COLS) * STEP_Y
            texture = self.card_textures.get(cid)
            selected = (self.selected_inventory_card == cid)

            if texture:
                arcade.draw_texture_rect(
                    texture, arcade.XYWH(cx, cy, texture.width, texture.height))
                brd_size = texture.width + 8
                brd_col  = (255, 230, 40, 255) if selected else (200, 200, 200, 180)
                arcade.draw_rect_outline(
                    arcade.XYWH(cx, cy, brd_size, texture.height + 8), brd_col,
                    4 if selected else 2)
                click_w, click_h = texture.width + 4, texture.height + 4
            else:
                col = (90, 140, 90, 210)
                arcade.draw_rect_filled( arcade.XYWH(cx, cy, BOX, BOX), col)
                brd_col = (255, 230, 40, 255) if selected else (160, 200, 160, 200)
                arcade.draw_rect_outline(arcade.XYWH(cx, cy, BOX, BOX), brd_col,
                                         4 if selected else 2)
                click_w, click_h = BOX, BOX

            arcade.draw_text(card.name, cx, cy - click_h / 2 - 11,
                             arcade.color.WHITE, 9, font_name=self.font,
                             anchor_x="center")
            arcade.draw_text(f"x{count}", cx + click_w / 2 - 4,
                             cy + click_h / 2 + 2,
                             arcade.color.LIGHT_GREEN, 10, font_name=self.font)
            self.inv_card_rects.append(
                (cx - click_w / 2, cy - click_h / 2,
                 cx + click_w / 2, cy + click_h / 2, cid))

        # Ausrüstungs-Slots
        BOX_W, BOX_H = 195, 148
        by = 85
        for slot_x, label, slot in [
            (SCREEN_WIDTH / 2 - 220, "Primary  [LMB]",  self.slot_primary),
            (SCREEN_WIDTH / 2 + 220, "Secondary  [RMB]", self.slot_secondary),
        ]:
            selected_target = self.selected_inventory_card is not None
            bg  = (28, 55, 88, 235) if not selected_target else (40, 80, 120, 245)
            brd = (80, 140, 200, 200) if not selected_target else (120, 200, 255, 255)
            arcade.draw_rect_filled( arcade.XYWH(slot_x, by, BOX_W, BOX_H), bg)
            arcade.draw_rect_outline(arcade.XYWH(slot_x, by, BOX_W, BOX_H), brd,
                                     3 if selected_target else 2)
            arcade.draw_text(label, slot_x, by + 52,
                             arcade.color.LIGHT_BLUE, 11,
                             font_name=self.font, anchor_x="center")
            if slot.card_id and slot.card_id in self.cards_db:
                c = self.cards_db[slot.card_id]
                arcade.draw_text(c.name, slot_x, by + 15,
                                 arcade.color.WHITE, 12,
                                 font_name=self.font, anchor_x="center")
                arcade.draw_text(f"Charges: {slot.charges}", slot_x, by - 15,
                                 arcade.color.LIGHT_GRAY, 10,
                                 font_name=self.font, anchor_x="center")
                arcade.draw_text("[Klick zum Ablegen]", slot_x, by - 40,
                                 (140, 140, 160, 180), 9,
                                 font_name=self.font, anchor_x="center")
            else:
                arcade.draw_text("Leer", slot_x, by,
                                 arcade.color.LIGHT_GRAY, 14,
                                 font_name=self.font, anchor_x="center")

    def _draw_inv_page_runes(self):
        if not (CARD_SYSTEM_AVAILABLE and self.rune_inventory and self.rune_inventory.runes):
            arcade.draw_text("Keine Runen im Inventar.",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.LIGHT_GRAY, 18,
                             font_name=self.font, anchor_x="center", anchor_y="center")
            return

        cols, rw, rh, gap_x, gap_y = 4, 210, 70, 14, 12
        total_w = cols * rw + (cols - 1) * gap_x
        sx = SCREEN_WIDTH / 2 - total_w / 2 + rw / 2
        sy = SCREEN_HEIGHT - 130

        for i, rune in enumerate(self.rune_inventory.runes):
            col = i % cols
            row = i // cols
            rx = sx + col * (rw + gap_x)
            ry = sy - row * (rh + gap_y)
            rc = self._RUNE_UI_COLORS.get(rune.rune_type, (180, 180, 180))
            bg = (rc[0] // 5, rc[1] // 5, rc[2] // 5, 220)
            arcade.draw_rect_filled( arcade.XYWH(rx, ry, rw, rh), bg)
            arcade.draw_rect_outline(arcade.XYWH(rx, ry, rw, rh), rc + (220,), 2)
            arcade.draw_rect_filled( arcade.XYWH(rx - rw / 2 + 4, ry, 5, rh - 6), rc + (230,))
            arcade.draw_text(rune.display_name, rx, ry + 10,
                             rc + (255,), 12,
                             font_name=self.font, anchor_x="center", anchor_y="center",
                             bold=True)
            arcade.draw_text(f"Stack: {rune.stack_level}", rx, ry - 14,
                             arcade.color.LIGHT_GRAY, 9,
                             font_name=self.font, anchor_x="center")

    def _draw_inv_page_fusions(self):
        if not self.active_fusions:
            arcade.draw_text("Noch keine Fusionen entdeckt.",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                             arcade.color.LIGHT_GRAY, 18,
                             font_name=self.font, anchor_x="center", anchor_y="center")
            arcade.draw_text("Kombiniere Karten + Runen an der Fusion Station!",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 14,
                             (120, 160, 120, 200), 13,
                             font_name=self.font, anchor_x="center")
            return

        cols, fw, fh, gap_x, gap_y = 3, 280, 88, 14, 12
        total_w = cols * fw + (cols - 1) * gap_x
        sx = SCREEN_WIDTH / 2 - total_w / 2 + fw / 2
        sy = SCREEN_HEIGHT - 115

        rarity_colors = {
            "common":    (200, 200, 200),
            "uncommon":  (80,  210, 80),
            "rare":      (80,  145, 230),
            "epic":      (185, 80,  205),
            "legendary": (225, 195, 55),
        }

        for i, fusion in enumerate(self.active_fusions):
            col = i % cols
            row = i // cols
            fx = sx + col * (fw + gap_x)
            fy = sy - row * (fh + gap_y)
            rc = rarity_colors.get(fusion.rarity, (200, 200, 200))
            arcade.draw_rect_filled( arcade.XYWH(fx, fy, fw, fh), (18, 28, 18, 230))
            arcade.draw_rect_outline(arcade.XYWH(fx, fy, fw, fh), rc + (220,), 2)
            arcade.draw_rect_filled( arcade.XYWH(fx - fw / 2 + 4, fy, 4, fh - 6),
                                     rc + (230,))
            arcade.draw_text(fusion.fusion_name, fx, fy + 24,
                             rc + (255,), 13,
                             font_name=self.font, anchor_x="center",
                             anchor_y="center", bold=True)
            arcade.draw_text(
                f"{fusion.card_type.value.replace('_',' ').title()}  +  "
                f"{', '.join(r.value.capitalize() for r in fusion.runes)}",
                fx, fy + 2, arcade.color.LIGHT_GRAY, 9,
                font_name=self.font, anchor_x="center")
            arcade.draw_text(fusion.rarity.upper(), fx, fy - 20,
                             rc + (200,), 9,
                             font_name=self.font, anchor_x="center")

    def on_update(self, delta_time):
        if self.game_over:
            return

        # ─── Update Crafting Station ──────────────────────────────────────
        if CARD_SYSTEM_AVAILABLE and self.crafting_station:
            self.crafting_station.update(delta_time)

        if self.in_shop_hub:
            self.hub_wait_timer = min(self.hub_wait_min, self.hub_wait_timer + delta_time)
            self.hub_can_return = self.hub_wait_timer >= self.hub_wait_min
            return

        if self.showing_shop or self.showing_inventory:
            return

        self.dash_cooldown = max(0.0, self.dash_cooldown - delta_time)
        if self.dash_active:
            self.dash_timer -= delta_time
            if self.dash_timer <= 0:
                self.dash_active = False

        move_x = 0
        move_y = 0
        inv_wind = self.fusion_rune_counts(CardType.INVINCIBILITY).get(RuneType.WIND, 0) if self.protection_timer > 0 else 0
        frame_speed = PLAYER_SPEED * self.player_speed_multiplier * (1.0 + 0.35 * inv_wind) * delta_time * 60.0
        if self.dash_active:
            dash_amount = DASH_DISTANCE * min(delta_time / DASH_DURATION, 1.0)
            move_x = self.dash_dir[0] * dash_amount
            move_y = self.dash_dir[1] * dash_amount
        else:
            if self.move_left:
                move_x -= frame_speed
            if self.move_right:
                move_x += frame_speed
            if self.move_up:
                move_y += frame_speed
            if self.move_down:
                move_y -= frame_speed

        cam_x = self.camera.position[0]
        cam_y = self.camera.position[1]
        target_x = self.player.center_x
        target_y = self.player.center_y
        self.camera.position = (cam_x + (target_x - cam_x) * CAMERA_LERP,
                                cam_y + (target_y - cam_y) * CAMERA_LERP)

        if self.screen_shake_timer > 0.0:
            self.screen_shake_timer = max(0.0, self.screen_shake_timer - delta_time)
            intensity = 4.0 * (self.screen_shake_timer / 0.35)
            self.camera.position = (
                self.camera.position[0] + random.uniform(-intensity, intensity),
                self.camera.position[1] + random.uniform(-intensity, intensity)
            )

        self.shoot_timer      = max(0.0, self.shoot_timer      - delta_time * self.cooldown_multiplier)
        self.dmg_timer        = max(0.0, self.dmg_timer        - delta_time)
        self.protection_timer = max(0.0, self.protection_timer - delta_time)
        self.shockwave_timer  = max(0.0, self.shockwave_timer  - delta_time)

        if self.dmg_timer <= 0 and self.protection_timer <= 0 and not self.game_over:
            self.regen_timer += delta_time
        else:
            self.regen_timer = 0.0

        if self.hp < self.player_max_hp and self.regen_timer >= (2.5 if self.difficulty == 1 else 4.0 if self.difficulty == 2 else 6.0):
            self.hp = min(self.player_max_hp, self.hp + 1)
            self.regen_timer = 0.0

        old_x, old_y = self.player.center_x, self.player.center_y

        self.player.center_x += move_x
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_x = old_x

        self.player.center_y += move_y
        if arcade.check_for_collision_with_list(self.player, self.wall_list):
            self.player.center_y = old_y

        player_vx = self.player.center_x - old_x
        player_vy = self.player.center_y - old_y

        wm = self.camera.unproject((self.mx, self.my))
        dx  = wm[0] - self.player.center_x
        dy  = wm[1] - self.player.center_y
        rad = math.atan2(dy, dx)
        self.staff.center_x = self.player.center_x + math.cos(rad) * 12
        self.staff.center_y = self.player.center_y + math.sin(rad) * 12
        self.staff.angle    = 90 - math.degrees(rad)

        dead_shards  = set()
        dead_enemies = set()

        if self.shield_active:
            self.shield_sprite.visible = True
            shield_x = self.player.center_x + math.cos(rad) * SHIELD_FORWARD
            shield_y = self.player.center_y + math.sin(rad) * SHIELD_FORWARD
            self.shield_sprite.position = (shield_x, shield_y)
            self.shield_sprite.angle = self.staff.angle
            self.shield_timer += delta_time
            while self.shield_timer >= SHIELD_TICK_INTERVAL:
                self.shield_timer -= SHIELD_TICK_INTERVAL
                beam_dx = math.cos(rad)
                beam_dy = math.sin(rad)
                for e in self.enemies:
                    if e.room is not self.current_room:
                        continue
                    ex = e.body.center_x - shield_x
                    ey = e.body.center_y - shield_y
                    if math.hypot(ex, ey) <= SHIELD_RADIUS:
                        e.body.center_x += beam_dx * SHIELD_KNOCKBACK
                        e.body.center_y += beam_dy * SHIELD_KNOCKBACK
                        shield_counts = self.fusion_rune_counts(CardType.SHIELD)
                        if shield_counts:
                            fake = type("ShieldHit", (), {})()
                            fake.rune_counts = shield_counts
                            fake.damage_bonus = max(shield_counts.values()) - 1
                            fake.change_x = beam_dx
                            fake.change_y = beam_dy
                            e.hp -= 1 + fake.damage_bonus
                            self.apply_rune_hit_effects(fake, e, dead_enemies)
        else:
            self.shield_sprite.visible = False

        for p in list(self.particle_list):
            p.timer += delta_time
            if p.timer >= p.lifetime:
                p.remove_from_sprite_lists()
                continue
            p.center_x += p.change_x
            p.center_y += p.change_y
            p.alpha = int(255 * (1.0 - p.timer / p.lifetime))

        for s in list(self.shard_list):
            s.timer += delta_time
            if s.timer >= s.lifetime:
                if getattr(s, "is_cluster", False):
                    num_small = 10 + (self.slot_primary.charges - 1) * 5
                    for i in range(num_small):
                        a = random.uniform(0, 2 * math.pi)
                        ss = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.2)
                        ss.position = s.position
                        sl = Light(ss.center_x, ss.center_y, 20, (180, 200, 255), "soft")
                        self.light_layer.add(sl)
                        ss.light = sl
                        self.shard_list.append(ss)
                dead_shards.add(s)
                continue

            s.center_x += s.change_x
            s.center_y += s.change_y
            if s.light:
                s.light.position = s.position

            if arcade.check_for_collision_with_list(s, self.wall_list):
                dead_shards.add(s)
                continue

            if getattr(s, "is_fragment", False):
                continue

            for e in self.enemies:
                if id(e) in dead_enemies:
                    continue
                if e.room is self.current_room and not getattr(e, "immune_in_air", False) and arcade.check_for_collision(s, e.body):
                    base_dmg = 1 + getattr(s, "damage_bonus", 0)
                    # Burning Soul (LIFE UP + FIRE): +50 % Schaden pro Rune-Level wenn HP < 50 %
                    life_fire = self.fusion_rune_counts(CardType.LIFE_UP).get(RuneType.FIRE, 0)
                    if life_fire > 0 and self.hp < self.player_max_hp // 2:
                        base_dmg += life_fire
                    e.hp -= base_dmg
                    e.hit_timer = DAMAGE_FLASH_DURATION
                    e.body.color = (255, 180, 180)
                    if s.change_x != 0 or s.change_y != 0:
                        length = math.hypot(s.change_x, s.change_y) or 1.0
                        nx = s.change_x / length
                        ny = s.change_y / length
                        e.body.center_x += nx * HIT_KNOCKBACK
                        e.body.center_y += ny * HIT_KNOCKBACK

                    for i in range(10):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(1.8, 3.8)
                        particle = arcade.SpriteSolidColor(3, 3, (255, 180, 120))
                        particle.alpha = 220
                        particle.position = e.body.position
                        particle.change_x = math.cos(angle) * speed
                        particle.change_y = math.sin(angle) * speed
                        particle.timer = 0.0
                        particle.lifetime = 0.18
                        self.particle_list.append(particle)

                    if not s.is_piercing:
                        dead_shards.add(s)
                    self.apply_rune_hit_effects(s, e, dead_enemies)
                    # Venom Spread (SHOTGUN + POISON): Giftwolke beim Treffer
                    shotgun_poi = self.fusion_rune_counts(CardType.SHOTGUN).get(RuneType.POISON, 0)
                    if shotgun_poi > 0 and getattr(s, "is_spread", False):
                        for neighbor in self.enemies:
                            if neighbor is e and not getattr(neighbor, "immune_in_air", False):
                                continue
                            if neighbor.room is self.current_room and math.hypot(
                                    neighbor.body.center_x - e.body.center_x,
                                    neighbor.body.center_y - e.body.center_y) < 28 + 8 * shotgun_poi:
                                self.set_enemy_status(neighbor, "poison", 2.0 + shotgun_poi)
                    if e.hp <= 0:
                        if RuneType.ICE in getattr(s, "rune_counts", {}) and getattr(s, "rune_counts", {}).get(RuneType.ICE, 0) >= 3:
                            self.damage_enemies_near(e.body.center_x, e.body.center_y, 48, 2, dead_enemies, exclude=e)
                        dead_enemies.add(id(e))
                    break

        self.update_enemy_statuses(delta_time, dead_enemies)
        self.apply_aura_fusions(delta_time, dead_enemies)

        for s in dead_shards:
            if s.light and s.light in self.light_layer:
                self.light_layer.remove(s.light)
            s.remove_from_sprite_lists()

        actually_dead = [e for e in self.enemies if id(e) in dead_enemies]
        for e in actually_dead:
            if e.light in self.light_layer:
                self.light_layer.remove(e.light)
            e.body.remove_from_sprite_lists()
            for o in e.orbiters:
                o.remove_from_sprite_lists()
            if e.is_boss:
                self.boss_defeated = True
                self.complete_pending_fusion_after_boss()
            self.enemies.remove(e)

        if actually_dead:
            self.coins += 5 * len(actually_dead)

        for e in self.enemies:
            e.update(delta_time, self.player.center_x, self.player.center_y, player_vx, player_vy)

        # Handle HandEnemy stomp landings (pending stomp flag)
        for e in list(self.enemies):
            if getattr(e, "pending_stomp", False):
                    e.pending_stomp = False
                    cx, cy = e.body.center_x, e.body.center_y
                    self.enemy_shockwaves.append({
                        "x": cx,
                        "y": cy,
                        "radius": 8.0,
                        "speed": 180.0,
                        "thickness": 18.0,
                        "max_radius": 360.0,
                        "alpha": 220,
                        "player_hit": False,
                    })
                    self.screen_shake_timer = max(self.screen_shake_timer, 0.35)

                    # gray stomp particles
                    for i in range(22):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(0.8, 3.2)
                        part = arcade.SpriteSolidColor(4, 4, (150, 150, 160))
                        part.alpha = 220
                        part.position = (cx, cy)
                        part.change_x = math.cos(angle) * speed
                        part.change_y = math.sin(angle) * speed
                        part.timer = 0.0
                        part.lifetime = 0.6
                        self.particle_list.append(part)

                    # Damage nearby enemies on impact
                    for other in list(self.enemies):
                        if other is e:
                            continue
                        od = math.hypot(other.body.center_x - cx, other.body.center_y - cy)
                        if od < 48:
                            other.hp -= 1
                            other.hit_timer = DAMAGE_FLASH_DURATION
                            other.body.color = (200, 140, 255)
                            for i in range(8):
                                a = random.uniform(0, 2 * math.pi)
                                sp = arcade.SpriteSolidColor(3, 3, (180, 120, 220))
                                sp.alpha = 220
                                sp.position = other.body.position
                                sp.change_x = math.cos(a) * random.uniform(0.8, 2.4)
                                sp.change_y = math.sin(a) * random.uniform(0.8, 2.4)
                                sp.timer = 0.0
                                sp.lifetime = 0.7
                                self.particle_list.append(sp)
                            if other.hp <= 0:
                                dead_enemies.add(id(other))
        for ring in list(self.enemy_shockwaves):
            ring["radius"] += ring["speed"] * delta_time
            ring["alpha"] = int(180 * max(0.0, 1.0 - ring["radius"] / ring["max_radius"]))
            remove_ring = False
            if ring["radius"] >= ring["max_radius"]:
                remove_ring = True
            else:
                for sample_i in range(8):
                    a = sample_i * (math.pi / 4)
                    self._collision_probe.center_x = ring["x"] + math.cos(a) * ring["radius"]
                    self._collision_probe.center_y = ring["y"] + math.sin(a) * ring["radius"]
                    if arcade.check_for_collision_with_list(self._collision_probe, self.wall_list):
                        remove_ring = True
                        break
            if remove_ring:
                self.enemy_shockwaves.remove(ring)
                continue
            player_dist = math.hypot(self.player.center_x - ring["x"], self.player.center_y - ring["y"])
            if not self.dash_active and not ring["player_hit"]:
                if abs(player_dist - ring["radius"]) <= ring["thickness"] * 0.8:
                    self.hp -= 4
                    self.dmg_timer = DAMAGE_COOLDOWN
                    ring["player_hit"] = True
                    if self.hp <= 0:
                        self.game_over = True

        if self.dmg_timer <= 0 and self.protection_timer <= 0:
            for e in self.enemies:
                if e.room is not self.current_room:
                    continue
                if self.dash_active:
                    continue
                hit = (arcade.check_for_collision(self.player, e.body) or
                       arcade.check_for_collision_with_list(self.player, e.orbiters))
                if hit:
                    damage = 2 if getattr(e, "behavior", None) == "blocker" and getattr(e, "is_dashing", False) else 1
                    self.hp       -= damage
                    self.dmg_timer = DAMAGE_COOLDOWN
                    if self.hp <= 0:
                        self.game_over = True
                    # Unstable Core (LIFE UP + EXPLOSION): AoE-Explosion wenn Spieler Schaden nimmt
                    life_exp = self.fusion_rune_counts(CardType.LIFE_UP).get(RuneType.EXPLOSION, 0)
                    if life_exp > 0:
                        self.damage_enemies_near(self.player.center_x, self.player.center_y,
                                                 30 + 12 * life_exp, life_exp, dead_enemies)
                        self.screen_shake_timer = max(self.screen_shake_timer, 0.12)
                    # Toxic Blood (LIFE UP + POISON): Angreifer vergiftet sich
                    life_poi = self.fusion_rune_counts(CardType.LIFE_UP).get(RuneType.POISON, 0)
                    if life_poi > 0:
                        self.set_enemy_status(e, "poison", 2.0 + life_poi)
                    break

        for s in list(self.shard_list):
            if getattr(s, "is_spinning", False):
                s.spin_angle += s.spin_speed * delta_time
                s.center_x = self.player.center_x + math.cos(s.spin_angle) * s.spin_radius
                s.center_y = self.player.center_y + math.sin(s.spin_angle) * s.spin_radius
                if s.light:
                    s.light.position = s.position

        if self.current_room and not self.current_room.cleared:
            if not any(e.room is self.current_room for e in self.enemies):
                self.current_room.cleared = True
                self._update_doors()
                if self.current_room is self.boss_room:
                    self.boss_defeated = True
                    self.complete_pending_fusion_after_boss()
                    if not self.in_shop_hub:
                        self.enter_boss_hub()

        for r in self.rooms:
            if r is not self.current_room and r.contains(
                    self.player.center_x, self.player.center_y):
                self.enter_room(r)
                break

        self.player_light.position = self.player.position

    def on_mouse_motion(self, x, y, dx, dy):
        self.mx, self.my = x, y

    def _handle_inventory_click(self, x: float, y: float, button: int):
        """Geteilte Klick-Logik für Tab-Inventar und Hub-Inventar."""
        # Tab-Klick
        for tl, tb, tr, tt, page in self.inv_tab_rects:
            if tl <= x <= tr and tb <= y <= tt:
                self.inv_page = page
                self.selected_inventory_card = None
                return

        # Seite 1 (Runen) und Seite 2 (Fusionen) – kein Card-/Slot-Klick
        if self.inv_page != 0:
            return

        # Karten-Klick
        for cl, cb, cr, ct, cid in self.inv_card_rects:
            if cl <= x <= cr and cb <= y <= ct:
                self.selected_inventory_card = (
                    None if self.selected_inventory_card == cid else cid)
                return

        # Ausrüstungs-Slots
        BOX_W, BOX_H = 195, 148
        by = 85
        for slot_x, slot_name in (
            (SCREEN_WIDTH / 2 - 220, "primary"),
            (SCREEN_WIDTH / 2 + 220, "secondary"),
        ):
            if (slot_x - BOX_W / 2 <= x <= slot_x + BOX_W / 2 and
                    by - BOX_H / 2 <= y <= by + BOX_H / 2):
                if self.selected_inventory_card:
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.equip_card_from_inventory(
                            self.selected_inventory_card, "primary")
                    elif button == arcade.MOUSE_BUTTON_RIGHT:
                        self.equip_card_from_inventory(
                            self.selected_inventory_card, "secondary")
                    self.selected_inventory_card = None
                else:
                    if button == arcade.MOUSE_BUTTON_LEFT:
                        self.unequip_slot(slot_name)
                return

    def on_mouse_press(self, x, y, button, modifiers):
        if self.showing_dev_menu:
            # Zurück / Schließen
            if self.dev_menu_close_rect and self._rect_contains(self.dev_menu_close_rect, x, y):
                if self.dev_menu_category:
                    self.dev_menu_button_pressed = ("back", None)
                    self.dev_menu_category = None
                else:
                    self.dev_menu_button_pressed = ("close", None)
                    self.showing_dev_menu = False
                return
            if self.dev_menu_category:
                # Klick auf Sub-Menü-Eintrag
                for left, bottom, right, top, action in self.dev_menu_sub_rects:
                    if left <= x <= right and bottom <= y <= top:
                        self.dev_menu_button_pressed = ("sub", action)
                        self._execute_dev_action(action)
                        return
            else:
                # Klick auf Kategorie
                for left, bottom, right, top, cat_id in self.dev_menu_category_rects:
                    if left <= x <= right and bottom <= y <= top:
                        self.dev_menu_button_pressed = ("cat", cat_id)
                        self.dev_menu_category = cat_id
                        return
            return

        if self.handle_crafting_click(x, y):
            return

        if self.in_training_cage:
            if self.training_enemy_button_rect and self._rect_contains(self.training_enemy_button_rect, x, y):
                self.training_enemy_menu_open = not self.training_enemy_menu_open
                return
            for left, bottom, right, top, enemy_type in self.training_enemy_option_rects:
                if left <= x <= right and bottom <= y <= top:
                    self._spawn_training_enemy(enemy_type)
                    return
            if self.training_exit_rect and self._rect_contains(self.training_exit_rect, x, y):
                self.exit_training_cage()
                return

        if CARD_SYSTEM_AVAILABLE and self.skill_tree_ui and self.skill_tree_ui.visible and button == arcade.MOUSE_BUTTON_LEFT:
            for node in self.skill_tree.get_all_nodes():
                nx = (node.x - self.skill_tree.camera_x) * self.skill_tree.zoom + SCREEN_WIDTH // 2
                ny = (node.y - self.skill_tree.camera_y) * self.skill_tree.zoom + SCREEN_HEIGHT // 2
                if math.hypot(x - nx, y - ny) <= 24 * self.skill_tree.zoom:
                    self.skill_tree_ui.selected_node = node
                    return
            return

        if CARD_SYSTEM_AVAILABLE and self.mini_map_ui and self.mini_map_ui.visible:
            return

        if self.in_shop_hub:
            if self.hub_shop_menu2:
                if self.hub_refresh_button_rect and self._rect_contains(self.hub_refresh_button_rect, x, y):
                    self.open_shop(hub=True)
                    return
                if self.hub_craft_button_rect and self._rect_contains(self.hub_craft_button_rect, x, y):
                    if self.crafting_station_ui:
                        self.crafting_station_ui.visible = True
                    return
                if self.hub_skilltree_button_rect and self._rect_contains(self.hub_skilltree_button_rect, x, y):
                    if self.skill_tree_ui:
                        self.skill_tree_ui.visible = True
                    return
                if self.hub_shop_back_rect and self._rect_contains(self.hub_shop_back_rect, x, y):
                    self.hub_shop_menu2 = False
                    return
                for left, bottom, right, top, cid in self.hub_shop_card_rects:
                    if left <= x <= right and bottom <= y <= top:
                        self.buy_card(cid)
                        return
            else:
                if self.hub_inventory_open:
                    self._handle_inventory_click(x, y, button)
                    # Inventar-Button schließt die Ansicht
                    if self.hub_inventory_button_rect and self._rect_contains(
                            self.hub_inventory_button_rect, x, y):
                        self.hub_inventory_open = False
                        self.selected_inventory_card = None
                    return
                if self.hub_shop_button_rect and self._rect_contains(self.hub_shop_button_rect, x, y):
                    self.open_shop(hub=True)
                    return
                if self.hub_craft_button_rect and self._rect_contains(self.hub_craft_button_rect, x, y):
                    if self.crafting_station_ui:
                        self.crafting_station_ui.visible = True
                    return
                if self.hub_skilltree_button_rect and self._rect_contains(self.hub_skilltree_button_rect, x, y):
                    if self.skill_tree_ui:
                        self.skill_tree_ui.visible = True
                    return
                if self.hub_inventory_button_rect and self._rect_contains(self.hub_inventory_button_rect, x, y):
                    self.hub_inventory_open = not self.hub_inventory_open
                    return
                if self.hub_training_button_rect and self._rect_contains(self.hub_training_button_rect, x, y):
                    self.in_shop_hub = False
                    self.hub_shop_menu2 = False
                    self.start_training_cage()
                    return
                if self.hub_return_button_rect and self._rect_contains(self.hub_return_button_rect, x, y):
                    if self.hub_can_return:
                        self.in_shop_hub = False
                        self.hub_shop_menu2 = False
                        self._new_dungeon()
                    return
            return

        if self.showing_shop:
            start_x = SCREEN_WIDTH/2 - 300
            y_center = SCREEN_HEIGHT/2
            for i, cid in enumerate(self.shop_choices):
                card = self.cards_db[cid]
                texture = self.card_textures.get(card.id)
                width = texture.width if texture else 220
                height = texture.height if texture else 280
                cx = start_x + i * 300
                left = cx - width/2
                right = cx + width/2
                top = y_center + 10 + height/2
                bottom = y_center + 10 - height/2
                if left <= x <= right and bottom <= y <= top:
                    self.buy_card(cid)
                    return
            return

        if not self.in_shop_hub and not self.showing_inventory and not self.showing_shop:
            if button == arcade.MOUSE_BUTTON_LEFT:
                if self.dev_menu_button_rect and self._rect_contains(self.dev_menu_button_rect, x, y):
                    self.showing_dev_menu = True
                    return
                if self.teleport_boss_button_rect and self._rect_contains(self.teleport_boss_button_rect, x, y):
                    if hasattr(self, 'boss_room') and self.boss_room:
                        self.enter_room(self.boss_room)
                    return
                if self.teleport_room_button_rect and self._rect_contains(self.teleport_room_button_rect, x, y):
                    if self.rooms:
                        self.enter_room(self.rooms[0])
                    return

        if self.showing_inventory:
            self._handle_inventory_click(x, y, button)
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            self.use_primary()
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.use_secondary()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.stop_shield()
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.dev_menu_button_pressed = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if CARD_SYSTEM_AVAILABLE and self.skill_tree_ui and self.skill_tree_ui.visible:
            if scroll_y > 0:
                self.skill_tree.zoom_in()
            elif scroll_y < 0:
                self.skill_tree.zoom_out()
            return
            slider_defs = [
                ("Move Speed", "movement", 0.5, 2.5),
                ("Cooldown", "cooldown", 0.3, 2.0),
                ("Attack Speed", "attack_speed", 0.4, 2.5),
                ("Dash Distance", "dash_distance", 16.0, 128.0),
                ("Dash Duration", "dash_duration", 0.05, 0.4),
                ("Shield Radius", "shield_radius", 6.0, 50.0),
                ("Shield Knockback", "shield_knockback", 0.0, 80.0),
                ("Enemy Speed", "enemy_speed", 8.0, 80.0),
                ("Shard Speed", "shard_speed", 2.0, 14.0),
                ("Shard Lifetime", "shard_lifetime", 0.5, 5.0),
                ("Damage Cooldown", "damage_cooldown", 0.1, 1.5),
                ("Spawn Protection", "spawn_protection", 0.0, 3.0),
                ("Camera Zoom", "camera_zoom", 1.5, 6.0),
                ("Enemy Aggro", "enemy_aggro", 0.0, 3.0),
                ("Health Regen", "regen_speed", 0.2, 3.0),
            ]
            visible_height = slider_top - slider_bottom
            total_height = len(slider_defs) * 56
            if total_height <= visible_height:
                self.dev_menu_slider_scroll = 0.0
            else:
                self.dev_menu_slider_scroll = max(-(total_height - visible_height), min(0.0, self.dev_menu_slider_scroll))

    def start_shield(self, rad):
        self.shield_active = True
        self.shield_timer = 0.0
        self.shield_sprite.visible = True
        self.shield_sprite.position = (
            self.player.center_x + math.cos(rad) * SHIELD_FORWARD,
            self.player.center_y + math.sin(rad) * SHIELD_FORWARD)
        self.shield_sprite.angle = self.staff.angle

    def stop_shield(self):
        self.shield_active = False
        self.shield_sprite.visible = False

    def start_dash(self):
        if self.dash_active or self.dash_cooldown > 0:
            return

        dx = 0.0
        dy = 0.0
        if self.move_left:
            dx -= 1.0
        if self.move_right:
            dx += 1.0
        if self.move_up:
            dy += 1.0
        if self.move_down:
            dy -= 1.0

        if dx == 0.0 and dy == 0.0:
            wm = self.camera.unproject((self.mx, self.my))
            dx = wm[0] - self.player.center_x
            dy = wm[1] - self.player.center_y

        length = math.hypot(dx, dy)
        if length == 0.0:
            return

        self.dash_dir = (dx / length, dy / length)
        self.dash_active = True
        self.dash_timer = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN

    def use_primary(self):
        if self.shoot_timer > 0:
            return

        if self.slot_primary.card_id:
            cid = self.slot_primary.card_id
            card = self.cards_db.get(cid)
            if card is None:
                self.slot_primary.card_id = None
            else:
                rad = math.atan2(self.camera.unproject((self.mx, self.my))[1] - self.player.center_y,
                                 self.camera.unproject((self.mx, self.my))[0] - self.player.center_x)

                if cid == "shield":
                    self.start_shield(rad)
                    self.shoot_timer = SHARD_COOLDOWN * self.attack_speed_multiplier
                    return

                if card.kind == "shot":
                    if cid == "normal_shot":
                        num_shards = max(1, self.slot_primary.charges)
                        for i in range(num_shards):
                            spread = (i - (num_shards - 1) / 2) * 0.08
                            a = rad + spread
                            s = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False)
                            s.position = self.staff.position
                            sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
                            self.light_layer.add(sl)
                            s.light = sl
                            self.attach_fusion_to_shard(s, CardType.NORMAL_SHOT)
                            self.shard_list.append(s)
                    elif cid == "shotgun":
                        num_shards = 5 + (self.slot_primary.charges - 1) * 2
                        for i in range(num_shards):
                            spread = random.uniform(-0.5, 0.5)
                            a = rad + spread
                            s = Shard(self.tex_shard, a, SHARD_SPEED, is_piercing=False, lifetime=0.5)
                            s.is_spread = True
                            s.position = self.staff.position
                            sl = Light(s.center_x, s.center_y, 25, (200, 180, 255), "soft")
                            self.light_layer.add(sl)
                            s.light = sl
                            self.attach_fusion_to_shard(s, CardType.SHOTGUN)
                            self.shard_list.append(s)
                    elif cid == "cluster":
                        num_shards = 10 + (self.slot_primary.charges - 1) * 2
                        for i in range(num_shards):
                            angle = i * (2 * math.pi / num_shards)
                            s = Shard(self.tex_shard, angle, 0.0, is_piercing=False, lifetime=2.5)
                            s.is_spinning = True
                            s.spin_angle = angle
                            s.spin_radius = 36
                            s.spin_speed = 4.0
                            s.position = (self.player.center_x + math.cos(angle) * s.spin_radius,
                                          self.player.center_y + math.sin(angle) * s.spin_radius)
                            sl = Light(s.center_x, s.center_y, 25, (180, 200, 255), "soft")
                            self.light_layer.add(sl)
                            s.light = sl
                            self.attach_fusion_to_shard(s, CardType.SPIN)
                            self.shard_list.append(s)
                    elif cid == "shockwave":
                        if self.shockwave_timer <= 0:
                            self.do_shockwave()
                            self.shockwave_timer = 5.0
                self.shoot_timer = SHARD_COOLDOWN * self.attack_speed_multiplier
                return

        rad = math.atan2(self.camera.unproject((self.mx, self.my))[1] - self.player.center_y,
                         self.camera.unproject((self.mx, self.my))[0] - self.player.center_x)
        s = Shard(self.tex_shard, rad, SHARD_SPEED, is_piercing=False)
        s.position = self.staff.position
        sl = Light(s.center_x, s.center_y, 35, (150, 200, 255), "soft")
        self.light_layer.add(sl)
        s.light = sl
        self.attach_fusion_to_shard(s, CardType.NORMAL_SHOT)
        self.shard_list.append(s)
        self.shoot_timer = SHARD_COOLDOWN * self.attack_speed_multiplier

    def use_secondary(self):
        if self.slot_secondary.card_id and self.slot_secondary.charges > 0:
            cid = self.slot_secondary.card_id
            card = self.cards_db[cid]
            if card.kind != "buff":
                return
            if cid == "shield":
                rad = math.atan2(self.camera.unproject((self.mx, self.my))[1] - self.player.center_y,
                                 self.camera.unproject((self.mx, self.my))[0] - self.player.center_x)
                self.start_shield(rad)
                self.slot_secondary.use_charge()
                return
            card.apply_fn(self)
            self.slot_secondary.use_charge()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            if self.showing_dev_menu:
                if self.dev_menu_category:
                    self.dev_menu_category = None
                else:
                    self.showing_dev_menu = False
                return
            if self.in_shop_hub and getattr(self, "hub_inventory_open", False):
                self.hub_inventory_open = False
                return
            if CARD_SYSTEM_AVAILABLE and self.mini_map_ui and self.mini_map_ui.visible:
                self.mini_map_ui.visible = False
                return
            if CARD_SYSTEM_AVAILABLE and self.crafting_station_ui and self.crafting_station_ui.visible:
                self.crafting_station_ui.visible = False
                return
            if CARD_SYSTEM_AVAILABLE and self.skill_tree_ui and self.skill_tree_ui.visible:
                self.skill_tree_ui.visible = False
                return
            if self.showing_shop:
                self.showing_shop = False
                return
            if self.showing_inventory:
                self.showing_inventory = False
                self.selected_inventory_card = None
                return
            self.window.show_view(StartMenuView())
            return

        if symbol == arcade.key.R:
            if self.game_over:
                self.setup()
            return

        if symbol == arcade.key.M:
            if self.game_over:
                self.window.show_view(StartMenuView())
                return
            if CARD_SYSTEM_AVAILABLE and self.mini_map_ui:
                self.mini_map_ui.toggle_visibility()
            return

        if CARD_SYSTEM_AVAILABLE and self.mini_map_ui and self.mini_map_ui.visible:
            return

        if symbol == arcade.key.Q:
            if not self.game_over and not self.win:
                self.map_timer = max(0.0, self.map_timer - 30.0)
            return

        if symbol == arcade.key.N:
            if self.game_over:
                return
            if not self.boss_defeated:
                return
            if self.in_shop_hub:
                return
            if self.showing_inventory:
                self.showing_inventory = False
                self.selected_inventory_card = None
            self.showing_shop = not self.showing_shop
            if self.showing_shop:
                self.open_shop()
            return

        if symbol == arcade.key.TAB:
            if self.game_over:
                return
            if self.showing_shop:
                self.showing_shop = False
            self.showing_inventory = not self.showing_inventory
            if self.showing_inventory:
                self.selected_inventory_card = None
            return

        # ─── New Card System Controls ─────────────────────────────────────
        if CARD_SYSTEM_AVAILABLE:
            if self.handle_crafting_key(symbol):
                return
            # Skill Tree Toggle (G key)
            if symbol == ord('G') or symbol == ord('g'):
                if self.skill_tree_ui and self.in_shop_hub:
                    self.skill_tree_ui.toggle_visibility()
                return
            
            # Crafting Station Toggle (C key)
            if symbol == ord('C') or symbol == ord('c'):
                if self.crafting_station_ui and self.in_shop_hub:
                    self.crafting_station_ui.toggle_visibility()
                return
            
            # Skill Tree Navigation (WASD when visible)
            if self.skill_tree_ui and self.skill_tree_ui.visible:
                pan_speed = 30.0
                if symbol == arcade.key.W or symbol == arcade.key.UP:
                    self.skill_tree.pan(0, pan_speed)
                    return
                elif symbol == arcade.key.S or symbol == arcade.key.DOWN:
                    self.skill_tree.pan(0, -pan_speed)
                    return
                elif symbol == arcade.key.A or symbol == arcade.key.LEFT:
                    self.skill_tree.pan(-pan_speed, 0)
                    return
                elif symbol == arcade.key.D or symbol == arcade.key.RIGHT:
                    self.skill_tree.pan(pan_speed, 0)
                    return
                elif symbol == arcade.key.EQUAL or symbol == arcade.key.PLUS:
                    self.skill_tree.zoom_in()
                    return
                elif symbol == arcade.key.MINUS:
                    self.skill_tree.zoom_out()
                    return

        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.move_left = True
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.move_right = True
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.move_up = True
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.move_down = True
        if symbol == arcade.key.SPACE or symbol == arcade.key.LSHIFT or symbol == arcade.key.RSHIFT:
            if not self.game_over and not self.showing_shop and not self.showing_inventory:
                self.start_dash()

    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.A or symbol == arcade.key.LEFT:
            self.move_left = False
        if symbol == arcade.key.D or symbol == arcade.key.RIGHT:
            self.move_right = False
        if symbol == arcade.key.W or symbol == arcade.key.UP:
            self.move_up = False
        if symbol == arcade.key.S or symbol == arcade.key.DOWN:
            self.move_down = False

    def draw_pixel_screen(self, title, sub, title_col):
        arcade.draw_rect_filled(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        SCREEN_WIDTH, SCREEN_HEIGHT),
            (0, 0, 0, 185))
        arcade.draw_rect_outline(
            arcade.XYWH(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                        640, 220),
            title_col, 4)
        for ox, oy in [(4, -4), (2, -2)]:
            arcade.draw_text(
                title,
                SCREEN_WIDTH / 2 + ox, SCREEN_HEIGHT / 2 + 55 + oy,
                (0, 0, 0, 210), 54,
                font_name=self.font, bold=True,
                anchor_x="center", anchor_y="center")
        arcade.draw_text(
            title,
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 55,
            title_col, 54,
            font_name=self.font, bold=True,
            anchor_x="center", anchor_y="center")
        arcade.draw_text(
            sub,
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30,
            arcade.color.LIGHT_GRAY, 16,
            font_name=self.font,
            anchor_x="center", anchor_y="center")


class StartMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.state = "main"
        self.difficulties = ["Einfach", "Normal", "Schwer"]
        self.selected_index = 1
        self.music_volume = 0.6
        self.slider_dragging = False
        self.button_rects = {}
        self.font = PIXEL_FONT

        bp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        font_path = os.path.join(bp, "BoldPixels.ttf")
        if os.path.exists(font_path):
            arcade.load_font(font_path)
            self.font = os.path.splitext(os.path.basename(font_path))[0]

        self.music_sound = None
        self.music_player = None
        music_path = os.path.join(bp, "Bildschirmaufnahme 2026-05-25 201940.mp3")
        if os.path.exists(music_path):
            self.music_sound = arcade.load_sound(music_path)

    def on_show_view(self):
        if self.music_sound and not self.music_player:
            try:
                self.music_player = arcade.play_sound(self.music_sound, volume=self.music_volume, loop=True)
            except Exception:
                self.music_player = None

    def draw_button(self, x, y, width, height, text, active=True):
        color = arcade.color.DARK_BLUE if active else arcade.color.DARK_GRAY
        border = arcade.color.WHITE if active else arcade.color.GRAY
        draw_rectangle_filled(x + width / 2, y - height / 2, width, height, color)
        draw_rectangle_outline(x + width / 2, y - height / 2, width, height, border, 3)
        arcade.draw_text(text, x + width / 2, y - height / 2, arcade.color.WHITE, 20,
                         font_name=self.font, anchor_x="center", anchor_y="center")

    def point_in_rect(self, x, y, rect):
        left, bottom, right, top = rect
        return left <= x <= right and bottom <= y <= top

    def button_rect(self, x, y, width, height):
        return (x, y - height, x + width, y)

    def on_draw(self):
        self.clear()
        draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                     SCREEN_WIDTH, SCREEN_HEIGHT,
                                     (12, 18, 35, 255))
        arcade.draw_text("FROG ROGUELIKE", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 180,
                         arcade.color.WHITE, 52, font_name=self.font,
                         anchor_x="center")

        if self.state == "main":
            self.draw_button(312, SCREEN_HEIGHT / 2 + 20, 400, 80, "Start")
            self.draw_button(312, SCREEN_HEIGHT / 2 - 110, 400, 80, "Music")

        elif self.state == "difficulty":
            arcade.draw_text("Wähle die Schwierigkeit:", SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2 + 120,
                             arcade.color.LIGHT_GRAY, 24,
                             font_name=self.font, anchor_x="center")
            for i, label in enumerate(self.difficulties):
                color = arcade.color.YELLOW if i == self.selected_index else arcade.color.WHITE
                self.draw_button(312, SCREEN_HEIGHT / 2 + 20 - i * 100, 400, 80, label)

        elif self.state == "music":
            arcade.draw_text("Musiklautstärke:", SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2 + 120,
                             arcade.color.LIGHT_GRAY, 24,
                             font_name=self.font, anchor_x="center")
            slider_left = SCREEN_WIDTH / 2 - 200
            slider_right = SCREEN_WIDTH / 2 + 200
            slider_y = SCREEN_HEIGHT / 2
            draw_rectangle_filled(SCREEN_WIDTH / 2, slider_y,
                                         410, 40, (50, 50, 70, 220))
            draw_rectangle_filled((slider_left + slider_right) / 2, slider_y,
                                         slider_right - slider_left, 10,
                                         arcade.color.WHITE)
            handle_x = slider_left + self.music_volume * (slider_right - slider_left)
            arcade.draw_circle_filled(handle_x, slider_y, 14, arcade.color.AUBURN)
            arcade.draw_text(f"Lautstärke: {int(self.music_volume * 100)}%",
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80,
                             arcade.color.LIGHT_GRAY, 18,
                             font_name=self.font, anchor_x="center")
            self.button_rects["Back"] = (SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 170,
                                          SCREEN_WIDTH / 2 + 120, SCREEN_HEIGHT / 2 - 120)
            draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 145,
                                         240, 40, arcade.color.DARK_BLUE)
            draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 145,
                                          240, 40, arcade.color.WHITE, 3)
            arcade.draw_text("Zurück", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 145,
                             arcade.color.WHITE, 18,
                             font_name=self.font, anchor_x="center", anchor_y="center")

    def update_volume(self, x):
        slider_left = SCREEN_WIDTH / 2 - 200
        slider_right = SCREEN_WIDTH / 2 + 200
        self.set_volume((x - slider_left) / (slider_right - slider_left))

    def on_mouse_press(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.state == "main":
            start_rect = self.button_rect(312, SCREEN_HEIGHT / 2 + 20, 400, 80)
            music_rect = self.button_rect(312, SCREEN_HEIGHT / 2 - 110, 400, 80)
            if self.point_in_rect(x, y, start_rect):
                self.state = "difficulty"
                return
            if self.point_in_rect(x, y, music_rect):
                self.state = "music"
                return

        elif self.state == "difficulty":
            for i, label in enumerate(self.difficulties):
                rect = self.button_rect(312, SCREEN_HEIGHT / 2 + 20 - i * 100, 400, 80)
                if self.point_in_rect(x, y, rect):
                    self.selected_index = i
                    difficulty = i + 1
                    self.window.show_view(GameView(difficulty=difficulty))
                    return

        elif self.state == "music":
            slider_left = SCREEN_WIDTH / 2 - 200
            slider_right = SCREEN_WIDTH / 2 + 200
            slider_y = SCREEN_HEIGHT / 2
            if slider_left <= x <= slider_right and slider_y - 20 <= y <= slider_y + 20:
                self.slider_dragging = True
                self.update_volume(x)
                return
            back_rect = self.button_rect(SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 - 145, 240, 40)
            if self.point_in_rect(x, y, back_rect):
                self.state = "main"
                return

    def on_mouse_release(self, x, y, button, modifiers):
        self.slider_dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.state == "music" and self.slider_dragging:
            self.update_volume(x)

    def set_volume(self, volume):
        self.music_volume = min(1.0, max(0.0, volume))
        if self.music_player:
            try:
                self.music_player.volume = self.music_volume
            except Exception:
                pass

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.state = "main"
            return
        if self.state == "main":
            if symbol == arcade.key.UP or symbol == arcade.key.W:
                self.selected_index = max(0, self.selected_index - 1)
            elif symbol == arcade.key.DOWN or symbol == arcade.key.S:
                self.selected_index = min(len(self.difficulties) - 1, self.selected_index + 1)
            elif symbol == arcade.key.ENTER or symbol == arcade.key.SPACE:
                self.state = "difficulty"
                return
            elif symbol == arcade.key.M:
                self.state = "music"
                return
        elif self.state == "difficulty":
            if symbol == arcade.key.KEY_1:
                self.selected_index = 0
            elif symbol == arcade.key.KEY_2:
                self.selected_index = 1
            elif symbol == arcade.key.KEY_3:
                self.selected_index = 2
            elif symbol == arcade.key.ENTER or symbol == arcade.key.SPACE:
                difficulty = self.selected_index + 1
                self.window.show_view(GameView(difficulty=difficulty))
                return
        elif self.state == "music":
            if symbol == arcade.key.LEFT or symbol == arcade.key.A:
                self.set_volume(self.music_volume - 0.05)
            elif symbol == arcade.key.RIGHT or symbol == arcade.key.D:
                self.set_volume(self.music_volume + 0.05)


def main():
    # Erstellt das Hauptfenster mit den oben definierten Einstellungen
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    
    # Zeigt das Startmenü, in dem die Schwierigkeit gewählt werden kann
    start_menu = StartMenuView()
    window.show_view(start_menu)
    
    # Startet die Arcade-Spielschleife
    arcade.run()

if __name__ == "__main__":
    main()
    
 