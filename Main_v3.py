import pygame
import math
import random
import socket
import threading
import pickle
import sys
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class GameState(Enum):
    MODE_SELECT = 0
    LOGIN = 1
    INTRO = 2
    PLAYING = 3
    LEVEL_COMPLETE = 4
    GAME_OVER = 5

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

# Network Configuration
HOST = ''
PORT = 5050
BUFFER_SIZE = 8192

# Display Configuration
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60
TILE_SIZE = 40
INFO_BAR_HEIGHT = 100
MAZE_GAP = 20

# Game Configuration
PLAYER_SPEED = 4
PLAYER_HEALTH = 100
PLAYER_ATTACK_DAMAGE = 15
PLAYER_ATTACK_RANGE = TILE_SIZE * 1.5
PLAYER_ATTACK_COOLDOWN = 300

ENEMY_SPEED_PATROL = 2
ENEMY_SPEED_CHASE = 3
ENEMY_HEALTH = 30
ENEMY_DAMAGE = 5
ENEMY_ATTACK_RANGE = TILE_SIZE * 1.2
ENEMY_ATTACK_COOLDOWN = 1000
ENEMY_DETECTION_RANGE = TILE_SIZE * 6

GOLD_VALUE = 25
HEALTH_POTION_HEAL = 20
WALL_HEALTH = 40

# Enhanced Colors
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (220, 50, 50),
    'green': (50, 220, 50),
    'blue': (50, 50, 220),
    'yellow': (255, 255, 0),
    'gold': (255, 215, 0),
    'cyan': (0, 255, 255),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0),
    'dark_gray': (40, 40, 40),
    'gray': (100, 100, 100),
    'light_gray': (180, 180, 180),
    'floor': (30, 30, 30),
    'wall': (60, 80, 120),
    'breakable_wall': (120, 120, 120),
    'health_bar': (255, 0, 0),
    'health_bar_bg': (50, 50, 50),
    # New UI colors
    'ui_bg': (20, 20, 35),
    'ui_panel': (35, 35, 55),
    'ui_border': (70, 70, 100),
    'ui_accent': (100, 150, 255),
    'ui_hover': (120, 170, 255),
    'ui_text': (230, 230, 240),
    'ui_text_dim': (150, 150, 160),
    'gradient_top': (25, 25, 45),
    'gradient_bottom': (15, 15, 25),
}

# ============================================================================
# LEVEL MAPS
# ============================================================================

LEVELS = [
    # Level 1 - Tutorial
    [
        "####################",
        "#P.................#",
        "#.####.####.####.###",
        "#.#..#.#..#.#..#...#",
        "#.#..#.#..#.#..###.#",
        "#.####.####.####...#",
        "#.....G............#",
        "#.###.####.###.###.#",
        "#.#.#.#..#.#.#.#.#.#",
        "#.#.#.#..#.#.#.#.#.#",
        "#.###.####.###.###.#",
        "#........E.........#",
        "#.###.###.###.###.##",
        "#.#.#.#.#.#.#.#.#..#",
        "#.#.#.#.#.#.#.#.#.##",
        "#.###.###.###.###..#",
        "#.................L#",
        "####################"
    ],
    # Level 2 - Combat Practice
    [
        "####################",
        "#P....E....E.....E.#",
        "#.#####.####.#####.#",
        "#.....#.#..#.#.....#",
        "####..#.#..#.#..####",
        "#..#..G.####.G..#..#",
        "#..#############...#",
        "#..............#...#",
        "#..############....#",
        "#..#........E.#....#",
        "#..#.##########....#",
        "#..#.#........#....#",
        "#..#.#.H####K.#....#",
        "#....#........#....#",
        "######.########....#",
        "#..................#",
        "#.................L#",
        "####################"
    ],
    # Level 3 - Maze Challenge
    [
        "####################",
        "#P.#...............#",
        "#.###.###.###.###.##",
        "#...#.#.#.#.#.#.#..#",
        "##..#.#.#.#.#.#.#.##",
        "#...#.#.#.#.#.#.#..#",
        "#.###.###.###.###.##",
        "#...........E......#",
        "#.###.###.###.###.##",
        "#.#.B.#.B.#.B.#.B..#",
        "#.#.#.#.#.#.#.#.#.##",
        "#.#.#.#G#.#H#.#K#..#",
        "#.#.#.###.###.###.##",
        "#.#.#..............#",
        "#.#.##############.#",
        "#.E................#",
        "#.................L#",
        "####################"
    ],
]

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def draw_gradient_rect(surface, rect, color_top, color_bottom):
    """Draw a vertical gradient rectangle"""
    for y in range(rect.height):
        ratio = y / rect.height
        color = tuple(int(color_top[i] + (color_bottom[i] - color_top[i]) * ratio) for i in range(3))
        pygame.draw.line(surface, color, (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

def draw_rounded_rect(surface, rect, color, radius=10, border_color=None, border_width=0):
    """Draw a rounded rectangle"""
    rect = pygame.Rect(rect)
    
    # Draw main rectangle
    pygame.draw.rect(surface, color, rect.inflate(-radius*2, 0))
    pygame.draw.rect(surface, color, rect.inflate(0, -radius*2))
    
    # Draw circles at corners
    pygame.draw.circle(surface, color, (rect.left + radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.top + radius), radius)
    pygame.draw.circle(surface, color, (rect.left + radius, rect.bottom - radius), radius)
    pygame.draw.circle(surface, color, (rect.right - radius, rect.bottom - radius), radius)
    
    # Draw border if specified
    if border_color and border_width > 0:
        # Top and bottom
        pygame.draw.line(surface, border_color, (rect.left + radius, rect.top), 
                        (rect.right - radius, rect.top), border_width)
        pygame.draw.line(surface, border_color, (rect.left + radius, rect.bottom), 
                        (rect.right - radius, rect.bottom), border_width)
        # Left and right
        pygame.draw.line(surface, border_color, (rect.left, rect.top + radius), 
                        (rect.left, rect.bottom - radius), border_width)
        pygame.draw.line(surface, border_color, (rect.right, rect.top + radius), 
                        (rect.right, rect.bottom - radius), border_width)
        # Corners
        pygame.draw.circle(surface, border_color, (rect.left + radius, rect.top + radius), 
                          radius, border_width)
        pygame.draw.circle(surface, border_color, (rect.right - radius, rect.top + radius), 
                          radius, border_width)
        pygame.draw.circle(surface, border_color, (rect.left + radius, rect.bottom - radius), 
                          radius, border_width)
        pygame.draw.circle(surface, border_color, (rect.right - radius, rect.bottom - radius), 
                          radius, border_width)

def draw_button(surface, rect, text, font, hover=False, icon=None):
    """Draw a modern button with hover effect"""
    color = COLORS['ui_hover'] if hover else COLORS['ui_accent']
    shadow_offset = 4
    
    # Shadow
    shadow_rect = rect.copy()
    shadow_rect.y += shadow_offset
    draw_rounded_rect(surface, shadow_rect, (0, 0, 0, 100), radius=8)
    
    # Button
    draw_rounded_rect(surface, rect, color, radius=8, border_color=COLORS['white'], border_width=2)
    
    # Icon if provided
    if icon:
        icon_surf = font.render(icon, True, COLORS['white'])
        icon_rect = icon_surf.get_rect(center=(rect.x + 30, rect.centery))
        surface.blit(icon_surf, icon_rect)
        text_x_offset = 20
    else:
        text_x_offset = 0
    
    # Text
    text_surf = font.render(text, True, COLORS['white'])
    text_rect = text_surf.get_rect(center=(rect.centerx + text_x_offset, rect.centery))
    surface.blit(text_surf, text_rect)

def draw_input_field(surface, rect, text, font, active=False, password=False):
    """Draw a modern input field"""
    border_color = COLORS['ui_accent'] if active else COLORS['ui_border']
    
    # Background
    draw_rounded_rect(surface, rect, COLORS['ui_panel'], radius=6)
    
    # Border with glow effect for active field
    if active:
        glow_rect = rect.inflate(6, 6)
        draw_rounded_rect(surface, glow_rect, (100, 150, 255, 50), radius=8)
    
    draw_rounded_rect(surface, rect, COLORS['ui_panel'], radius=6, 
                     border_color=border_color, border_width=2)
    
    # Text
    display_text = '*' * len(text) if password else text
    if not text and not active:
        display_text = ""
    
    text_surf = font.render(display_text, True, COLORS['ui_text'])
    text_rect = text_surf.get_rect(midleft=(rect.x + 15, rect.centery))
    surface.blit(text_surf, text_rect)
    
    # Cursor for active field
    if active and pygame.time.get_ticks() % 1000 < 500:
        cursor_x = text_rect.right + 2
        pygame.draw.line(surface, COLORS['ui_accent'], 
                        (cursor_x, rect.y + 10), (cursor_x, rect.bottom - 10), 2)

# ============================================================================
# UTILITY CLASSES
# ============================================================================

@dataclass
class Position:
    x: float
    y: float
    
    def to_grid(self) -> Tuple[int, int]:
        return int(self.y // TILE_SIZE), int(self.x // TILE_SIZE)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def distance_to(self, other: 'Position') -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], lifespan: int, size: int = 3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifespan = lifespan
        self.max_lifespan = lifespan
        self.size = size
    
    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.lifespan -= 1
        return self.lifespan > 0
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        if self.lifespan > 0:
            alpha = self.lifespan / self.max_lifespan
            color = tuple(int(c * alpha) for c in self.color)
            pygame.draw.circle(surface, color, 
                             (int(self.x + offset_x), int(self.y)), 
                             max(1, int(self.size * alpha)))

# ============================================================================
# GAME ENTITIES
# ============================================================================

class Entity:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.pos = Position(x, y)
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
    
    def update_rect(self):
        self.rect.x = self.pos.x - self.width // 2
        self.rect.y = self.pos.y - self.height // 2
    
    def get_state(self) -> dict:
        return {
            'x': self.pos.x,
            'y': self.pos.y
        }
    
    def set_state(self, state: dict):
        self.pos.x = state['x']
        self.pos.y = state['y']
        self.update_rect()

class Wall(Entity):
    def __init__(self, x: float, y: float, breakable: bool = False):
        super().__init__(x + TILE_SIZE // 2, y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)
        self.breakable = breakable
        self.health = WALL_HEALTH if breakable else -1
        self.max_health = WALL_HEALTH
    
    def take_damage(self, amount: int) -> bool:
        if self.breakable:
            self.health -= amount
            return self.health <= 0
        return False
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        color = COLORS['breakable_wall'] if self.breakable else COLORS['wall']
        
        if self.breakable and self.health < self.max_health:
            damage_ratio = 1 - (self.health / self.max_health)
            color = tuple(int(c * (1 - damage_ratio * 0.5)) for c in color)
        
        draw_rect = self.rect.copy()
        draw_rect.x += offset_x
        pygame.draw.rect(surface, color, draw_rect)
        pygame.draw.rect(surface, COLORS['black'], draw_rect, 2)

class Player(Entity):
    def __init__(self, x: float, y: float, player_id: int):
        size = TILE_SIZE - 8
        super().__init__(x, y, size, size)
        self.player_id = player_id
        self.color = COLORS['yellow'] if player_id == 1 else COLORS['green']
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.score = 0
        self.keys = 0
        self.speed = PLAYER_SPEED
        self.direction = Direction.NONE
        self.facing = Direction.RIGHT
        self.last_attack_time = 0
        self.mouth_open = True
        self.anim_timer = 0
    
    def move(self, dx: int, dy: int, walls: List[Wall]):
        if dx != 0 or dy != 0:
            self.direction = Direction((dx, dy))
            if dx != 0 or dy != 0:
                self.facing = Direction((dx, dy))
        
        new_x = self.pos.x + dx * self.speed
        new_y = self.pos.y + dy * self.speed
        
        test_rect = pygame.Rect(new_x - self.width // 2, new_y - self.height // 2,
                               self.width, self.height)
        
        collision = False
        for wall in walls:
            if test_rect.colliderect(wall.rect):
                collision = True
                break
        
        if not collision:
            self.pos.x = new_x
            self.pos.y = new_y
            self.update_rect()
    
    def attack(self, enemies: List['Enemy'], walls: List[Wall]) -> List[Particle]:
        particles = []
        now = pygame.time.get_ticks()
        
        if now - self.last_attack_time < PLAYER_ATTACK_COOLDOWN:
            return particles
        
        self.last_attack_time = now
        
        for enemy in enemies:
            if self.pos.distance_to(enemy.pos) < PLAYER_ATTACK_RANGE:
                enemy.take_damage(PLAYER_ATTACK_DAMAGE)
                for _ in range(5):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 5)
                    particles.append(Particle(
                        enemy.pos.x, enemy.pos.y,
                        math.cos(angle) * speed, math.sin(angle) * speed,
                        COLORS['red'], 30, 3
                    ))
        
        for wall in walls:
            if wall.breakable and self.pos.distance_to(wall.pos) < PLAYER_ATTACK_RANGE:
                if wall.take_damage(PLAYER_ATTACK_DAMAGE):
                    for _ in range(10):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 6)
                        particles.append(Particle(
                            wall.pos.x, wall.pos.y,
                            math.cos(angle) * speed, math.sin(angle) * speed,
                            COLORS['gray'], 40, 4
                        ))
        
        return particles
    
    def take_damage(self, amount: int):
        self.health -= amount
        if self.health < 0:
            self.health = 0
    
    def heal(self, amount: int):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        center = (int(self.pos.x + offset_x), int(self.pos.y))
        radius = self.width // 2
        
        if pygame.time.get_ticks() - self.anim_timer > 150:
            self.mouth_open = not self.mouth_open
            self.anim_timer = pygame.time.get_ticks()
        
        pygame.draw.circle(surface, self.color, center, radius)
        
        if self.mouth_open:
            mouth_angle = 30
            facing_angle = 0
            if self.facing == Direction.LEFT:
                facing_angle = 180
            elif self.facing == Direction.UP:
                facing_angle = -90
            elif self.facing == Direction.DOWN:
                facing_angle = 90
            
            points = [center]
            for angle in range(facing_angle - mouth_angle, 
                             facing_angle + mouth_angle + 5, 5):
                rad = math.radians(angle)
                px = center[0] + radius * math.cos(rad)
                py = center[1] + radius * math.sin(rad)
                points.append((px, py))
            pygame.draw.polygon(surface, COLORS['black'], points)
        
        eye_offset = radius * 0.3
        eye_angle = 0
        if self.facing == Direction.LEFT:
            eye_angle = 180
        elif self.facing == Direction.UP:
            eye_angle = -90
        elif self.facing == Direction.DOWN:
            eye_angle = 90
        
        rad = math.radians(eye_angle)
        eye_x = center[0] + eye_offset * math.cos(rad) - radius * 0.2 * math.sin(rad)
        eye_y = center[1] + eye_offset * math.sin(rad) + radius * 0.2 * math.cos(rad)
        pygame.draw.circle(surface, COLORS['black'], (int(eye_x), int(eye_y)), 
                          max(2, radius // 6))
    
    def get_state(self) -> dict:
        state = super().get_state()
        state.update({
            'health': self.health,
            'score': self.score,
            'keys': self.keys,
            'player_id': self.player_id,
            'facing': self.facing.value
        })
        return state
    
    def set_state(self, state: dict):
        super().set_state(state)
        self.health = state['health']
        self.score = state['score']
        self.keys = state['keys']
        self.facing = Direction(tuple(state['facing']))

class Enemy(Entity):
    def __init__(self, x: float, y: float):
        size = TILE_SIZE - 8
        super().__init__(x, y, size, size)
        self.health = ENEMY_HEALTH
        self.max_health = ENEMY_HEALTH
        self.speed = ENEMY_SPEED_PATROL
        self.state = 'patrol'
        self.patrol_target = Position(x, y)
        self.last_attack_time = 0
        self.next_patrol_time = pygame.time.get_ticks()
    
    def update(self, player: Player, walls: List[Wall]):
        dist = self.pos.distance_to(player.pos)
        
        if dist < ENEMY_DETECTION_RANGE:
            self.state = 'chase'
            self.speed = ENEMY_SPEED_CHASE
            target = player.pos
        else:
            self.state = 'patrol'
            self.speed = ENEMY_SPEED_PATROL
            
            now = pygame.time.get_ticks()
            if now > self.next_patrol_time or \
               self.pos.distance_to(self.patrol_target) < 10:
                self.patrol_target = Position(
                    self.pos.x + random.randint(-100, 100),
                    self.pos.y + random.randint(-100, 100)
                )
                self.next_patrol_time = now + random.randint(1000, 3000)
            target = self.patrol_target
        
        dx = target.x - self.pos.x
        dy = target.y - self.pos.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            dx = (dx / dist) * self.speed
            dy = (dy / dist) * self.speed
            
            new_x = self.pos.x + dx
            new_y = self.pos.y + dy
            
            test_rect = pygame.Rect(new_x - self.width // 2, new_y - self.height // 2,
                                   self.width, self.height)
            
            collision = False
            for wall in walls:
                if not wall.breakable and test_rect.colliderect(wall.rect):
                    collision = True
                    break
            
            if not collision:
                self.pos.x = new_x
                self.pos.y = new_y
                self.update_rect()
        
        if self.state == 'chase' and dist < ENEMY_ATTACK_RANGE:
            now = pygame.time.get_ticks()
            if now - self.last_attack_time > ENEMY_ATTACK_COOLDOWN:
                player.take_damage(ENEMY_DAMAGE)
                self.last_attack_time = now
    
    def take_damage(self, amount: int):
        self.health -= amount
        if self.health < 0:
            self.health = 0
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        draw_rect = self.rect.copy()
        draw_rect.x += offset_x
        
        color = COLORS['red'] if self.state == 'chase' else COLORS['orange']
        pygame.draw.rect(surface, color, draw_rect)
        pygame.draw.rect(surface, COLORS['black'], draw_rect, 2)
        
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            bar_x = draw_rect.x
            bar_y = draw_rect.y - 8
            
            pygame.draw.rect(surface, COLORS['health_bar_bg'],
                           (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(surface, COLORS['health_bar'],
                           (bar_x, bar_y, health_width, bar_height))
    
    def get_state(self) -> dict:
        state = super().get_state()
        state.update({
            'health': self.health,
            'state': self.state,
            'patrol_x': self.patrol_target.x,
            'patrol_y': self.patrol_target.y
        })
        return state
    
    def set_state(self, state: dict):
        super().set_state(state)
        self.health = state['health']
        self.state = state['state']
        self.patrol_target = Position(state['patrol_x'], state['patrol_y'])

class Collectible(Entity):
    def __init__(self, x: float, y: float, item_type: str):
        size = TILE_SIZE // 2
        super().__init__(x + TILE_SIZE // 2, y + TILE_SIZE // 2, size, size)
        self.item_type = item_type
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        center = (int(self.pos.x + offset_x), int(self.pos.y))
        
        if self.item_type == 'G':
            pygame.draw.circle(surface, COLORS['gold'], center, self.width // 2)
            pygame.draw.circle(surface, COLORS['black'], center, self.width // 2, 2)
        elif self.item_type == 'H':
            size = self.width
            rect = pygame.Rect(center[0] - size // 2, center[1] - size // 2, size, size)
            pygame.draw.rect(surface, COLORS['red'], rect)
            thickness = size // 4
            pygame.draw.rect(surface, COLORS['white'],
                           (center[0] - thickness // 2, rect.top, thickness, size))
            pygame.draw.rect(surface, COLORS['white'],
                           (rect.left, center[1] - thickness // 2, size, thickness))
        elif self.item_type == 'K':
            pygame.draw.circle(surface, COLORS['gold'], center, self.width // 3)
            pygame.draw.rect(surface, COLORS['gold'],
                           (center[0], center[1], self.width // 2, self.width // 3))
    
    def get_state(self) -> dict:
        state = super().get_state()
        state['type'] = self.item_type
        return state
    
    def set_state(self, state: dict):
        super().set_state(state)
        self.item_type = state['type']

# ============================================================================
# MAZE STATE
# ============================================================================

class MazeState:
    def __init__(self, player_id: int, level_map: List[str]):
        self.player_id = player_id
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.collectibles: List[Collectible] = []
        self.walls: List[Wall] = []
        self.exit_rect: Optional[pygame.Rect] = None
        self.particles: List[Particle] = []
        
        self.load_level(level_map)
    
    def load_level(self, level_map: List[str]):
        self.enemies.clear()
        self.collectibles.clear()
        self.walls.clear()
        self.particles.clear()
        
        for row_idx, row in enumerate(level_map):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                
                if tile == '#':
                    self.walls.append(Wall(x, y, False))
                elif tile == 'B':
                    self.walls.append(Wall(x, y, True))
                elif tile == 'P':
                    self.player = Player(x + TILE_SIZE // 2, y + TILE_SIZE // 2, 
                                        self.player_id)
                elif tile == 'E':
                    self.enemies.append(Enemy(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                elif tile in ['G', 'H', 'K']:
                    self.collectibles.append(Collectible(x, y, tile))
                elif tile == 'L':
                    self.exit_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
    
    def update(self):
        if not self.player:
            return
        
        for enemy in self.enemies[:]:
            enemy.update(self.player, self.walls)
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.player.score += 50
                for _ in range(15):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(3, 7)
                    self.particles.append(Particle(
                        enemy.pos.x, enemy.pos.y,
                        math.cos(angle) * speed, math.sin(angle) * speed,
                        COLORS['red'], 50, 4
                    ))
        
        for collectible in self.collectibles[:]:
            if self.player.rect.colliderect(collectible.rect):
                if collectible.item_type == 'G':
                    self.player.score += GOLD_VALUE
                elif collectible.item_type == 'H':
                    self.player.heal(HEALTH_POTION_HEAL)
                elif collectible.item_type == 'K':
                    self.player.keys += 1
                self.collectibles.remove(collectible)
                
                for _ in range(8):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 5)
                    color = COLORS['gold'] if collectible.item_type == 'G' else COLORS['green']
                    self.particles.append(Particle(
                        collectible.pos.x, collectible.pos.y,
                        math.cos(angle) * speed, math.sin(angle) * speed,
                        color, 30, 3
                    ))
        
        self.walls = [w for w in self.walls if not w.breakable or w.health > 0]
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface: pygame.Surface, offset_x: int = 0):
        maze_width = len(LEVELS[0][0]) * TILE_SIZE
        maze_height = len(LEVELS[0]) * TILE_SIZE
        pygame.draw.rect(surface, COLORS['floor'],
                        (offset_x, 0, maze_width, maze_height))
        
        for i in range(len(LEVELS[0][0]) + 1):
            x = i * TILE_SIZE + offset_x
            pygame.draw.line(surface, COLORS['dark_gray'], (x, 0), (x, maze_height))
        for i in range(len(LEVELS[0]) + 1):
            y = i * TILE_SIZE
            pygame.draw.line(surface, COLORS['dark_gray'], (offset_x, y), 
                           (offset_x + maze_width, y))
        
        if self.exit_rect:
            draw_rect = self.exit_rect.copy()
            draw_rect.x += offset_x
            pygame.draw.rect(surface, COLORS['cyan'], draw_rect)
            pygame.draw.rect(surface, COLORS['white'], draw_rect, 3)
        
        for wall in self.walls:
            wall.draw(surface, offset_x)
        
        for collectible in self.collectibles:
            collectible.draw(surface, offset_x)
        
        for enemy in self.enemies:
            enemy.draw(surface, offset_x)
        
        if self.player:
            self.player.draw(surface, offset_x)
        
        for particle in self.particles:
            particle.draw(surface, offset_x)
    
    def get_state(self) -> dict:
        return {
            'player': self.player.get_state() if self.player else None,
            'enemies': [e.get_state() for e in self.enemies],
            'collectibles': [c.get_state() for c in self.collectibles],
            'walls': [{'x': w.pos.x, 'y': w.pos.y, 'breakable': w.breakable, 
                      'health': w.health} for w in self.walls],
            'exit': (self.exit_rect.x, self.exit_rect.y) if self.exit_rect else None
        }
    
    def set_state(self, state: dict):
        if state['player'] and self.player:
            self.player.set_state(state['player'])
        
        while len(self.enemies) < len(state['enemies']):
            self.enemies.append(Enemy(0, 0))
        while len(self.enemies) > len(state['enemies']):
            self.enemies.pop()
        for enemy, e_state in zip(self.enemies, state['enemies']):
            enemy.set_state(e_state)
        
        while len(self.collectibles) < len(state['collectibles']):
            self.collectibles.append(Collectible(0, 0, 'G'))
        while len(self.collectibles) > len(state['collectibles']):
            self.collectibles.pop()
        for collectible, c_state in zip(self.collectibles, state['collectibles']):
            collectible.set_state(c_state)
        
        self.walls.clear()
        for w_state in state['walls']:
            wall = Wall(w_state['x'] - TILE_SIZE // 2, w_state['y'] - TILE_SIZE // 2,
                       w_state['breakable'])
            wall.health = w_state['health']
            self.walls.append(wall)

# ============================================================================
# GAME MANAGER
# ============================================================================

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Explorer Multiplayer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        
        self.state = GameState.MODE_SELECT
        self.is_server = False
        self.is_connected = False
        self.running = True
        
        self.maze1: Optional[MazeState] = None
        self.maze2: Optional[MazeState] = None
        self.current_level = 0
        
        self.socket: Optional[socket.socket] = None
        self.connection: Optional[socket.socket] = None
        
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.error_message = ""
        
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
    
    def start_server(self):
        self.is_server = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((HOST, PORT))
        self.socket.listen(1)
        print(f"[SERVER] Listening on port {PORT}")
        threading.Thread(target=self._server_listen, daemon=True).start()
    
    def _server_listen(self):
        try:
            self.connection, addr = self.socket.accept()
            print(f"[SERVER] Client connected from {addr}")
            self.is_connected = True
            threading.Thread(target=self._server_communicate, daemon=True).start()
        except Exception as e:
            print(f"[SERVER] Error: {e}")
    
    def _server_communicate(self):
        while self.running and self.is_connected:
            try:
                if self.maze1 and self.maze2:
                    game_state = {
                        'maze1': self.maze1.get_state(),
                        'maze2': self.maze2.get_state(),
                        'level': self.current_level,
                        'state': self.state.value
                    }
                    data = pickle.dumps(game_state)
                    self.connection.sendall(len(data).to_bytes(4, 'big'))
                    self.connection.sendall(data)
                
                size_data = self.connection.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, 'big')
                data = b''
                while len(data) < size:
                    packet = self.connection.recv(min(size - len(data), BUFFER_SIZE))
                    if not packet:
                        break
                    data += packet
                
                if data:
                    client_input = pickle.loads(data)
                    self._process_client_input(client_input)
                
                pygame.time.wait(16)
            except Exception as e:
                print(f"[SERVER] Communication error: {e}")
                self.is_connected = False
                break
    
    def connect_to_server(self, host: str):
        self.is_server = False
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, PORT))
            print(f"[CLIENT] Connected to {host}:{PORT}")
            self.is_connected = True
            threading.Thread(target=self._client_communicate, daemon=True).start()
        except Exception as e:
            print(f"[CLIENT] Connection error: {e}")
            self.error_message = f"Connection failed: {e}"
    
    def _client_communicate(self):
        while self.running and self.is_connected:
            try:
                size_data = self.socket.recv(4)
                if not size_data:
                    break
                size = int.from_bytes(size_data, 'big')
                data = b''
                while len(data) < size:
                    packet = self.socket.recv(min(size - len(data), BUFFER_SIZE))
                    if not packet:
                        break
                    data += packet
                
                if data:
                    game_state = pickle.loads(data)
                    self._process_server_state(game_state)
                
                if self.maze2 and self.maze2.player:
                    client_input = {
                        'keys': list(self.keys_pressed),
                        'attack': pygame.K_SPACE in self.keys_pressed
                    }
                    data = pickle.dumps(client_input)
                    self.socket.sendall(len(data).to_bytes(4, 'big'))
                    self.socket.sendall(data)
                
                pygame.time.wait(16)
            except Exception as e:
                print(f"[CLIENT] Communication error: {e}")
                self.is_connected = False
                break
    
    def _process_client_input(self, input_data: dict):
        if not self.maze2 or not self.maze2.player:
            return
        
        keys = set(input_data.get('keys', []))
        dx, dy = 0, 0
        
        if pygame.K_UP in keys:
            dy -= 1
        if pygame.K_DOWN in keys:
            dy += 1
        if pygame.K_LEFT in keys:
            dx -= 1
        if pygame.K_RIGHT in keys:
            dx += 1
        
        self.maze2.player.move(dx, dy, self.maze2.walls)
        
        if input_data.get('attack'):
            particles = self.maze2.player.attack(self.maze2.enemies, self.maze2.walls)
            self.maze2.particles.extend(particles)
    
    def _process_server_state(self, state: dict):
        self.current_level = state.get('level', 0)
        self.state = GameState(state.get('state', GameState.PLAYING.value))
        
        if state.get('maze1'):
            if not self.maze1:
                self.maze1 = MazeState(1, LEVELS[self.current_level])
            self.maze1.set_state(state['maze1'])
        
        if state.get('maze2'):
            if not self.maze2:
                self.maze2 = MazeState(2, LEVELS[self.current_level])
            self.maze2.set_state(state['maze2'])
    
    def start_game(self):
        self.state = GameState.PLAYING
        self.current_level = 0
        self.maze1 = MazeState(1, LEVELS[0])
        self.maze2 = MazeState(2, LEVELS[0])
    
    def advance_level(self):
        self.current_level += 1
        if self.current_level >= len(LEVELS):
            self.state = GameState.GAME_OVER
            return
        
        p1_health = self.maze1.player.health if self.maze1 and self.maze1.player else PLAYER_HEALTH
        p1_score = self.maze1.player.score if self.maze1 and self.maze1.player else 0
        p1_keys = self.maze1.player.keys if self.maze1 and self.maze1.player else 0
        
        p2_health = self.maze2.player.health if self.maze2 and self.maze2.player else PLAYER_HEALTH
        p2_score = self.maze2.player.score if self.maze2 and self.maze2.player else 0
        p2_keys = self.maze2.player.keys if self.maze2 and self.maze2.player else 0
        
        self.maze1 = MazeState(1, LEVELS[self.current_level])
        self.maze2 = MazeState(2, LEVELS[self.current_level])
        
        if self.maze1.player:
            self.maze1.player.health = p1_health
            self.maze1.player.score = p1_score
            self.maze1.player.keys = p1_keys
        
        if self.maze2.player:
            self.maze2.player.health = p2_health
            self.maze2.player.score = p2_score
            self.maze2.player.keys = p2_keys
        
        self.state = GameState.LEVEL_COMPLETE
        pygame.time.set_timer(pygame.USEREVENT, 2000, 1)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.USEREVENT:
                if self.state == GameState.LEVEL_COMPLETE:
                    self.state = GameState.PLAYING
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                if self.state == GameState.MODE_SELECT:
                    if event.key == pygame.K_1:
                        self.start_server()
                        self.state = GameState.LOGIN
                    elif event.key == pygame.K_2:
                        self.state = GameState.LOGIN
                
                elif self.state == GameState.LOGIN:
                    self._handle_login_input(event)
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MODE_SELECT
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.MODE_SELECT:
                    self._handle_mode_select_click(event.pos)
                elif self.state == GameState.LOGIN:
                    self._handle_login_click(event.pos)
    
    def _handle_login_input(self, event):
        if self.active_field == "username":
            if event.key == pygame.K_RETURN:
                self.active_field = "password"
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_TAB:
                self.active_field = "password"
            elif event.unicode.isprintable():
                self.username += event.unicode
        
        elif self.active_field == "password":
            if event.key == pygame.K_RETURN:
                self._attempt_login()
            elif event.key == pygame.K_BACKSPACE:
                self.password = self.password[:-1]
            elif event.key == pygame.K_TAB:
                self.active_field = "username"
            elif event.unicode.isprintable():
                self.password += event.unicode
    
    def _handle_mode_select_click(self, pos):
        server_rect = pygame.Rect(450, 350, 250, 80)
        client_rect = pygame.Rect(900, 350, 250, 80)
        
        if server_rect.collidepoint(pos):
            self.start_server()
            self.state = GameState.LOGIN
        elif client_rect.collidepoint(pos):
            self.state = GameState.LOGIN
    
    def _handle_login_click(self, pos):
        username_rect = pygame.Rect(550, 320, 500, 50)
        password_rect = pygame.Rect(550, 420, 500, 50)
        login_rect = pygame.Rect(650, 530, 300, 60)
        
        if username_rect.collidepoint(pos):
            self.active_field = "username"
        elif password_rect.collidepoint(pos):
            self.active_field = "password"
        elif login_rect.collidepoint(pos):
            self._attempt_login()
    
    def _attempt_login(self):
        if self.username == "user" and self.password == "pass":
            self.error_message = ""
            if self.is_server:
                self.start_game()
            else:
                self.connect_to_server("127.0.0.1")
                if self.is_connected:
                    self.state = GameState.PLAYING
        else:
            self.error_message = "Invalid credentials"
    
    def update(self):
        if self.state == GameState.PLAYING and self.is_server:
            if self.maze1:
                dx, dy = 0, 0
                if pygame.K_UP in self.keys_pressed:
                    dy -= 1
                if pygame.K_DOWN in self.keys_pressed:
                    dy += 1
                if pygame.K_LEFT in self.keys_pressed:
                    dx -= 1
                if pygame.K_RIGHT in self.keys_pressed:
                    dx += 1
                
                if self.maze1.player:
                    self.maze1.player.move(dx, dy, self.maze1.walls)
                    
                    if pygame.K_SPACE in self.keys_pressed:
                        particles = self.maze1.player.attack(self.maze1.enemies, 
                                                            self.maze1.walls)
                        self.maze1.particles.extend(particles)
                
                self.maze1.update()
                
                if self.maze1.player and self.maze1.exit_rect:
                    if self.maze1.player.rect.colliderect(self.maze1.exit_rect):
                        self.advance_level()
                
                if self.maze1.player and self.maze1.player.health <= 0:
                    self.state = GameState.GAME_OVER
            
            if self.maze2:
                self.maze2.update()
                
                if self.maze2.player and self.maze2.exit_rect:
                    if self.maze2.player.rect.colliderect(self.maze2.exit_rect):
                        self.advance_level()
                
                if self.maze2.player and self.maze2.player.health <= 0:
                    self.state = GameState.GAME_OVER
        
        elif self.state == GameState.PLAYING and not self.is_server:
            if self.maze2 and self.maze2.player:
                dx, dy = 0, 0
                if pygame.K_UP in self.keys_pressed:
                    dy -= 1
                if pygame.K_DOWN in self.keys_pressed:
                    dy += 1
                if pygame.K_LEFT in self.keys_pressed:
                    dx -= 1
                if pygame.K_RIGHT in self.keys_pressed:
                    dx += 1
                
                self.maze2.player.move(dx, dy, self.maze2.walls)
    
    def draw(self):
        self.screen.fill(COLORS['ui_bg'])
        
        if self.state == GameState.MODE_SELECT:
            self._draw_mode_select()
        elif self.state == GameState.LOGIN:
            self._draw_login()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_mode_select(self):
        # Gradient background
        draw_gradient_rect(self.screen, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                          COLORS['gradient_top'], COLORS['gradient_bottom'])
        
        # Animated title
        pulse = math.sin(pygame.time.get_ticks() / 500) * 0.1 + 1
        title = self.title_font.render("DUNGEON EXPLORER", True, COLORS['gold'])
        title_scaled = pygame.transform.scale(title, 
                                             (int(title.get_width() * pulse), 
                                              int(title.get_height() * pulse)))
        title_rect = title_scaled.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_scaled, title_rect)
        
        # Subtitle with glow effect
        subtitle = self.subtitle_font.render("MULTIPLAYER ADVENTURE", True, COLORS['ui_accent'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 230))
        
        # Glow
        for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
            glow_surf = self.subtitle_font.render("MULTIPLAYER ADVENTURE", True, (50, 100, 150, 100))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2 + offset[0], 230 + offset[1]))
            self.screen.blit(glow_surf, glow_rect)
        
        self.screen.blit(subtitle, subtitle_rect)
        
        # Server button
        server_rect = pygame.Rect(450, 350, 250, 80)
        server_hover = server_rect.collidepoint(self.mouse_pos)
        draw_button(self.screen, server_rect, "HOST SERVER", self.font, server_hover, "🖥")
        
        hint = self.font.render("Press 1 or Click", True, COLORS['ui_text_dim'])
        hint_rect = hint.get_rect(center=(575, 450))
        self.screen.blit(hint, hint_rect)
        
        # Client button
        client_rect = pygame.Rect(900, 350, 250, 80)
        client_hover = client_rect.collidepoint(self.mouse_pos)
        draw_button(self.screen, client_rect, "JOIN GAME", self.font, client_hover, "🎮")
        
        hint = self.font.render("Press 2 or Click", True, COLORS['ui_text_dim'])
        hint_rect = hint.get_rect(center=(1025, 450))
        self.screen.blit(hint, hint_rect)
        
        # Instructions panel
        panel_rect = pygame.Rect(350, 540, 900, 280)
        draw_rounded_rect(self.screen, panel_rect, COLORS['ui_panel'], radius=15,
                         border_color=COLORS['ui_border'], border_width=2)
        
        instructions_title = self.subtitle_font.render("HOW TO PLAY", True, COLORS['gold'])
        title_rect = instructions_title.get_rect(center=(SCREEN_WIDTH // 2, 580))
        self.screen.blit(instructions_title, title_rect)
        
        instructions = [
            "⌨  Use Arrow Keys to move your character",
            "⚔  Press Space to attack enemies and breakable walls",
            "💰 Collect gold coins to increase your score",
            "❤  Pick up health potions to restore HP",
            "🔑 Find keys to unlock special areas",
            "🚪 Reach the cyan exit to advance to the next level"
        ]
        
        y_offset = 630
        for instruction in instructions:
            text = self.font.render(instruction, True, COLORS['ui_text'])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 32
    
    def _draw_login(self):
        # Gradient background
        draw_gradient_rect(self.screen, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                          COLORS['gradient_top'], COLORS['gradient_bottom'])
        
        # Main login panel
        panel_rect = pygame.Rect(400, 150, 800, 600)
        draw_rounded_rect(self.screen, panel_rect, COLORS['ui_panel'], radius=20,
                         border_color=COLORS['ui_border'], border_width=3)
        
        # Title
        title = self.title_font.render("LOGIN", True, COLORS['gold'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(title, title_rect)
        
        # Username field
        label = self.subtitle_font.render("Username", True, COLORS['ui_text'])
        self.screen.blit(label, (550, 280))
        
        username_rect = pygame.Rect(550, 320, 500, 50)
        draw_input_field(self.screen, username_rect, self.username, 
                        self.font, self.active_field == "username")
        
        # Password field
        label = self.subtitle_font.render("Password", True, COLORS['ui_text'])
        self.screen.blit(label, (550, 380))
        
        password_rect = pygame.Rect(550, 420, 500, 50)
        draw_input_field(self.screen, password_rect, self.password, 
                        self.font, self.active_field == "password", password=True)
        
        # Login button
        login_rect = pygame.Rect(650, 530, 300, 60)
        login_hover = login_rect.collidepoint(self.mouse_pos)
        draw_button(self.screen, login_rect, "LOGIN", self.subtitle_font, login_hover)
        
        # Error message
        if self.error_message:
            error_panel = pygame.Rect(500, 620, 600, 50)
            draw_rounded_rect(self.screen, error_panel, (100, 30, 30), radius=8,
                            border_color=COLORS['red'], border_width=2)
            error = self.font.render(self.error_message, True, COLORS['red'])
            error_rect = error.get_rect(center=(SCREEN_WIDTH // 2, 645))
            self.screen.blit(error, error_rect)
        
        # Hint
        hint = self.font.render("Default credentials: user / pass", True, COLORS['ui_text_dim'])
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 690))
        self.screen.blit(hint, hint_rect)
        
        # Connection status
        if self.is_server:
            status_color = COLORS['orange'] if not self.is_connected else COLORS['green']
            status_text = "⏳ Waiting for client..." if not self.is_connected else "✓ Client connected!"
            status_panel = pygame.Rect(450, 720, 700, 40)
            draw_rounded_rect(self.screen, status_panel, COLORS['ui_panel'], radius=8,
                            border_color=status_color, border_width=2)
            text = self.font.render(status_text, True, status_color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 740))
            self.screen.blit(text, text_rect)
    
    def _draw_game(self):
        self.screen.fill(COLORS['ui_bg'])
        
        maze_width = len(LEVELS[0][0]) * TILE_SIZE
        maze_height = len(LEVELS[0]) * TILE_SIZE
        
        if self.maze1:
            self.maze1.draw(self.screen, 50)
            self._draw_info_bar(self.maze1, 50, maze_height + 20, "PLAYER 1", COLORS['yellow'])
        
        if self.maze2:
            offset_x = 50 + maze_width + MAZE_GAP
            self.maze2.draw(self.screen, offset_x)
            self._draw_info_bar(self.maze2, offset_x, maze_height + 20, "PLAYER 2", COLORS['green'])
        
        # Level indicator with style
        level_panel = pygame.Rect(SCREEN_WIDTH // 2 - 150, 10, 300, 60)
        draw_rounded_rect(self.screen, level_panel, COLORS['ui_panel'], radius=10,
                         border_color=COLORS['gold'], border_width=3)
        
        level_text = self.subtitle_font.render(f"LEVEL {self.current_level + 1}", 
                                              True, COLORS['gold'])
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(level_text, level_rect)
    
    def _draw_info_bar(self, maze: MazeState, x: int, y: int, label: str, color: tuple):
        if not maze.player:
            return
        
        bar_width = len(LEVELS[0][0]) * TILE_SIZE
        bar_rect = pygame.Rect(x, y, bar_width, 80)
        
        draw_rounded_rect(self.screen, bar_rect, COLORS['ui_panel'], radius=10,
                         border_color=COLORS['ui_border'], border_width=2)
        
        # Player label
        label_text = self.subtitle_font.render(label, True, color)
        self.screen.blit(label_text, (x + 15, y + 10))
        
        # Health bar with gradient
        health_label = self.font.render("HP:", True, COLORS['ui_text'])
        self.screen.blit(health_label, (x + 15, y + 45))
        
        bar_x = x + 60
        bar_y = y + 45
        bar_w = 200
        bar_h = 25
        
        # Health bar background
        health_bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        draw_rounded_rect(self.screen, health_bg_rect, COLORS['health_bar_bg'], radius=5)
        
        # Health bar fill with gradient
        health_ratio = maze.player.health / maze.player.max_health
        health_width = int(bar_w * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_h)
            health_color = COLORS['health_bar'] if health_ratio > 0.3 else (150, 0, 0)
            draw_rounded_rect(self.screen, health_rect, health_color, radius=5)
        
        # Health bar border
        pygame.draw.rect(self.screen, COLORS['ui_border'], 
                        pygame.Rect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 2, border_radius=5)
        
        # Health text
        health_text = self.font.render(f"{maze.player.health}/{maze.player.max_health}", 
                                       True, COLORS['white'])
        health_text_rect = health_text.get_rect(center=(bar_x + bar_w // 2, bar_y + bar_h // 2))
        self.screen.blit(health_text, health_text_rect)
        
        # Score with icon
        score_text = self.font.render(f"💰 {maze.player.score}", True, COLORS['gold'])
        self.screen.blit(score_text, (x + 280, y + 45))
        
        # Keys with icon
        keys_text = self.font.render(f"🔑 {maze.player.keys}", True, COLORS['gold'])
        self.screen.blit(keys_text, (x + 420, y + 45))
    
    def _draw_level_complete(self):
        self._draw_game()
        
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS['black'])
        self.screen.blit(overlay, (0, 0))
        
        # Completion panel
        panel_rect = pygame.Rect(400, 300, 800, 300)
        draw_rounded_rect(self.screen, panel_rect, COLORS['ui_panel'], radius=20,
                         border_color=COLORS['gold'], border_width=4)
        
        # Animated checkmark
        pulse = math.sin(pygame.time.get_ticks() / 200) * 0.15 + 1
        checkmark = self.title_font.render("✓", True, COLORS['green'])
        checkmark_scaled = pygame.transform.scale(checkmark,
                                                 (int(checkmark.get_width() * pulse),
                                                  int(checkmark.get_height() * pulse)))
        check_rect = checkmark_scaled.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(checkmark_scaled, check_rect)
        
        # Text
        text = self.title_font.render("LEVEL COMPLETE!", True, COLORS['gold'])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 480))
        self.screen.blit(text, text_rect)
        
        next_text = self.subtitle_font.render(f"Advancing to Level {self.current_level + 1}...",
                                             True, COLORS['ui_text'])
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(next_text, next_rect)
    
    def _draw_game_over(self):
        # Gradient background
        draw_gradient_rect(self.screen, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
                          COLORS['gradient_top'], COLORS['gradient_bottom'])
        
        # Determine winner
        p1_score = self.maze1.player.score if self.maze1 and self.maze1.player else 0
        p2_score = self.maze2.player.score if self.maze2 and self.maze2.player else 0
        
        if p1_score > p2_score:
            winner = "PLAYER 1 WINS!"
            winner_color = COLORS['yellow']
            trophy = "🏆"
        elif p2_score > p1_score:
            winner = "PLAYER 2 WINS!"
            winner_color = COLORS['green']
            trophy = "🏆"
        else:
            winner = "TIE GAME!"
            winner_color = COLORS['gold']
            trophy = "🤝"
        
        # Main panel
        panel_rect = pygame.Rect(300, 150, 1000, 600)
        draw_rounded_rect(self.screen, panel_rect, COLORS['ui_panel'], radius=20,
                         border_color=COLORS['ui_border'], border_width=3)
        
        # Game Over title
        title = self.title_font.render("GAME OVER", True, COLORS['red'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(title, title_rect)
        
        # Trophy/Icon with animation
        pulse = math.sin(pygame.time.get_ticks() / 300) * 0.2 + 1.2
        trophy_text = self.title_font.render(trophy, True, winner_color)
        trophy_scaled = pygame.transform.scale(trophy_text,
                                              (int(trophy_text.get_width() * pulse),
                                               int(trophy_text.get_height() * pulse)))
        trophy_rect = trophy_scaled.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(trophy_scaled, trophy_rect)
        
        # Winner text
        winner_text = self.title_font.render(winner, True, winner_color)
        winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, 420))
        self.screen.blit(winner_text, winner_rect)
        
        # Score panel
        score_panel_rect = pygame.Rect(450, 500, 700, 150)
        draw_rounded_rect(self.screen, score_panel_rect, COLORS['ui_bg'], radius=15,
                         border_color=COLORS['ui_border'], border_width=2)
        
        # Player scores
        p1_text = self.subtitle_font.render(f"Player 1: {p1_score} points", True, COLORS['yellow'])
        p1_rect = p1_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(p1_text, p1_rect)
        
        p2_text = self.subtitle_font.render(f"Player 2: {p2_score} points", True, COLORS['green'])
        p2_rect = p2_text.get_rect(center=(SCREEN_WIDTH // 2, 600))
        self.screen.blit(p2_text, p2_rect)
        
        # Exit instruction
        exit_panel = pygame.Rect(550, 680, 500, 50)
        draw_rounded_rect(self.screen, exit_panel, COLORS['ui_panel'], radius=10,
                         border_color=COLORS['ui_border'], border_width=2)
        exit_text = self.font.render("Press ESC to return to menu", True, COLORS['ui_text_dim'])
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, 705))
        self.screen.blit(exit_text, exit_rect)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        if self.socket:
            self.socket.close()
        if self.connection:
            self.connection.close()
        pygame.quit()
        sys.exit()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()