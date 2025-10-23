import sys
sys.path.append("E:/venv/Lib/site-packages")

import pygame
import math
import random
import time
import socket
import threading
import pickle
import sys

# --- Networking Constants ---
HOST = '' # Listen on all available interfaces for the server
PORT = 5000 # Port for the game connection
RECV_BUFFER_SIZE = 4096 * 2 # Increased buffer size for larger game state data (two mazes)

# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init()

# Get screen info after Pygame init but before setting the mode
infoObject = pygame.display.Info()
DEFAULT_SCREEN_WIDTH = 800
DEFAULT_SCREEN_HEIGHT = 600

actual_display_width = max(DEFAULT_SCREEN_WIDTH, infoObject.current_w) if infoObject.current_w else DEFAULT_SCREEN_WIDTH
actual_display_height = max(DEFAULT_SCREEN_HEIGHT, infoObject.current_h) if infoObject.current_h else DEFAULT_SCREEN_HEIGHT

# --- Game Constants (initial definitions, TILE_SIZE will be calculated) ---
INFO_BAR_HEIGHT = 80
FPS = 60
FONT_SIZE = 24
MAZE_GAP = 10 # Pixels of space between the two mazes

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)       # Player 2 color
RED = (200, 0, 0)         # Enemy color
GOLD = (255, 215, 0)      # Gold color
BLUE = (30, 30, 100)      # Wall color (Indestructible walls - darker blue)
FLOOR_COLOR = (30, 30, 30) # Floor color
HEALTH_COLOR = (255, 0, 0) # Health bar color
EXIT_COLOR = (0, 255, 255) # Cyan for the level exit
PAC_MAN_YELLOW = (255, 255, 0) # Specific yellow for Pac-Man (Player 1)
TEXT_INPUT_BOX_COLOR = (50, 50, 50)
TEXT_INPUT_BORDER_COLOR = (150, 150, 150)
ERROR_MESSAGE_COLOR = (255, 50, 50)
BREAKABLE_WALL_INITIAL_COLOR = (100, 100, 100) # Lighter gray for breakable walls
BREAKABLE_WALL_COLOR_DAMAGED = (50, 50, 50) # Darker gray when damaged
ELECTRICITY_COLOR = (100, 255, 255) # Cyan/light blue for electricity
DEBRIS_COLOR = (80, 70, 60) # Dark brown/gray for debris

# Castle Deformation Constant
castle_deformation_duration_ms = 8000 # Moved here to be globally accessible

# Game states
GAME_STATE_MODE_SELECT = -3 # New: Choose server/client
GAME_STATE_LOGIN = -2
GAME_STATE_INTRO = -1
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAME_OVER = 2
GAME_STATE_LEVEL_COMPLETE = 3

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
NO_DIRECTION = (0, 0)

# --- Map Layouts (remain unchanged) ---
LEVEL_1_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BP.B.........E.B...#",
    "B.B########.####.K.B",
    "#.#.B.....#.#..#...#",
    "#B#.#####.#.####.#B#",
    "#.#.#G#B..#G...#.#.#",
    "#.#.###.###.####.#.#",
    "#.#.B.#.B.#.#..#.#B#",
    "B.#.B.#.#B#.#..#.#.#",
    "#.#.#####.B.####.#.#",
    "#B#.....E.#....Y.#B#",
    "#H####B######.#..#.#",
    "#..B..........#..B.#",
    "#####B###.#########X",
    "#....L....#....L...#",
    "#G#########.####.H.#",
    "#...........E....Z.#", # Added Z for electricity spawn
    "####################"
]

LEVEL_2_MAP = [
    "XXXXXXXXXXXXXXXXXXXX",
    "XW.B.B.B.B.B.B.B.W.X",
    "XW.#############.W.X",
    "XW.#.B.........#.W.X",
    "XW.#.B#########.#.W.",
    "XW.#.#.B.....B.#.W.X",
    "XW.#.#.B#####.#.W.X.",
    "XW.#.#.#P...#.#.H.W.",
    "XW.E.B.#..G..#B#B.W.",
    "XW.#.#.#####.#.W.X.B",
    "XW.#.#.B.....B.#.W.X",
    "XW.#########.B.W.X",
    "XW.B...........#.W.X",
    "XW.#############.W.X",
    "XW.B...........L.B.X",
    "XWWWWWWWWWWWWWWWWWWX",
    "XW...B.........Z.W.X", # Added Z for electricity spawn
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_3_MAP = [
    "####################",
    "#P...........E....Z#", # Added Z for electricity spawn
    "#.BBBBBBBB.BBBBB##BB",
    "#.#G...#B.#.G....#.#",
    "#.#.E..#.#.BBBBBB.#.",
    "#.#.####.#.#.....#.#",
    "#.#.B.###.#.#.B.###.#",
    "#.#.####.#.#.E..#.#B",
    "#.#....#.#.#####.#.#",
    "#.######.B#....#.#.B",
    "#........#.#.###.#.#",
    "#.########.#.#...#.#",
    "#.H........#.#.###.#",
    "#####B###########B.#",
    "#....L....#....L...Y.#",
    "#G#########.####.K.#",
    "#...........E......#",
    "####################"
]

LEVEL_4_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BPE........B.E.....B",
    "B.B.B.B.B.B.B.B.B.B.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.L..........L....N.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.E.E.G.E.H.E.K.E.EZ", # Added Z for electricity spawn
    "BBBBBBBBBBBBBBBBBBBB"
]

LEVEL_5_MAP = [
    "X##################X",
    "X#P..............E#X",
    "X#.###############.#",
    "X#.##B#....G....#B##",
    "X#.#E#.#.#######.#E.",
    "X#.#.#.#.##H##.#.#.#",
    "X#.#.#.#.#####.#.#.#",
    "X#.#.#.#..E....#.#.#",
    "X#.#.#.########.#.#X",
    "X#.#.B....#K#...B.#X",
    "X#.#######.###.#####",
    "X#.......E.#.E....#X",
    "X#.B############.B.#",
    "X#.#.L.........L.#.#",
    "X#.#.###########.#.#",
    "X#...............EZ#", # Added Z for electricity spawn
    "X##################X",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_6_MAP = [
    "####################",
    "#P...............L.#",
    "#.#####.############",
    "#.E...#.#..........#",
    "#####.#.#.B.#######B",
    "#G....#.#.G...#....#",
    "#.#####.#####.#.####",
    "#.E...#.......#.#..#",
    "#.#####.#######.#.##",
    "#.......E.....#.#..#",
    "#######.#####.#.#.##",
    "#H....#K....#.#..#",
    "#.#######.#####.#.##",
    "#.E.....#.......#..#",
    "#.#####.############",
    "#.............E....#",
    "##################Z#", # Added Z for electricity spawn
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_7_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BBP.G.B.E.G.B.H.B.K.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.L.L.L.L.L.L.L.L.L.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "BBBBBBBBBBBBBBBBBBBB"
]

LEVEL_8_MAP = [
    "####################",
    "#P................E#",
    "#.################.#",
    "#.##B##..G..##B##.#B",
    "#.##E##.H.K.##E##.#B",
    "#.#############.##.#",
    "#.##.........##.##.#",
    "#.##.E.....E.##.##.#",
    "#.##.#######.##.##.#",
    "#.##.#######.##.##.#",
    "#.##.E.....E.##.##.#",
    "#.##.........##.##.#",
    "#.#############.##.#",
    "#.##B##.H.K.##B##.#B",
    "#.##E##..G..##E##.#B",
    "#.################.#",
    "#L...............Z.#", # Added Z for electricity spawn
    "####################"
]

LEVEL_9_MAP = [
    "####################",
    "#P.#.#.#.#.#.#.#.#.#",
    "#.B.#.#.#.#.#.#.#.B#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B.#.#.#.#.#.B.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.B.#.#.#.#.#.#.#.B.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B.#.#.#.#.#.B.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.B.#.#.#.#.#.#.#.B.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B.#.#.#.#.#.B.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "#.H.G.K.G.H.G.K.G.H.",
    "##########L#########"
]

LEVEL_10_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "B.P..............G.B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.#.#.#.#.#.#.#.#.#B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.#.#.#.#.#.#.#.#.#B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.#.#.#.#.#.#.#.#.#B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.#.#.#.#.#.#.#.#.#B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.#.#.#.#.#.#.#.#.#B",
    "B.B.#.#.#.#.#.#.#B.B",
    "B.E.#.#.#.#.#.#.#.#B",
    "B.L..............EZB", # Added Z for electricity spawn
    "B.B.B.B.B.B.B.B.B.B.",
    "B.K.H.G.H.K.G.H.K.G.",
    "BBBBBBBBBBBBBBBBBBBB"
]

LEVEL_11_MAP = [
    "####################",
    "#P#.#.#.#.#.#.#.#E.#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.B.B.B.B.B.B.B.B.BZ", # Added Z for electricity spawn
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#E.#.#.#.#.#.#.#.#L.",
    "####################"
]

LEVEL_12_MAP = [
    "XBBBBBBBBBBBBBBBBBBX",
    "XP................LX",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X..................X",
    "X.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "XBBBBBBBBBBBBBBBBBBX"
]

LEVEL_13_MAP = [
    "####################",
    "#P...#.#.#.#.#.E...#",
    "#.#.B#.#.#.#.#.#.#.#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B#.#.#.#.#.#.#.#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B#.#.#.#.#.#.#.#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B#.#.#.#.#.#.#.#",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.B#.#.#.#.#.#.#.#",
    "#E...#.#.#.#.#.L..Z#", # Added Z for electricity spawn
    "#B#############B####",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_14_MAP = [
    "XBBBBBBBBBBBBBBBBBBX",
    "XP.#.#.#.#.#.#.#.#BX",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.B.B.B.B.B.B.B.B.BX",
    "X.#.#.#.#.#.#.#.#.#X",
    "X.L.#.#.#.#.#.#.#.ZX", # Added Z for electricity spawn
    "X.E.E.E.E.E.E.E.E.EX",
    "XGHGKGHGKGHGKGHGKGHX",
    "XBBBBBBBBBBBBBBBBBBX"
]

LEVEL_15_MAP = [
    "####################",
    "#P...#G....Y.#H....#",
    "#.#B.#.#####.#.#.#.#",
    "#.#.#.#.#E.#.#.#.#.#",
    "#.#.#.#.##.#.#.#.#.#",
    "#.#.#.#....#.#.#.#.#",
    "#.#.#####.##.#.#.#.#",
    "#.#.E....#G.#.#.#.#.",
    "#.#.#######.B#.#.#.#",
    "#.#..........E.#.#.#",
    "#.#B###########.H#.#",
    "#.#............#.#.#",
    "#.#.############.#.#",
    "#.#.E..........#.#.#",
    "#.#.############.B.#",
    "#L...............Z.#", # Added Z for electricity spawn
    "####################",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_16_MAP = [
    "XXXXXXXXXXXXXXXXXXXX",
    "X#P.E.G.E.H.E.K.E.E#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#.#.#.#.#.#.#.#.#.#",
    "X#E.E.G.E.H.E.K.E.LZ", # Added Z for electricity spawn
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_17_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "B.P.H.G.H.G.H.G.H.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.L.H.G.H.G.H.G.H.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "BBBBBBBBBBBBBBBBBBBB"
]

LEVEL_18_MAP = [
    "####################",
    "#PH..............BL#",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#.##E##.##E##.#.#B",
    "#.##G##.##H##.#.#B",
    "#.##K##.##G##.#.#B",
    "#.##H##.##E##.#.#B",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#.############.#.#",
    "#E...............EZ#", # Added Z for electricity spawn
    "####################"
]

LEVEL_19_MAP = [
    "X##################X",
    "X#P..............L#X",
    "X#.#############.E.#",
    "X#.##B#....G....#B##",
    "X#.#E#.#.#######.#E.",
    "X#.#.#.#.##H##.#.#.#",
    "X#.#.#.#.#####.#.#.#",
    "X#.#.#.#..E....#.#.#",
    "X#.#.#.########.#.#X",
    "X#.#.B....#K#...B.#X",
    "X#.#######.###.#####",
    "X#.......E.#.E....#X",
    "X#.B############.B.#",
    "X#.#.L.........L.#.#",
    "X#.#.###########.#.#",
    "X#...............EZ#", # Added Z for electricity spawn
    "X##################X",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_20_MAP = [
    "####################",
    "#P.B.Z.#.B.H.H.G..LB",
    "#.ZB#.GGG..BHHZB#.#B",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.E.G.H.K.E.G.H.K.EZ", # Added Z for electricity spawn
    "#.G.H.K.E.G.H.K.E.G.",
    "####################"
]

LEVEL_21_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BPZZZZZZ.BPZZZZZZ.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.ZZZZZZ.B.ZZZZZZ.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.HHHHHH.B.HHHHHH.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.GGGGGG.B.ZZZZZZ.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.BBBBBB.B.GGZZZZ.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.EEEEEE.B.EEEEEE.B.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.HHHHHH.B.GGGGGG.B.",
    "B.L.L.L.L.B.K.K.K.K.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.EEEEEE.B.EEEEEE.BZ", # Added Z for electricity spawn
    "BBBBBBBBBBBLBBBBBBBB"
]

LEVEL_22_MAP = [
    "X..................X",
    "X.P.E.E.E.E.E.E.E.L.",
    "X..................X",
    "X.G.H.K.G.H.K.G.H.K.",
    "X..................X",
    "X.E.E.E.E.E.E.E.E.E.",
    "X..................X",
    "X.G.H.K.G.H.K.G.H.K.",
    "X..................X",
    "X.E.E.E.E.E.E.E.E.E.",
    "X..................X",
    "X.G.H.K.G.H.K.G.H.K.",
    "X..................X",
    "X.E.E.E.E.E.E.E.E.E.",
    "X..................X",
    "X.G.H.K.G.H.K.G.H.KZ", # Added Z for electricity spawn
    "X.E.E.E.E.E.E.E.E.E.",
    "X..................X"
]

LEVEL_23_MAP = [
    "####################",
    "#P#.#.#.#.B.E.H.B.BL",
    "#.HHH.HEE.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.###.###.##",
    "#.#.#.#.#.#.#.#.#.#.",
    "#.###.###.BBB.###.##",
    "#E.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "#B################B#",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_24_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BP..........E......B",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.#.#.#.#.#.#.#.#.#.",
    "B.L.........G.H.K.L.",
    "B.E.E.E.E.E.E.E.E.E.",
    "B.G.H.K.G.H.K.G.H.KZ", # Added Z for electricity spawn
    "BBBBBBBBBBBBBBBBBBBB"
]

LEVEL_25_MAP = [
    "XBBBBBBBBBBBBBBBBBBX",
    "XPB..............L.X",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.B.",
    "X.B.B.B.B.B.B.B.B.BZ", # Added Z for electricity spawn
    "X.E.E.E.E.E.E.E.E.E.",
    "XBBBBBBBBBBBBBBBBBBX"
]

LEVEL_26_MAP = [
    "####################",
    "#P.K.............E.#",
    "#.#############.####",
    "#.#.#.#.#.#.#.#.#..#",
    "#.#.#.#.#.#.#.#.#.##",
    "#.#.#.#.#.#.#.#.#..#",
    "#.#.#.H.#.#.#.#.#.##",
    "#.#.#.#.#.#.#.#.#..#",
    "#.#.#.#.#.#.#.#.#.##",
    "#.#.#.#.#.#.#.#.#..#",
    "#.L.B###########.H#.",
    "#.#.#.#.#.#.#.#.#..#",
    "#.#.#.#.#.#.#.#.#.##",
    "#.#.#.#.#.#.#.#.#..#",
    "#.LB###########.####",
    "#...............EZ.#", # Added Z for electricity spawn
    "####################",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_27_MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "BPGGGGGGGGGGGGGGGGLB",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.G.G.G.G.G.G.G.G.G.",
    "B.B.B.B.B.B.B.B.B.B.",
    "B.E.E.E.E.E.E.E.E.E.",
    "B.E.E.E.E.E.E.E.E.EZ", # Added Z for electricity spawn
    "BBBBBBBBBBBLBBBBBBBB"
]

LEVEL_28_MAP = [
    "X##################X",
    "X#P.H.H.H.H.H.H.H.E#",
    "X#.###############.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.#.H.H.H.H.H.H.H.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.#.H.H.H.H.H.H.H.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.#.H.H.H.H.H.H.H.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.#.H.H.H.H.H.H.H.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.#.H.H.H.H.H.H.H.#",
    "X#.#.E.E.E.E.E.E.E.#",
    "X#.L.H.H.H.H.H.H.H.#",
    "X#................EZ#", # Added Z for electricity spawn
    "X##################X",
    "XXXXXXXXXXXXXXXXXXXX"
]

LEVEL_29_MAP = [
    "X..................X",
    "X.P................X",
    "X.........E........X",
    "X..................X",
    "X........G.........X",
    "X..................X",
    "X.........H........X",
    "X..................X",
    "X........E.........X",
    "X..................X",
    "X.........K........X",
    "X..................X",
    "X........E.........X",
    "X..................X",
    "X........L.........X",
    "X..................X",
    "X.........EZ.......X", # Added Z for electricity spawn
    "X..................X"
]

LEVEL_30_MAP = [
    "####################",
    "#P................L#",
    "#.################.#",
    "#.###G###.E.E.E.###.",
    "#.###H###.B.B.B.###.",
    "#.###K###.E.E.E.###.",
    "#.################.#",
    "#.###G###.E.E.E.###.",
    "#.###H###.B.B.B.B###",
    "#.###K###.E.E.E.###.",
    "#.################.#",
    "#.###G###.E.E.E.###.",
    "#.###H###.B.B.B.###.",
    "#.###K###.E.E.E.###.",
    "#.################.#",
    "#................Z.#", # Added Z for electricity spawn
    "####################",
    "XXXXXXXXXXXXXXXXXXXX"
]

ALL_LEVEL_MAPS = [
    LEVEL_1_MAP, LEVEL_2_MAP, LEVEL_3_MAP, LEVEL_4_MAP, LEVEL_5_MAP,
    LEVEL_6_MAP, LEVEL_7_MAP, LEVEL_8_MAP, LEVEL_9_MAP, LEVEL_10_MAP,
    LEVEL_11_MAP, LEVEL_12_MAP, LEVEL_13_MAP, LEVEL_14_MAP, LEVEL_15_MAP,
    LEVEL_16_MAP, LEVEL_17_MAP, LEVEL_18_MAP, LEVEL_19_MAP, LEVEL_20_MAP,
    LEVEL_21_MAP, LEVEL_22_MAP, LEVEL_23_MAP, LEVEL_24_MAP, LEVEL_25_MAP,
    LEVEL_26_MAP, LEVEL_27_MAP, LEVEL_28_MAP, LEVEL_29_MAP, LEVEL_30_MAP
]

music_files = {
    0: "level_1_music.mp3", 1: "level_2_music.mp3", 2: "level_3_music.mp3",
    3: "level_4_music.mp3", 4: "level_5_music.mp3", 5: "level_6_music.mp3",
    6: "level_7_music.mp3", 7: "level_8_music.mp3", 8: "level_9_music.mp3",
    9: "level_10_music.mp3", 10: "level_11_music.mp3", 11: "level_12_music.mp3",
    12: "level_13_music.mp3", 13: "level_14_music.mp3", 14: "level_15_music.mp3",
    15: "level_16_music.mp3", 16: "level_17_music.mp3", 17: "level_18_music.mp3",
    18: "level_19_music.mp3", 19: "level_20_music.mp3", 20: "level_21_music.mp3",
    21: "level_22_music.mp3", 22: "level_23_music.mp3", 23: "level_24_music.mp3",
    24: "level_25_music.mp3", 25: "level_26_music.mp3", 26: "level_27_music.mp3",
    27: "level_28_music.mp3", 28: "level_29_music.mp3", 29: "level_30_music.mp3"
}


maze_width_tiles = len(ALL_LEVEL_MAPS[0][0])
maze_height_tiles = len(ALL_LEVEL_MAPS[0])

# Calculate TILE_SIZE based on a single maze's dimensions
tile_size_from_width = (actual_display_width - MAZE_GAP) // (maze_width_tiles * 2) # Divide by 2 for two mazes side-by-side, account for gap
tile_size_from_height = (actual_display_height - INFO_BAR_HEIGHT) // maze_height_tiles

TILE_SIZE = max(20, min(tile_size_from_width, tile_size_from_height, 40))

# Redefine game dimensions based on the new TILE_SIZE and two mazes
game_width_single_maze = maze_width_tiles * TILE_SIZE
game_area_height_single_maze = maze_height_tiles * TILE_SIZE
game_width_total = (2 * game_width_single_maze) + MAZE_GAP # Added MAZE_GAP here
game_height_total = game_area_height_single_maze + INFO_BAR_HEIGHT

screen = pygame.display.set_mode((game_width_total, game_height_total))
pygame.display.set_caption("Dungeon Explorer Multiplayer")

PLAYER_SPEED = max(1, int(0.1 * TILE_SIZE))
ENEMY_SPEED_PATROL = max(0.5, 0.04 * TILE_SIZE) 
ENEMY_SPEED_CHASE = max(0.75, 0.06 * TILE_SIZE) 

PLAYER_ATTACK_RANGE = TILE_SIZE * 1.5
ENEMY_PATROL_DISTANCE = TILE_SIZE * 5
ENEMY_MELEE_ATTACK_RANGE = TILE_SIZE * 1.2
BREAKABLE_WALL_HEALTH = 40 
GOLD_VALUE = 25 
HEALTH_POTION_HEAL = 20 

PLAYER_ATTACK_DAMAGE = 10
PLAYER_ATTACK_COOLDOWN_MS = 300
ENEMY_ATTACK_DAMAGE = 5
ENEMY_ATTACK_COOLDOWN_MS = 1000

# --- Constants for Electricity Event (moved here for global access) ---
ELECTRICITY_PARTICLE_COUNT = 80
ELECTRICITY_EFFECT_DURATION_MS = 1000
BONUS_ENEMIES_TO_SPAWN = 2

font = pygame.font.Font(None, FONT_SIZE)
large_font = pygame.font.Font(None, FONT_SIZE * 2)

# --- Global Networking Variables ---
server_socket = None # Server's listening socket
client_socket = None # Client's connection to server, or server's connection to client
is_server_instance = False # True if this instance is the server
is_connected = False # True once a client/server connection is established
game_running_flag = True # Controls main game loop and threads

# --- Helper Functions for Grid-Pixel Conversion ---
def get_tile_pixel_coords(row, col, x_offset=0):
    return col * TILE_SIZE + x_offset, row * TILE_SIZE

def get_tile_indices(pixel_x, pixel_y, x_offset=0):
    return int(pixel_y // TILE_SIZE), int((pixel_x - x_offset) // TILE_SIZE)

def get_tile_center_pixel_coords(row, col, x_offset=0):
    return (col * TILE_SIZE) + TILE_SIZE // 2 + x_offset, (row * TILE_SIZE) + TILE_SIZE // 2

# --- Fireworks Classes ---
class FireworkParticle:
    def __init__(self, x, y, vx, vy, color, radius, lifespan, is_rocket=False, is_trail=False, can_reexplode=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.original_color = color
        self.color = color
        self.radius = radius
        self.lifespan = lifespan
        self.current_lifespan = lifespan
        self.is_rocket = is_rocket
        self.is_trail = is_trail
        self.can_reexplode = can_reexplode

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.current_lifespan -= 1
        
        if not self.is_rocket:
            fade_factor = self.current_lifespan / self.lifespan
            if fade_factor < 0: fade_factor = 0
            self.color = (int(self.original_color[0] * fade_factor),
                          int(self.original_color[1] * fade_factor),
                          int(self.original_color[2] * fade_factor))
        else:
            self.color = self.original_color
        
        if not self.is_rocket:
            self.radius = max(0.1, self.radius * fade_factor)

    def draw(self, surface):
        if self.current_lifespan > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class FireworksManager:
    def __init__(self):
        self.particles = []
        self.last_launch_time = 0
        self.launch_interval = 100
        self.is_active = False

        self.explosion_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 165, 0), (128, 0, 128),
            (255, 105, 180)
        ]
        self.next_trail_spawn_time = 0

    def launch_firework(self):
        global chateau_image_original, chateau_rect_final_pos
        now = pygame.time.get_ticks()
        if now - self.last_launch_time > self.launch_interval:
            if chateau_rect_final_pos and chateau_image_original:
                launch_padding = TILE_SIZE // 2
                start_x = random.randint(chateau_rect_final_pos.left + launch_padding, chateau_rect_final_pos.right - launch_padding)
                start_y = chateau_rect_final_pos.top - TILE_SIZE // 2
            else:
                start_x = random.randint(game_width_total // 5, game_width_total * 4 // 5)
                start_y = game_area_height_single_maze
            
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-15, -10)
            
            color = random.choice(self.explosion_colors)
            rocket = FireworkParticle(start_x, start_y, vx, vy, color, random.uniform(10, 14), random.randint(200, 250), is_rocket=True)
            self.particles.append(rocket)
            self.last_launch_time = now

    def spawn_rocket_trail(self, rocket_particle):
        now = pygame.time.get_ticks()
        if now > self.next_trail_spawn_time:
            trail_color = (max(0, rocket_particle.original_color[0] - 50),
                           max(0, rocket_particle.original_color[1] - 50),
                           max(0, rocket_particle.original_color[2] - 50))
            
            trail_x = rocket_particle.x - rocket_particle.vx * 0.5
            trail_y = rocket_particle.y - rocket_particle.vy * 0.5
            
            trail_vx = random.uniform(-0.5, 0.5)
            trail_vy = random.uniform(-0.5, 0.5)
            
            trail_particle = FireworkParticle(trail_x, trail_y, trail_vx, trail_vy, trail_color, random.uniform(1, 2), 20, is_trail=True)
            self.particles.append(trail_particle)
            self.next_trail_spawn_time = now + random.randint(50, 100)

    def explode_firework(self, x, y, base_color, is_secondary_explosion=False):
        if not is_secondary_explosion:
            num_color_segments = random.randint(2, 4)
            chosen_colors = random.sample(self.explosion_colors, num_color_segments)
            sparks_per_segment = random.randint(150, 250)
            total_sparks = num_color_segments * sparks_per_segment
        else:
            chosen_colors = [base_color]
            sparks_per_segment = random.randint(10, 20)
            total_sparks = sparks_per_segment

        for i in range(total_sparks):
            color_index = i % len(chosen_colors)
            spark_base_color = chosen_colors[color_index]

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 8) if not is_secondary_explosion else random.uniform(2, 4)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            
            spark_lifespan = random.randint(150, 250)
            spark_radius = random.uniform(5, 8) if not is_secondary_explosion else random.uniform(2, 3.5)
            
            spark_color = (min(255, max(0, spark_base_color[0] + random.randint(-50, 50))),
                           min(255, max(0, spark_base_color[1] + random.randint(-50, 50))),
                           min(255, max(0, spark_base_color[2] + random.randint(-50, 50))))

            can_reexplode = False
            if not is_secondary_explosion and random.random() < 0.35:
                can_reexplode = True

            spark = FireworkParticle(x, y, vx, vy, spark_color, spark_radius, spark_lifespan, can_reexplode=can_reexplode)
            self.particles.append(spark)

    def update(self):
        if self.is_active:
            self.launch_firework()

        new_particles = []
        for p in self.particles:
            if p.is_rocket:
                self.spawn_rocket_trail(p)
            
            p.update()

            if p.current_lifespan <= 0:
                if p.is_rocket:
                    self.explode_firework(p.x, p.y, p.original_color, is_secondary_explosion=False)
                elif p.can_reexplode:
                    self.explode_firework(p.x, p.y, p.original_color, is_secondary_explosion=True)
            else:
                new_particles.append(p)
        self.particles = new_particles

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

fireworks_manager = FireworksManager()

# --- Global variables for Chateau Image ---
chateau_image_original = None
chateau_image_current_state = None
chateau_rect_final_pos = None

# --- Castle Deformation Variables ---
castle_deforming_active = False
castle_deformation_start_time = 0
debris_particles = []
game_quit_timer = 0

class ElectricityParticle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-TILE_SIZE/4, TILE_SIZE/4)
        self.y = y + random.uniform(-TILE_SIZE/4, TILE_SIZE/4)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.lifespan = random.randint(20, 40)
        self.radius = random.uniform(1, 3)
        self.color = ELECTRICITY_COLOR

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1
        fade_factor = self.lifespan / max(1, self.lifespan)
        self.color = (int(ELECTRICITY_COLOR[0] * fade_factor),
                      int(ELECTRICITY_COLOR[1] * fade_factor),
                      int(ELECTRICITY_COLOR[2] * fade_factor))
        self.radius = max(0.1, self.radius * fade_factor)

    def draw(self, surface):
        if self.lifespan > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class DebrisParticle:
    def __init__(self, x, y, vx, vy, size, color, angle=0, angular_velocity=0, image_chunk=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.original_color = color
        self.color = color
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.lifespan = random.randint(300, 600)
        self.current_lifespan = self.lifespan
        self.is_settled = False
        self.image_chunk = image_chunk

        if image_chunk:
            self.surface = image_chunk
            self.rect_size = self.surface.get_size()
            self.shape_type = "image"
        else:
            self.shape_type = random.choice(["rect", "circle"])
            if self.shape_type == "rect":
                self.rect_size = size
                self.surface = pygame.Surface(self.rect_size, pygame.SRCALPHA)
                self.surface.fill(self.original_color)
            else:
                self.radius = size[0] / 2
                self.rect_size = (size[0], size[0])
                self.surface = pygame.Surface((self.rect_size[0], self.rect_size[0]), pygame.SRCALPHA)
                pygame.draw.circle(self.surface, self.original_color, (self.radius, self.radius), self.radius)

    def update(self):
        if self.current_lifespan <= 0 and self.is_settled:
            return

        if not self.is_settled:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.2

            self.angle += self.angular_velocity

            bottom_edge = game_area_height_single_maze
            if self.y + self.rect_size[1] // 2 >= bottom_edge:
                self.y = bottom_edge - self.rect_size[1] // 2
                self.vx *= 0.5
                self.vy = 0
                self.angular_velocity *= 0.5
                self.is_settled = True
                self.lifespan = random.randint(600, 1200)
                self.current_lifespan = self.lifespan

        self.current_lifespan -= 1
        fade_factor = self.current_lifespan / self.lifespan
        if fade_factor < 0: fade_factor = 0
        
        if self.image_chunk:
            self.surface.set_alpha(int(255 * fade_factor))
        else:
            self.color = (int(self.original_color[0] * fade_factor),
                          int(self.original_color[1] * fade_factor),
                          int(self.original_color[2] * fade_factor))
            self.surface.fill((0,0,0,0))
            if self.shape_type == "rect":
                pygame.draw.rect(self.surface, self.color, (0, 0, self.rect_size[0], self.rect_size[1]))
            else:
                pygame.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

    def draw(self, surface):
        if self.current_lifespan <= 0 and self.is_settled:
            return

        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        rotated_rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_surface, rotated_rect)

# --- Game Object Classes ---
class GameObject:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface, x_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset
        pygame.draw.rect(surface, self.color, draw_rect)

class Wall(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE, BLUE)

    def draw(self, surface, x_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset
        pygame.draw.rect(surface, self.color, draw_rect)
        pygame.draw.rect(surface, BLACK, draw_rect, max(1, TILE_SIZE // 40))

class BreakableWall(Wall):
    def __init__(self, x, y, map_layout_ref, row, col):
        super().__init__(x, y)
        self.original_color = BREAKABLE_WALL_INITIAL_COLOR
        self.color = self.original_color
        self.health = BREAKABLE_WALL_HEALTH 
        self.max_health = BREAKABLE_WALL_HEALTH 
        self.last_hit_time = 0
        # Store row/col for server to update map_layout_ref
        self.row = row
        self.col = col
        self.map_layout_ref = map_layout_ref # Reference to the actual current_map_layout list

    def take_damage(self, amount):
        self.health -= amount
        self.last_hit_time = pygame.time.get_ticks() # Only relevant for visual flash

    def draw(self, surface, x_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset

        current_time = pygame.time.get_ticks()
        draw_color = self.original_color
        if current_time - self.last_hit_time < 100:
            draw_color = (255, 100, 100)
        elif self.health < self.max_health:
            health_ratio = self.health / self.max_health
            current_r = int(self.original_color[0] * health_ratio + BREAKABLE_WALL_COLOR_DAMAGED[0] * (1 - health_ratio))
            current_g = int(self.original_color[1] * health_ratio + BREAKABLE_WALL_COLOR_DAMAGED[1] * (1 - health_ratio))
            current_b = int(self.original_color[2] * health_ratio + BREAKABLE_WALL_COLOR_DAMAGED[2] * (1 - health_ratio))
            draw_color = (current_r, current_g, current_b)

        pygame.draw.rect(surface, draw_color, draw_rect)
        pygame.draw.rect(surface, BLACK, draw_rect, max(1, TILE_SIZE // 40))

    def get_state(self):
        return {
            'x': self.rect.x,
            'y': self.rect.y,
            'health': self.health,
            'row': self.row,
            'col': self.col
        }

    def set_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.health = state['health']
        self.row = state['row']
        self.col = state['col']

class Player(GameObject):
    def __init__(self, x, y, player_id):
        player_rect_size = TILE_SIZE - int(4 * (TILE_SIZE / 40.0))
        color = PAC_MAN_YELLOW if player_id == 1 else GREEN
        super().__init__(x - player_rect_size // 2, y - player_rect_size // 2, player_rect_size, player_rect_size, color)
        self.player_id = player_id # 1 for server's player, 2 for client's player
        self.speed = PLAYER_SPEED
        self.health = 100
        self.max_health = 100
        self.keys = 0
        self.score = 0
        self.desired_direction = NO_DIRECTION
        self.current_direction = NO_DIRECTION
        self.last_attack_time = 0

        self.current_row, self.current_col = get_tile_indices(x, y)
        self.target_x, self.target_y = get_tile_center_pixel_coords(self.current_row, self.current_col)
        self.rect.center = (self.target_x, self.target_y)

        self.mouth_open = True
        self.animation_timer = 0
        self.animation_interval = 100

    def update(self, walls_list, x_offset=0):
        epsilon = self.speed / 2.0
        at_tile_center = math.hypot(self.rect.centerx - self.target_x, self.rect.centery - self.target_y) < epsilon

        if at_tile_center:
            self.rect.center = (self.target_x, self.target_y)
            self.current_row, self.current_col = get_tile_indices(self.rect.centerx, self.rect.centery, x_offset)

            if self.desired_direction != NO_DIRECTION:
                potential_next_row = self.current_row + self.desired_direction[1]
                potential_next_col = self.current_col + self.desired_direction[0]
                
                if 0 <= potential_next_row < maze_height_tiles and 0 <= potential_next_col < maze_width_tiles:
                    next_tile_center_x, next_tile_center_y = get_tile_center_pixel_coords(potential_next_row, potential_next_col, x_offset)
                    temp_rect = pygame.Rect(next_tile_center_x - self.rect.width // 2, next_tile_center_y - self.rect.height // 2, self.rect.width, self.rect.height)

                    if not self.check_collisions(walls_list, test_rect=temp_rect):
                        self.current_direction = self.desired_direction
                        self.target_x, self.target_y = next_tile_center_x, next_tile_center_y
                    else:
                        self.current_direction = NO_DIRECTION
                else:
                    self.current_direction = NO_DIRECTION
            else:
                self.current_direction = NO_DIRECTION
                self.target_x, self.target_y = get_tile_center_pixel_coords(self.current_row, self.current_col, x_offset)

        if self.current_direction != NO_DIRECTION:
            dx = self.target_x - self.rect.centerx
            dy = self.target_y - self.rect.centery
            distance_to_target = math.hypot(dx, dy)

            if distance_to_target <= self.speed:
                self.rect.center = (self.target_x, self.target_y)
            elif distance_to_target > 0:
                move_x = (dx / distance_to_target) * self.speed
                move_y = (dy / distance_to_target) * self.speed
                self.rect.x += int(move_x)
                self.rect.y += int(move_y)
        else:
            self.rect.center = (self.target_x, self.target_y)
            self.current_row, self.current_col = get_tile_indices(self.rect.centerx, self.rect.centery, x_offset)

        # Restrict movement within its own maze's boundaries
        self.rect.left = max(x_offset, min(self.rect.left, x_offset + game_width_single_maze - self.rect.width))
        self.rect.top = max(0, min(self.rect.top, game_area_height_single_maze - self.rect.height))

        now = pygame.time.get_ticks()
        if self.current_direction != NO_DIRECTION and now - self.animation_timer > self.animation_interval:
            self.mouth_open = not self.mouth_open
            self.animation_timer = now
        elif self.current_direction == NO_DIRECTION:
            self.mouth_open = False

    def check_collisions(self, walls_list, test_rect=None):
        rect_to_check = test_rect if test_rect else self.rect
        for wall_obj in walls_list:
            if rect_to_check.colliderect(wall_obj.rect):
                return True
        return False

    def attack(self, enemies_list, walls_list, current_map_layout_ref):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > PLAYER_ATTACK_COOLDOWN_MS:
            self.last_attack_time = now

            targets_hit = []

            for enemy in enemies_list:
                dist = math.hypot(self.rect.centerx - enemy.rect.centerx,
                                  self.rect.centery - enemy.rect.centery)
                if dist < PLAYER_ATTACK_RANGE:
                    targets_hit.append(enemy)

            for wall_obj in walls_list:
                if isinstance(wall_obj, BreakableWall):
                    dist = math.hypot(self.rect.centerx - wall_obj.rect.centerx,
                                      self.rect.centery - wall_obj.rect.centery)
                    if dist < PLAYER_ATTACK_RANGE:
                        targets_hit.append(wall_obj)

            for target in targets_hit:
                if isinstance(target, Player):
                    continue
                if isinstance(target, Enemy):
                    target.take_damage(PLAYER_ATTACK_DAMAGE)
                elif isinstance(target, BreakableWall):
                    target.take_damage(PLAYER_ATTACK_DAMAGE)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def add_key(self):
        self.keys += 1

    def add_score(self, amount):
        self.score += amount

    def draw(self, surface, x_offset=0):
        draw_center = (self.rect.centerx + x_offset, self.rect.centery)
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset

        pygame.draw.circle(surface, self.color, draw_center, self.rect.width // 2)

        mouth_half_opening_deg = 45
        if not self.mouth_open:
            mouth_half_opening_deg = 5

        start_angle_body = 0
        end_angle_body = 0

        draw_direction = self.current_direction if self.current_direction != NO_DIRECTION else RIGHT
        
        if draw_direction == RIGHT:
            start_angle_body = mouth_half_opening_deg
            end_angle_body = 360 - mouth_half_opening_deg
        elif draw_direction == LEFT:
            start_angle_body = 180 + mouth_half_opening_deg
            end_angle_body = 180 - mouth_half_opening_deg + 360
        elif draw_direction == UP:
            start_angle_body = 90 + mouth_half_opening_deg
            end_angle_body = 90 - mouth_half_opening_deg + 360
        elif draw_direction == DOWN:
            start_angle_body = 270 + mouth_half_opening_deg
            end_angle_body = 270 - mouth_half_opening_deg + 360

        mouth_points = [draw_center]
        radius = self.rect.width // 2
        step_value = 5

        start_angle_normalized = start_angle_body % 360
        end_angle_normalized = end_angle_body % 360
        if end_angle_normalized < start_angle_normalized:
            end_angle_normalized += 360

        for angle in range(int(start_angle_normalized), int(end_angle_normalized) + step_value, step_value):
            if angle > end_angle_normalized and angle - end_angle_normalized > step_value * 0.5:
                angle = end_angle_normalized
            x = draw_center[0] + radius * math.cos(math.radians(angle))
            y = draw_center[1] + radius * math.sin(math.radians(angle))
            mouth_points.append((x, y))

        x_final_arc = draw_center[0] + radius * math.cos(math.radians(end_angle_normalized))
        y_final_arc = draw_center[1] + radius * math.sin(math.radians(end_angle_normalized))
        if not mouth_points or (abs(x_final_arc - mouth_points[-1][0]) > 1e-6 or abs(y_final_arc - mouth_points[-1][1]) > 1e-6):
            mouth_points.append((x_final_arc, y_final_arc))

        mouth_points.append(draw_center)

        if len(mouth_points) < 3:
            mouth_points = [draw_center,
                            (draw_center[0] + radius, draw_center[1] - radius//2),
                            (draw_center[0] + radius, draw_center[1] + radius//2)]

        pygame.draw.polygon(surface, BLACK, mouth_points)

        eye_radius = int(self.rect.width // 10)
        base_eye_offset_x = self.rect.width * 0.15
        base_eye_offset_y = -self.rect.height * 0.25

        eye_rotation_angle = 0
        if draw_direction == LEFT:
            eye_rotation_angle = 180
        elif draw_direction == UP:
            eye_rotation_angle = -90
        elif draw_direction == DOWN:
            eye_rotation_angle = 90
        
        rot_rad = math.radians(eye_rotation_angle)
        rotated_eye_x = base_eye_offset_x * math.cos(rot_rad) - base_eye_offset_y * math.sin(rot_rad)
        rotated_eye_y = base_eye_offset_x * math.sin(rot_rad) + base_eye_offset_y * math.cos(rot_rad)

        eye_pos = (draw_center[0] + rotated_eye_x, draw_center[1] + rotated_eye_y)
        pygame.draw.circle(surface, BLACK, eye_pos, eye_radius)

    def get_state(self):
        return {
            'x': self.rect.x,
            'y': self.rect.y,
            'health': self.health,
            'keys': self.keys,
            'score': self.score,
            'desired_direction': self.desired_direction,
            'current_direction': self.current_direction,
            'mouth_open': self.mouth_open,
            'player_id': self.player_id
        }

    def set_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.health = state['health']
        self.keys = state['keys']
        self.score = state['score']
        self.desired_direction = state['desired_direction']
        self.current_direction = state['current_direction']
        self.mouth_open = state['mouth_open']
        # Do not set player_id, it's fixed for the instance

class Enemy(GameObject): 
    def __init__(self, x, y):
        enemy_rect_size = TILE_SIZE - int(4 * (TILE_SIZE / 40.0))
        super().__init__(x - enemy_rect_size // 2, y - enemy_rect_size // 2, enemy_rect_size, enemy_rect_size, RED)
        self.health = 30
        self.max_health = 30
        self.speed = ENEMY_SPEED_PATROL
        self.last_attack_time = 0
        self.state = "patrol"
        self.patrol_target = (self.rect.x, self.rect.y)
        self.next_patrol_move_time = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def update(self, player_obj, walls_list): # Enemy now targets only its own player
        original_pos = self.rect.topleft
        dx, dy = 0, 0

        dist_to_player = math.hypot(self.rect.centerx - player_obj.rect.centerx,
                                    self.rect.centery - player_obj.rect.centery)

        if dist_to_player < TILE_SIZE * 5:
            self.state = "chase"
            self.speed = ENEMY_SPEED_CHASE
        else:
            self.state = "patrol"
            self.speed = ENEMY_SPEED_PATROL

        if self.state == "chase":
            dx = player_obj.rect.centerx - self.rect.centerx
            dy = player_obj.rect.centery - self.rect.centery
        elif self.state == "patrol":
            now = pygame.time.get_ticks()
            if now > self.next_patrol_move_time or \
               math.hypot(self.rect.centerx - self.patrol_target[0],
                          self.rect.centery - self.patrol_target[1]) < self.speed * 2:
                self.patrol_target = (self.rect.x + random.randint(-ENEMY_PATROL_DISTANCE, ENEMY_PATROL_DISTANCE),
                                      self.rect.y + random.randint(-ENEMY_PATROL_DISTANCE, ENEMY_PATROL_DISTANCE))
                self.next_patrol_move_time = now + random.randint(1000, 3000)

            dx = self.patrol_target[0] - self.rect.centerx
            dy = self.patrol_target[1] - self.rect.centery
        
        # Calculate move_x and move_y based on dx, dy, and speed
        dist = math.hypot(dx, dy)
        if dist == 0: dist = 1 # Avoid division by zero

        move_x = (dx / dist) * self.speed
        move_y = (dy / dist) * self.speed
        
        self.rect.x += int(move_x)
        self.rect.y += int(move_y)

        collided = False
        for wall_obj in walls_list:
            if not isinstance(wall_obj, BreakableWall) and self.rect.colliderect(wall_obj.rect):
                collided = True
                break
        
        if collided:
            self.rect.topleft = original_pos

        self.rect.left = max(0, min(self.rect.left, game_width_single_maze - self.rect.width))
        self.rect.top = max(0, min(self.rect.top, game_area_height_single_maze - self.rect.height))

    def perform_attack(self, player_obj):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time > ENEMY_ATTACK_COOLDOWN_MS:
            dist_to_player = math.hypot(self.rect.centerx - player_obj.rect.centerx,
                                        self.rect.centery - player_obj.rect.centery)
            if dist_to_player < ENEMY_MELEE_ATTACK_RANGE:
                player_obj.take_damage(ENEMY_ATTACK_DAMAGE)
                self.last_attack_time = now

    def draw(self, surface, x_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset
        pygame.draw.rect(surface, self.color, draw_rect)
        if self.health < self.max_health:
            health_bar_width = self.rect.width
            health_bar_height = max(1, int(3 * (TILE_SIZE / 40.0)))
            health_percentage = self.health / self.max_health
            current_bar_width = int(health_bar_width * health_percentage)
            health_bar_rect = pygame.Rect(draw_rect.x, draw_rect.y - health_bar_height - max(1, int(2 * (TILE_SIZE / 40.0))), health_bar_width, health_bar_height)
            pygame.draw.rect(surface, HEALTH_COLOR, (health_bar_rect.x, health_bar_rect.y, current_bar_width, health_bar_height))
            pygame.draw.rect(surface, BLACK, health_bar_rect, max(1, TILE_SIZE // 40))

    def get_state(self):
        return {
            'x': self.rect.x,
            'y': self.rect.y,
            'health': self.health,
            'state': self.state,
            'patrol_target_x': self.patrol_target[0],
            'patrol_target_y': self.patrol_target[1],
            'next_patrol_move_time': self.next_patrol_move_time
        }

    def set_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.health = state['health']
        self.state = state['state']
        self.patrol_target = (state['patrol_target_x'], state['patrol_target_y'])
        self.next_patrol_move_time = state['next_patrol_move_time']

class Collectible(GameObject):
    def __init__(self, x, y, item_type):
        collectible_size = TILE_SIZE // 2
        centered_x = x + TILE_SIZE // 2 - (collectible_size // 2)
        centered_y = y + TILE_SIZE // 2 - (collectible_size // 2)
        super().__init__(centered_x, centered_y, collectible_size, collectible_size, BLACK)
        self.item_type = item_type

    def draw(self, surface, x_offset=0):
        draw_center = (self.rect.centerx + x_offset, self.rect.centery)
        draw_rect = self.rect.copy()
        draw_rect.x += x_offset

        if self.item_type == 'gold':
            pygame.draw.circle(surface, GOLD, draw_center, self.rect.width // 2)
            pygame.draw.circle(surface, BLACK, draw_center, self.rect.width // 2, max(1, TILE_SIZE // 40))
        elif self.item_type == 'health':
            pygame.draw.rect(surface, RED, draw_rect)
            line_thickness = max(1, TILE_SIZE // 15)
            pygame.draw.line(surface, WHITE, (draw_rect.centerx, draw_rect.top), (draw_rect.centerx, draw_rect.bottom), line_thickness)
            pygame.draw.line(surface, WHITE, (draw_rect.left, draw_rect.centery), (draw_rect.right, draw_rect.centery), line_thickness)
        elif self.item_type == 'key':
            key_head_radius = self.rect.width // 4
            key_body_width = self.rect.width // 2
            key_body_height = self.rect.height // 4
            key_teeth_width = self.rect.width // 4
            key_teeth_height = self.rect.height // 8
            line_thickness = max(1, TILE_SIZE // 40)

            pygame.draw.circle(surface, GOLD, (draw_rect.x + key_head_radius, draw_rect.y + key_head_radius), key_head_radius)
            pygame.draw.rect(surface, GOLD, (draw_rect.x + key_head_radius, draw_rect.y + key_body_height, key_body_width, key_body_height))
            pygame.draw.rect(surface, GOLD, (draw_rect.x + int(self.rect.width * 0.75), draw_rect.y + int(self.rect.height * 0.75), key_teeth_width, key_teeth_height))
            
            pygame.draw.circle(surface, BLACK, (draw_rect.x + key_head_radius, draw_rect.y + key_head_radius), key_head_radius, line_thickness)
            pygame.draw.rect(surface, BLACK, (draw_rect.x + key_head_radius, draw_rect.y + key_body_height, key_body_width, key_body_height), line_thickness)
            pygame.draw.rect(surface, BLACK, (draw_rect.x + int(self.rect.width * 0.75), draw_rect.y + int(self.rect.height * 0.75), key_teeth_width, key_teeth_height), line_thickness)

    def get_state(self):
        return {
            'x': self.rect.x,
            'y': self.rect.y,
            'item_type': self.item_type
        }

    def set_state(self, state):
        self.rect.x = state['x']
        self.rect.y = state['y']
        self.item_type = state['item_type'] # This is redundant but kept for consistency

class MazeState:
    def __init__(self, player_id):
        self.player = None
        self.enemies = []
        self.collectibles = []
        self.walls = []
        self.level_exit_rect = None
        self.current_map_layout = []
        self.score = 0
        self.health = 100
        self.keys = 0
        self.current_level_index = 0
        self.electricity_active = False
        self.electricity_spawn_time = 0
        self.electricity_spawn_location = (0,0)
        self.initial_enemy_count = 0
        self.bonus_enemies_spawned_this_level = False
        self.level_21_initial_enemy_data = []
        self.level_21_respawn_pending = False
        self.player_id = player_id # 1 for server's maze, 2 for client's maze

    def load_level(self, level_map):
        self.enemies.clear()
        self.collectibles.clear()
        self.walls.clear()
        self.level_exit_rect = None

        self.electricity_active = False
        self.electricity_spawn_time = 0
        self.initial_enemy_count = 0
        self.bonus_enemies_spawned_this_level = False
        self.level_21_initial_enemy_data.clear()
        self.level_21_respawn_pending = False

        self.current_map_layout = [list(row) for row in level_map]

        temp_enemies = []
        electricity_z_found = False

        for r_idx, row in enumerate(self.current_map_layout):
            for c_idx, tile_char in enumerate(row):
                x, y = get_tile_pixel_coords(r_idx, c_idx) # Use 0 offset for internal maze coords
                
                if tile_char == '#':
                    self.walls.append(Wall(x, y))
                elif tile_char == 'B':
                    self.walls.append(BreakableWall(x, y, self.current_map_layout, r_idx, c_idx))
                elif tile_char == 'P':
                    # Player starts at 'P'
                    self.player = Player(x + TILE_SIZE // 2, y + TILE_SIZE // 2, self.player_id)
                elif tile_char == 'E':
                    temp_enemies.append(Enemy(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                    if self.current_level_index == 20: # Level 21 is index 20
                        self.level_21_initial_enemy_data.append(('E', x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                elif tile_char == 'G':
                    self.collectibles.append(Collectible(x, y, 'gold'))
                elif tile_char == 'H':
                    self.collectibles.append(Collectible(x, y, 'health'))
                elif tile_char == 'K':
                    self.collectibles.append(Collectible(x, y, 'key'))
                elif tile_char == 'L':
                    self.level_exit_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                elif tile_char == 'Z':
                    self.electricity_spawn_location = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                    electricity_z_found = True
                    self.current_map_layout[r_idx][c_idx] = '.'

        self.enemies.extend(temp_enemies)
        self.initial_enemy_count = len(self.enemies)

        if not electricity_z_found:
            fallback_col = maze_width_tiles - 2
            fallback_row = maze_height_tiles - 2
            
            found_fallback = False
            for r_offset in range(2):
                for c_offset in range(2):
                    r = min(maze_height_tiles - 1, fallback_row + r_offset)
                    c = min(maze_width_tiles - 1, fallback_col + c_offset)
                    if self.current_map_layout[r][c] == '.':
                        fx, fy = get_tile_pixel_coords(r, c)
                        self.electricity_spawn_location = (fx + TILE_SIZE // 2, fy + TILE_SIZE // 2)
                        found_fallback = True
                        break
                if found_fallback: break
            
            if not found_fallback:
                fx, fy = get_tile_pixel_coords(maze_height_tiles - 1, maze_width_tiles - 1)
                self.electricity_spawn_location = (fx + TILE_SIZE // 2, fy + TILE_SIZE // 2)

        # Restore player's current stats
        if self.player:
            self.player.health = self.health
            self.player.score = self.score
            self.player.keys = self.keys

    def update_game_logic(self):
        # Player update
        if self.player:
            self.player.update(self.walls)

        # Collectibles collision
        for collectible in self.collectibles[:]:
            if self.player and self.player.rect.colliderect(collectible.rect):
                if collectible.item_type == 'gold':
                    self.score += GOLD_VALUE
                elif collectible.item_type == 'health':
                    self.health += HEALTH_POTION_HEAL
                    if self.health > 100: self.health = 100
                    self.player.health = self.health # Update player's health for UI
                elif collectible.item_type == 'key':
                    self.keys += 1
                    print(f"DEBUG (Server): Player {self.player_id} collected a key. Keys: {self.keys}") # DEBUG PRINT
                self.collectibles.remove(collectible)
        
        # Enemy updates and collision
        for enemy in self.enemies[:]: # Iterate over copy for safe removal
            enemy.update(self.player, self.walls) # Enemies now target only their own player
            
            if self.player and enemy.rect.colliderect(self.player.rect): # Check for collision
                now = pygame.time.get_ticks()
                if now - enemy.last_attack_time > ENEMY_ATTACK_COOLDOWN_MS: # Check cooldown
                    self.health -= ENEMY_ATTACK_DAMAGE
                    self.player.health = self.health # Update player's health for UI
                    enemy.last_attack_time = now
                    print(f"DEBUG (Server): Player {self.player_id} took {ENEMY_ATTACK_DAMAGE} damage. Current health: {self.health}") # DEBUG PRINT
                    if self.health < 0: self.health = 0

            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += 50
                
                if self.initial_enemy_count > 0 and len(self.enemies) == 0 and not self.bonus_enemies_spawned_this_level:
                    self.trigger_electricity_event()

        # Breakable wall destruction
        for wall_obj in self.walls[:]:
            if isinstance(wall_obj, BreakableWall) and wall_obj.health <= 0:
                self.walls.remove(wall_obj)
                self.current_map_layout[wall_obj.row][wall_obj.col] = '.'
                self.score += 10 # Score for destroying a wall

        # Update electricity particles if active
        if self.electricity_active:
            for p in electricity_particles_global[:]: # Electricity particles are global for now
                p.update()
                if p.lifespan <= 0:
                    electricity_particles_global.remove(p)

            if pygame.time.get_ticks() - self.electricity_spawn_time > ELECTRICITY_EFFECT_DURATION_MS:
                self.electricity_active = False
                
                if self.current_level_index == 20 and self.level_21_respawn_pending:
                    for enemy_data in self.level_21_initial_enemy_data:
                        spawn_x = self.electricity_spawn_location[0] + random.randint(-TILE_SIZE//2, TILE_SIZE//2)
                        spawn_y = self.electricity_spawn_location[1] + random.randint(-TILE_SIZE//2, TILE_SIZE//2)
                        self.enemies.append(Enemy(spawn_x, spawn_y))
                    
                    self.level_21_respawn_pending = False
                    self.initial_enemy_count = len(self.enemies)
                    self.bonus_enemies_spawned_this_level = False
                
                elif self.bonus_enemies_spawned_this_level and len(self.enemies) == 0:
                    for _ in range(BONUS_ENEMIES_TO_SPAWN):
                        spawn_x = self.electricity_spawn_location[0] + random.randint(-TILE_SIZE//2, TILE_SIZE//2)
                        spawn_y = self.electricity_spawn_location[1] + random.randint(-TILE_SIZE//2, TILE_SIZE//2)
                        self.enemies.append(Enemy(spawn_x, spawn_y))
                    self.initial_enemy_count = len(self.enemies)
                    self.bonus_enemies_spawned_this_level = False

    def trigger_electricity_event(self):
        if not self.bonus_enemies_spawned_this_level:
            self.electricity_active = True
            self.electricity_spawn_time = pygame.time.get_ticks()
            electricity_particles_global.clear() # Clear global particles
            for _ in range(ELECTRICITY_PARTICLE_COUNT):
                electricity_particles_global.append(ElectricityParticle(self.electricity_spawn_location[0], self.electricity_spawn_location[1]))
            
            self.bonus_enemies_spawned_this_level = True

            if self.current_level_index == 20:
                self.level_21_respawn_pending = True

    def get_serializable_state(self):
        players_state = self.player.get_state() if self.player else None
        enemies_state = [e.get_state() for e in self.enemies]
        collectibles_state = [c.get_state() for c in self.collectibles]
        
        walls_state = []
        for w in self.walls:
            w_state = w.get_state()
            if isinstance(w, BreakableWall):
                w_state['is_breakable'] = True # Mark breakable walls
            walls_state.append(w_state)

        exit_rect_state = None
        if self.level_exit_rect:
            exit_rect_state = (self.level_exit_rect.x, self.level_exit_rect.y, self.level_exit_rect.width, self.level_exit_rect.height)

        return {
            'player': players_state,
            'enemies': enemies_state,
            'collectibles': collectibles_state,
            'walls': walls_state,
            'score': self.score,
            'health': self.health, # Ensure MazeState's health is serialized
            'keys': self.keys,
            'current_level_index': self.current_level_index,
            'level_exit_rect': exit_rect_state,
            'electricity_active': self.electricity_active,
            'electricity_spawn_time': self.electricity_spawn_time,
            'bonus_enemies_spawned_this_level': self.bonus_enemies_spawned_this_level,
            'level_21_respawn_pending': self.level_21_respawn_pending,
            'player_id': self.player_id
        }

    def set_state(self, state):
        # Update MazeState's core attributes first
        self.score = state.get('score', 0)
        self.health = state.get('health', 100) # Update MazeState's health from received state
        self.keys = state.get('keys', 0)
        self.current_level_index = state.get('current_level_index', 0)

        if state['player']:
            if self.player:
                self.player.set_state(state['player'])
            else: # Create player if it doesn't exist (e.g., on initial sync)
                self.player = Player(state['player']['x'], state['player']['y'], state['player']['player_id'])
                self.player.set_state(state['player'])
            # Ensure player's health matches MazeState's health after setting player state
            self.player.health = self.health
        
        self.enemies.clear()
        for e_state in state.get('enemies', []):
            new_enemy = Enemy(0, 0)
            new_enemy.set_state(e_state)
            self.enemies.append(new_enemy)

        self.collectibles.clear()
        for c_state in state.get('collectibles', []):
            new_collectible = Collectible(0, 0, c_state['item_type'])
            new_collectible.set_state(c_state)
            self.collectibles.append(new_collectible)

        new_walls = []
        for w_state in state.get('walls', []):
            if w_state.get('is_breakable'):
                new_wall = BreakableWall(0, 0, None, w_state['row'], w_state['col'])
                new_wall.set_state(w_state)
            else:
                new_wall = Wall(0, 0)
                new_wall.set_state(w_state)
            new_walls.append(new_wall)
        self.walls[:] = new_walls

        exit_rect_state = state.get('level_exit_rect')
        if exit_rect_state:
            self.level_exit_rect = pygame.Rect(exit_rect_state[0], exit_rect_state[1], exit_rect_state[2], exit_rect_state[3])
        else:
            self.level_exit_rect = None

        self.electricity_active = state.get('electricity_active', False)
        self.electricity_spawn_time = state.get('electricity_spawn_time', 0)
        self.bonus_enemies_spawned_this_level = state.get('bonus_enemies_spawned_this_level', False)
        self.level_21_respawn_pending = state.get('level_21_respawn_pending', False)

# --- Game State Instances ---
# Server will have two actual game states
maze_state_p1 = None # Server's own maze and player
maze_state_p2 = None # Client's maze and player, controlled by client input

# Client will have two view-only game states
maze_state_p1_view = None # View of server's maze
maze_state_p2_view = None # View of client's own maze

# Global electricity particles (shared for visual effect across both mazes on a screen)
electricity_particles_global = []

# Overall game state variables
overall_game_state = GAME_STATE_MODE_SELECT
winning_player_id = 0 # 0 for no winner, 1 for P1, 2 for P2

login_music_playing = False

# Login Screen variables
username_input = ""
password_input = ""
active_input_field = "username"
login_error_message = ""
login_successful = False

username_box_rect = pygame.Rect(game_width_total // 2 - 100, game_height_total // 2 - 60, 200, 30)
password_box_rect = pygame.Rect(game_width_total // 2 - 100, game_height_total // 2, 200, 30)

# Intro animation variables
intro_logo = None
ring_base_img = None
violet_arc_img = None
intro_angle_arc = 0
intro_angle_logo = 0
intro_start_time = 0
music_duration = 5.0

last_skip_time = 0
SKIP_COOLDOWN_MS = 500

# --- Animated Coin Visual Effect Class ---
class AnimatedCoinVisual:
    ANIMATION_SPEED = 15 # Pixels per frame for coin animation

    def __init__(self, start_pos, target_pos, x_offset=0):
        self.current_pos = list(start_pos) # Use a list so we can modify it
        self.target_pos = (target_pos[0] + x_offset, target_pos[1]) # Adjust target for maze offset
        self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4) # Draw a gold circle
        self.rect = self.image.get_rect(center=self.current_pos)

    def update(self):
        # Calculate direction vector
        dx = self.target_pos[0] - self.current_pos[0]
        dy = self.target_pos[1] - self.current_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.ANIMATION_SPEED:
            # Move towards target
            self.current_pos[0] += (dx / distance) * self.ANIMATION_SPEED
            self.current_pos[1] += (dy / distance) * self.ANIMATION_SPEED
        else:
            # Reached target or very close
            self.current_pos = list(self.target_pos)
            return True # Signal that animation is complete
        self.rect.center = self.current_pos
        return False # Signal that animation is ongoing

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Lists for client-side visual coin animations
animating_coins_p1_visual = []
animating_coins_p2_visual = []

# Store previous collectible states to detect removals
previous_collectibles_p1 = []
previous_collectibles_p2 = []

# --- Networking Functions ---

def send_game_state(sock, state_data):
    """Sends the entire game state from server to client."""
    try:
        serialized_data = pickle.dumps(state_data)
        sock.sendall(serialized_data)
    except (socket.error, TypeError) as e:
        print(f"Error sending game state: {e}")
        global is_connected, game_running_flag
        is_connected = False
        game_running_flag = False # Stop game if connection breaks

def receive_game_state(sock):
    """Receives game state from the server."""
    try:
        data = b''
        while True:
            packet = sock.recv(RECV_BUFFER_SIZE)
            if not packet:
                break
            data += packet
            if len(packet) < RECV_BUFFER_SIZE: # Assume packet is complete if it's smaller than buffer
                break
        if data:
            return pickle.loads(data)
    except (socket.error, EOFError, pickle.UnpicklingError) as e:
        print(f"Error receiving game state: {e}")
        global is_connected, game_running_flag
        is_connected = False
        game_running_flag = False # Stop game if connection breaks
    return None

def server_thread_function(conn, addr):
    """Handles communication with a single client."""
    global is_connected, game_running_flag, maze_state_p1, maze_state_p2, overall_game_state, winning_player_id

    print(f"Accepted connection from {addr}")
    is_connected = True

    try:
        while game_running_flag and is_connected:
            # Server receives client's player input
            client_input = receive_game_state(conn) # Using receive_game_state for generic data
            if client_input is None:
                print("Client disconnected or error receiving input.")
                break

            # Update maze_state_p2 (client's player) based on client_input
            if maze_state_p2 and maze_state_p2.player and client_input.get('player_desired_direction') is not None:
                maze_state_p2.player.desired_direction = client_input['player_desired_direction']
            
            # Server sends full game state (both mazes) to client
            full_game_state = {
                'maze_state_p1': maze_state_p1.get_serializable_state() if maze_state_p1 else None,
                'maze_state_p2': maze_state_p2.get_serializable_state() if maze_state_p2 else None,
                'overall_game_state': overall_game_state,
                'winning_player_id': winning_player_id,
                'electricity_particles_global': [(p.x, p.y, p.radius, p.color) for p in electricity_particles_global]
            }
            send_game_state(conn, full_game_state)
            time.sleep(0.01) # Small delay to prevent busy-waiting
    finally:
        conn.close()
        print(f"Connection with {addr} closed.")
        is_connected = False
        # Do NOT set game_running_flag to False here, as the server might want to wait for another client
        # Or handle this more gracefully depending on game design (e.g., reset and wait for new connection)

def server_listener_thread():
    """Dedicated thread to listen for and accept new client connections."""
    global server_socket, is_connected, game_running_flag
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5) # Listen for up to 5 pending connections
        print(f"Server listening on {HOST}:{PORT}")

        while game_running_flag: # Keep running as long as the game is active
            try:
                conn, addr = server_socket.accept() # This is the blocking call, waits for a client
                print(f"Accepted connection from {addr}")
                # Spawn a new thread to handle this specific client connection
                client_handler_thread = threading.Thread(target=server_thread_function, args=(conn, addr), daemon=True)
                client_handler_thread.start()
                is_connected = True # Set connected flag once a client is accepted
            except OSError as e:
                # Handle specific error if socket is closed while waiting for accept
                if "An operation was attempted on something that is not a socket" in str(e) or "Bad file descriptor" in str(e):
                    print("Server socket was closed, stopping listener thread.")
                    break # Exit loop if socket is no longer valid
                else:
                    print(f"Error accepting connection: {e}")
                    time.sleep(0.1) # Small pause before retrying accept
            except Exception as e:
                print(f"Unexpected error in server listener: {e}")
                break # Break on other unexpected errors
    except Exception as e:
        print(f"Failed to start server socket: {e}")
    finally:
        if server_socket:
            server_socket.close()
            print("Server listener socket closed.")
        is_connected = False # Ensure connection status is false on exit

def client_thread_function(server_addr):
    """Handles communication with the server."""
    global client_socket, is_connected, game_running_flag, maze_state_p1_view, maze_state_p2_view, overall_game_state, winning_player_id, electricity_particles_global, \
           animating_coins_p1_visual, animating_coins_p2_visual, previous_collectibles_p1, previous_collectibles_p2

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_addr)
        print(f"Connected to server at {server_addr}")
        is_connected = True

        while game_running_flag and is_connected:
            # Client sends its player input to server
            if maze_state_p2_view and maze_state_p2_view.player:
                player_input = {'player_desired_direction': maze_state_p2_view.player.desired_direction}
                send_game_state(client_socket, player_input)
            else:
                send_game_state(client_socket, {'player_desired_direction': NO_DIRECTION}) # Send empty input if player not ready

            # Client receives full game state from server
            full_game_state = receive_game_state(client_socket)
            if full_game_state is None:
                print("Server disconnected or error receiving state.")
                break

            # Store current collectible positions before updating maze states
            current_collectibles_p1_coords = set()
            if full_game_state.get('maze_state_p1'):
                for c_state in full_game_state['maze_state_p1'].get('collectibles', []):
                    current_collectibles_p1_coords.add((c_state['x'], c_state['y']))

            current_collectibles_p2_coords = set()
            if full_game_state.get('maze_state_p2'):
                for c_state in full_game_state['maze_state_p2'].get('collectibles', []):
                    current_collectibles_p2_coords.add((c_state['x'], c_state['y']))

            # Update client's view of both mazes
            if full_game_state.get('maze_state_p1'):
                if maze_state_p1_view is None:
                    maze_state_p1_view = MazeState(1) # Player 1 is server's player
                maze_state_p1_view.set_state(full_game_state['maze_state_p1'])
            
            if full_game_state.get('maze_state_p2'):
                if maze_state_p2_view is None:
                    maze_state_p2_view = MazeState(2) # Player 2 is client's player
                maze_state_p2_view.set_state(full_game_state['maze_state_p2'])
            
            overall_game_state = full_game_state.get('overall_game_state', GAME_STATE_PLAYING)
            winning_player_id = full_game_state.get('winning_player_id', 0)

            # Update global electricity particles based on server's data
            electricity_particles_global.clear()
            for p_data in full_game_state.get('electricity_particles_global', []):
                x, y, radius, color = p_data
                p = ElectricityParticle(x, y)
                p.radius = radius
                p.color = color
                electricity_particles_global.append(p)

            # --- Coin Animation Trigger (Client-side) ---
            # For P1's maze
            if maze_state_p1_view:
                for prev_c_state in previous_collectibles_p1:
                    prev_x, prev_y, prev_item_type = prev_c_state
                    if prev_item_type == 'gold' and (prev_x, prev_y) not in current_collectibles_p1_coords:
                        # Gold coin was collected! Start animation.
                        animating_coins_p1_visual.append(AnimatedCoinVisual((prev_x + TILE_SIZE // 2, prev_y + TILE_SIZE // 2),
                                                                           (game_width_single_maze - 100, game_area_height_single_maze + 30), # Target score pos P1
                                                                           x_offset=0))
                        if pickup_sound:
                            pickup_sound.play()

            # For P2's maze
            if maze_state_p2_view:
                maze2_x_offset = game_width_single_maze + MAZE_GAP
                for prev_c_state in previous_collectibles_p2:
                    prev_x, prev_y, prev_item_type = prev_c_state
                    if prev_item_type == 'gold' and (prev_x, prev_y) not in current_collectibles_p2_coords:
                        # Gold coin was collected! Start animation.
                        animating_coins_p2_visual.append(AnimatedCoinVisual((prev_x + TILE_SIZE // 2, prev_y + TILE_SIZE // 2),
                                                                           (game_width_single_maze - 100, game_area_height_single_maze + 30), # Target score pos P2
                                                                           x_offset=maze2_x_offset))
                        if pickup_sound:
                            pickup_sound.play()

            # Update previous collectibles for next frame's comparison
            previous_collectibles_p1 = [(c.rect.x, c.rect.y, c.item_type) for c in maze_state_p1_view.collectibles] if maze_state_p1_view else []
            previous_collectibles_p2 = [(c.rect.x, c.rect.y, c.item_type) for c in maze_state_p2_view.collectibles] if maze_state_p2_view else []


            time.sleep(0.01) # Small delay to prevent busy-waiting
    finally:
        client_socket.close()
        print("Disconnected from server.")
        is_connected = False
        game_running_flag = False # Stop game if server disconnects

# --- Game Logic Functions ---

def play_level_music(level_index):
    """Loads and plays the music for the given level index."""
    try:
        music_file = music_files.get(level_index)
        if music_file:
            print(f"DEBUG: Attempting to load and play music for level {level_index + 1}: {music_file}")
            pygame.mixer.music.stop() # Ensure any previous music is stopped
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1) # Loop indefinitely
            print(f"DEBUG: Successfully started playing music for level {level_index + 1}: {music_file}")
        else:
            print(f"DEBUG: No music file found for level {level_index + 1}. Stopping music.")
            pygame.mixer.music.stop()
    except pygame.error as e:
        print(f"ERROR: Pygame mixer error playing music for level {level_index + 1}: {e}")

def advance_level():
    """Advances both mazes to the next level."""
    global current_level_index, overall_game_state, maze_state_p1, maze_state_p2, winning_player_id, castle_deforming_active, castle_deformation_start_time, fireworks_manager

    current_level_index += 1
    if current_level_index < len(ALL_LEVEL_MAPS):
        print(f"DEBUG (Server): Advancing to Level {current_level_index + 1}!") # DEBUG PRINT
        
        # Preserve player stats before loading new level
        p1_health = maze_state_p1.health
        p1_score = maze_state_p1.score
        p1_keys = maze_state_p1.keys

        p2_health = maze_state_p2.health
        p2_score = maze_state_p2.score
        p2_keys = maze_state_p2.keys

        # Load new level for both mazes
        maze_state_p1.current_level_index = current_level_index
        maze_state_p1.load_level(ALL_LEVEL_MAPS[current_level_index])
        maze_state_p2.current_level_index = current_level_index
        maze_state_p2.load_level(ALL_LEVEL_MAPS[current_level_index])

        # Restore player stats
        maze_state_p1.health = p1_health
        maze_state_p1.score = p1_score
        maze_state_p1.keys = p1_keys

        maze_state_p2.health = p2_health
        maze_state_p2.score = p2_score
        maze_state_p2.keys = p2_keys

        overall_game_state = GAME_STATE_PLAYING
        play_level_music(current_level_index)

    else:
        print("All levels complete! Game Over - You Win!")
        overall_game_state = GAME_STATE_GAME_OVER
        winning_player_id = 1 # Server's player wins (arbitrary for now, could be highest score)
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load('win_music.mp3')
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Error playing win music: {e}")
        
        # Start castle deformation and fireworks
        castle_deforming_active = True
        castle_deformation_start_time = pygame.time.get_ticks()
        fireworks_manager.is_active = True

def start_game():
    """Initializes game state and starts playing."""
    global overall_game_state, game_start_time, current_level_index, maze_state_p1, maze_state_p2, electricity_particles_global
    overall_game_state = GAME_STATE_PLAYING
    game_start_time = pygame.time.get_ticks()
    current_level_index = 0 # Ensure this is always 0 at start
    electricity_particles_global.clear() # Clear any lingering particles

    # Server side initialization
    if is_server_instance:
        maze_state_p1.health = 100 # Reset health for P1
        maze_state_p1.score = 0   # Reset score for P1
        maze_state_p1.keys = 0    # Reset keys for P1
        maze_state_p1.current_level_index = 0
        maze_state_p1.load_level(ALL_LEVEL_MAPS[maze_state_p1.current_level_index])

        # For the client's maze state on the server, reset and load level 1 as well
        maze_state_p2.health = 100 # Reset health for P2
        maze_state_p2.score = 0   # Reset score for P2
        maze_state_p2.keys = 0    # Reset keys for P2
        maze_state_p2.current_level_index = 0
        maze_state_p2.load_level(ALL_LEVEL_MAPS[maze_state_p2.current_level_index])
    
    print(f"DEBUG: Calling play_level_music for level index: {current_level_index}")
    play_level_music(current_level_index)

def handle_login(username, password):
    global login_error_message, login_successful, overall_game_state, login_music_playing
    # Simple dummy authentication
    if username == "user" and password == "pass":
        login_successful = True
        login_error_message = ""
        overall_game_state = GAME_STATE_INTRO # Transition to intro screen
        pygame.mixer.music.stop() # Stop login music
        login_music_playing = False
        print("Login successful. Transitioning to intro.")
        # Start intro animation timer
        global intro_start_time
        intro_start_time = pygame.time.get_ticks()
    else:
        login_successful = False
        login_error_message = "Invalid username or password."
        print("Login failed.")

def draw_text(surface, text, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_large_text(surface, text, color, x, y, center=False):
    text_surface = large_font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_info_bar(surface, maze_state, x_offset):
    bar_rect = pygame.Rect(x_offset, game_area_height_single_maze, game_width_single_maze, INFO_BAR_HEIGHT)
    pygame.draw.rect(surface, BLACK, bar_rect)
    pygame.draw.rect(surface, WHITE, bar_rect, 2) # Border

    if maze_state and maze_state.player:
        player = maze_state.player
        # Adjust score text position slightly for animation target
        score_text_pos_x = x_offset + game_width_single_maze - 100
        score_text_pos_y = game_area_height_single_maze + 30 # This is the target for coin animation

        draw_text(surface, f"Health: {player.health}", WHITE, x_offset + 10, game_area_height_single_maze + 10)
        draw_text(surface, f"Score: {player.score}", WHITE, score_text_pos_x, score_text_pos_y)
        draw_text(surface, f"Keys: {player.keys}", WHITE, x_offset + 10, game_area_height_single_maze + 50)
        draw_text(surface, f"Level: {maze_state.current_level_index + 1}", WHITE, x_offset + game_width_single_maze - 100, game_area_height_single_maze + 10)
    else:
        draw_text(screen, "Waiting for player data...", WHITE, x_offset + 10, game_area_height_single_maze + 10)

def draw_game_over_screen():
    screen.fill(BLACK)
    if winning_player_id == 1:
        draw_large_text(screen, "SERVER PLAYER WINS!", GOLD, game_width_total // 2, game_height_total // 2 - 50, center=True)
    elif winning_player_id == 2:
        draw_large_text(screen, "CLIENT PLAYER WINS!", GOLD, game_width_total // 2, game_height_total // 2 - 50, center=True)
    else:
        draw_large_text(screen, "GAME OVER!", RED, game_width_total // 2, game_height_total // 2 - 50, center=True)
    
    draw_text(screen, "Thanks for playing!", WHITE, game_width_total // 2, game_height_total // 2 + 10, center=True)
    draw_text(screen, "The castle has been destroyed!", WHITE, game_width_total // 2, game_height_total // 2 + 40, center=True)
    
    global game_quit_timer
    if game_quit_timer == 0:
        game_quit_timer = pygame.time.get_ticks()
    
    if pygame.time.get_ticks() - game_quit_timer > castle_deformation_duration_ms + 2000: # Wait for deformation + 2 seconds
        draw_text(screen, "Quitting in 3...", WHITE, game_width_total // 2, game_height_total // 2 + 80, center=True)
    if pygame.time.get_ticks() - game_quit_timer > castle_deformation_duration_ms + 3000:
        draw_text(screen, "Quitting in 2...", WHITE, game_width_total // 2, game_height_total // 2 + 80, center=True)
    if pygame.time.get_ticks() - game_quit_timer > castle_deformation_duration_ms + 4000:
        draw_text(screen, "Quitting in 1...", WHITE, game_width_total // 2, game_height_total // 2 + 80, center=True)
    
    fireworks_manager.draw(screen)

def draw_level_complete_screen():
    screen.fill(BLACK)
    draw_large_text(screen, "LEVEL COMPLETE!", GOLD, game_width_total // 2, game_height_total // 2 - 50, center=True)
    draw_text(screen, f"Proceeding to Level {current_level_index + 1}...", WHITE, game_width_total // 2, game_height_total // 2 + 10, center=True)

def draw_mode_select_screen():
    screen.fill(BLACK)
    draw_large_text(screen, "Select Mode", WHITE, game_width_total // 2, game_height_total // 2 - 100, center=True)
    
    server_button_rect = pygame.Rect(game_width_total // 2 - 100, game_height_total // 2 - 20, 200, 50)
    client_button_rect = pygame.Rect(game_width_total // 2 - 100, game_height_total // 2 + 40, 200, 50)

    pygame.draw.rect(screen, BLUE, server_button_rect)
    pygame.draw.rect(screen, BLUE, client_button_rect)

    draw_text(screen, "Start Server", WHITE, server_button_rect.centerx, server_button_rect.centery, center=True)
    draw_text(screen, "Connect as Client", WHITE, client_button_rect.centerx, client_button_rect.centery, center=True)
    return server_button_rect, client_button_rect

def draw_login_screen():
    screen.fill(BLACK)
    draw_large_text(screen, "Login", WHITE, game_width_total // 2, game_height_total // 2 - 150, center=True)

    # Username input box
    pygame.draw.rect(screen, TEXT_INPUT_BOX_COLOR, username_box_rect)
    if active_input_field == "username":
        pygame.draw.rect(screen, TEXT_INPUT_BORDER_COLOR, username_box_rect, 2)
    draw_text(screen, username_input, WHITE, username_box_rect.x + 5, username_box_rect.y + 5)
    draw_text(screen, "Username:", WHITE, username_box_rect.x, username_box_rect.y - 20)

    # Password input box
    pygame.draw.rect(screen, TEXT_INPUT_BOX_COLOR, password_box_rect)
    if active_input_field == "password":
        pygame.draw.rect(screen, TEXT_INPUT_BORDER_COLOR, password_box_rect, 2)
    draw_text(screen, "*" * len(password_input), WHITE, password_box_rect.x + 5, password_box_rect.y + 5)
    draw_text(screen, "Password:", WHITE, password_box_rect.x, password_box_rect.y - 20 + 60) # Adjusted y for password label

    # Login button
    login_button_rect = pygame.Rect(game_width_total // 2 - 50, game_height_total // 2 + 60, 100, 40)
    pygame.draw.rect(screen, BLUE, login_button_rect)
    draw_text(screen, "Login", WHITE, login_button_rect.centerx, login_button_rect.centery, center=True)

    if login_error_message:
        draw_text(screen, login_error_message, ERROR_MESSAGE_COLOR, game_width_total // 2, game_height_total // 2 + 120, center=True)
    
    return login_button_rect

def draw_intro_screen():
    global intro_angle_arc, intro_angle_logo, intro_logo, ring_base_img, violet_arc_img, intro_start_time, music_duration

    screen.fill(BLACK)

    elapsed_time = (pygame.time.get_ticks() - intro_start_time) / 1000.0

    if intro_logo and ring_base_img and violet_arc_img:
        # Scale images
        scale_factor = min(1.0, elapsed_time / 2.0) # Scale up over 2 seconds
        
        scaled_logo_size = (int(intro_logo.get_width() * scale_factor), int(intro_logo.get_height() * scale_factor))
        scaled_logo = pygame.transform.scale(intro_logo, scaled_logo_size)

        scaled_ring_size = (int(ring_base_img.get_width() * scale_factor), int(ring_base_img.get_height() * scale_factor))
        scaled_ring_base = pygame.transform.scale(ring_base_img, scaled_ring_size)
        scaled_violet_arc = pygame.transform.scale(violet_arc_img, scaled_ring_size)

        # Rotate elements
        intro_angle_arc = (intro_angle_arc + 1) % 360
        intro_angle_logo = (intro_angle_logo + 0.5) % 360

        rotated_arc = pygame.transform.rotate(scaled_violet_arc, intro_angle_arc)
        rotated_logo = pygame.transform.rotate(scaled_logo, intro_angle_logo)

        # Blit elements
        ring_rect = scaled_ring_base.get_rect(center=(game_width_total // 2, game_height_total // 2))
        arc_rect = rotated_arc.get_rect(center=(game_width_total // 2, game_height_total // 2))
        logo_rect = rotated_logo.get_rect(center=(game_width_total // 2, game_height_total // 2))

        screen.blit(scaled_ring_base, ring_rect)
        screen.blit(rotated_arc, arc_rect)
        screen.blit(rotated_logo, logo_rect)

    draw_large_text(screen, "DUNGEON EXPLORER", WHITE, game_width_total // 2, game_height_total // 2 + 150, center=True)
    draw_text(screen, "Press SPACE to Skip", WHITE, game_width_total // 2, game_height_total // 2 + 200, center=True)

    if elapsed_time > music_duration:
        start_game()

def draw_chateau_destruction_animation():
    global chateau_image_current_state, chateau_rect_final_pos, castle_deforming_active, castle_deformation_start_time, debris_particles, game_quit_timer, game_running_flag

    if chateau_image_original is None:
        try:
            chateau_image_original = pygame.image.load('chateau.png').convert_alpha()
        except pygame.error:
            print("Chateau image not found. Using a placeholder rectangle.")
            chateau_image_original = pygame.Surface((400, 300), pygame.SRCALPHA)
            chateau_image_original.fill((50, 50, 50, 150)) # Semi-transparent gray
            pygame.draw.rect(chateau_image_original, (100, 100, 100), chateau_image_original.get_rect(), 5)

    if chateau_image_current_state is None:
        chateau_image_current_state = chateau_image_original.copy()
        chateau_rect_final_pos = chateau_image_current_state.get_rect(center=(game_width_total // 2, game_area_height_single_maze - chateau_image_current_state.get_height() // 2))

    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - castle_deformation_start_time

    if elapsed_time < castle_deformation_duration_ms:
        deformation_progress = elapsed_time / castle_deformation_duration_ms
        
        # Create deformation effect by randomly shifting pixels or chunks
        if random.random() < 0.2: # Adjust frequency of deformation
            if chateau_image_current_state:
                img_width, img_height = chateau_image_current_state.get_size()
                
                # Option 2: Chunk displacement and debris generation
                chunk_size = random.randint(5, 20)
                cx = random.randint(0, img_width - chunk_size)
                cy = random.randint(0, img_height - chunk_size)
                
                chunk_rect = pygame.Rect(cx, cy, chunk_size, chunk_size)
                chunk_surface = chateau_image_current_state.subsurface(chunk_rect).copy()
                
                # Clear the chunk area in the original image
                chateau_image_current_state.fill((0,0,0,0), chunk_rect) # Fill with transparent

                # Create a debris particle from the chunk
                debris_x = chateau_rect_final_pos.x + cx + chunk_size // 2
                debris_y = chateau_rect_final_pos.y + cy + chunk_size // 2
                debris_vx = random.uniform(-5, 5) * (1 + deformation_progress * 2)
                debris_vy = random.uniform(-10, -5) * (1 + deformation_progress * 2)
                debris_angular_velocity = random.uniform(-5, 5)
                
                debris_particles.append(DebrisParticle(debris_x, debris_y, debris_vx, debris_vy, (chunk_size, chunk_size), DEBRIS_COLOR, image_chunk=chunk_surface))

        # Overall image fade (optional, but good for destruction)
        alpha = max(0, int(255 * (1 - deformation_progress)))
        chateau_image_current_state.set_alpha(alpha)

    # Draw the current state of the chateau
    if chateau_image_current_state:
        screen.blit(chateau_image_current_state, chateau_rect_final_pos)

    # Update and draw debris particles
    for particle in debris_particles[:]:
        particle.update()
        if particle.current_lifespan <= 0 and particle.is_settled:
            debris_particles.remove(particle)
        else:
            particle.draw(screen)
    
    if elapsed_time > castle_deformation_duration_ms + 5000: # Quit after animation and a few seconds
        game_running_flag = False

def run_game():
    global overall_game_state, game_running_flag, current_level_index, winning_player_id, \
           chateau_image_original, chateau_image_current_state, chateau_rect_final_pos, \
           castle_deforming_active, castle_deformation_start_time, game_quit_timer, \
           login_error_message, login_successful, username_input, password_input, active_input_field, \
           last_skip_time, intro_start_time, intro_logo, ring_base_img, violet_arc_img, intro_angle_arc, intro_angle_logo, \
           login_music_playing, pickup_sound, coin_pile_drop_sound, \
           animating_coins_p1_visual, animating_coins_p2_visual, previous_collectibles_p1, previous_collectibles_p2

    clock = pygame.time.Clock()

    # Load intro assets once
    try:
        intro_logo = pygame.image.load('logo.png').convert_alpha()
    except pygame.error:
        print("logo.png not found. Using a placeholder surface.")
        intro_logo = pygame.Surface((100, 100), pygame.SRCALPHA)
        intro_logo.fill((255, 0, 0, 150)) # Red placeholder

    try:
        ring_base_img = pygame.image.load('ring_base.png').convert_alpha()
    except pygame.error:
        print("ring_base.png not found. Using a placeholder surface.")
        ring_base_img = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(ring_base_img, (0, 0, 255, 150), (100, 100), 90, 5) # Blue circle placeholder

    try:
        violet_arc_img = pygame.image.load('violet_arc.png').convert_alpha()
    except pygame.error:
        print("violet_arc.png not found. Using a placeholder surface.")
        violet_arc_img = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.arc(violet_arc_img, (138, 43, 226, 150), (0, 0, 200, 200), math.radians(0), math.radians(180), 10) # Violet arc placeholder

    # Load general game sounds
    try:
        pygame.mixer.Sound('pickup_gold.wav') # Example, load all sounds here
    except pygame.error as e:
        print(f"Could not load game sounds: {e}")

    # Load pickup and coin drop sounds
    try:
        pickup_sound = pygame.mixer.Sound("pickup_gold.wav")
        pickup_sound.set_volume(0.5)
    except pygame.error as e:
        print(f"Warning: Could not load pickup_gold.wav. Error: {e}")
        pickup_sound = None

    try:
        coin_pile_drop_sound = pygame.mixer.Sound("coin_pile_drop.wav")
        coin_pile_drop_sound.set_volume(0.7)
    except pygame.error as e:
        print(f"Warning: Could not load coin_pile_drop.wav. Error: {e}")
        coin_pile_drop_sound = None

    # Initial music for login screen
    if overall_game_state == GAME_STATE_LOGIN and not login_music_playing:
        try:
            pygame.mixer.music.load('login_screen_music.mp3')
            pygame.mixer.music.play(-1)
            login_music_playing = True
        except pygame.error as e:
            print(f"Error playing login music: {e}")

    while game_running_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running_flag = False
            
            if overall_game_state == GAME_STATE_MODE_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    server_rect, client_rect = draw_mode_select_screen() # Get rects for click detection
                    if server_rect.collidepoint(event.pos):
                        global is_server_instance, maze_state_p1, maze_state_p2
                        is_server_instance = True
                        overall_game_state = GAME_STATE_LOGIN
                        
                        # Initialize maze states for server
                        maze_state_p1 = MazeState(1) # Server's own maze
                        maze_state_p2 = MazeState(2) # Client's maze (on server)
                        
                        # Start the dedicated server listener thread
                        server_listener = threading.Thread(target=server_listener_thread, daemon=True)
                        server_listener.start()

                    elif client_rect.collidepoint(event.pos):
                        global client_socket
                        is_server_instance = False
                        overall_game_state = GAME_STATE_LOGIN
                        print("Connecting as client...")
                        # Initialize maze states for client (view only)
                        global maze_state_p1_view, maze_state_p2_view
                        maze_state_p1_view = MazeState(1)
                        maze_state_p2_view = MazeState(2)
                        
                        # Start client thread
                        client_thread = threading.Thread(target=client_thread_function, args=((HOST if HOST else '127.0.0.1', PORT),), daemon=True)
                        client_thread.start()

            elif overall_game_state == GAME_STATE_LOGIN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    login_button_rect = draw_login_screen() # Get rect for click detection
                    if username_box_rect.collidepoint(event.pos):
                        active_input_field = "username"
                    elif password_box_rect.collidepoint(event.pos):
                        active_input_field = "password"
                    elif login_button_rect.collidepoint(event.pos):
                        handle_login(username_input, password_input)
                elif event.type == pygame.KEYDOWN:
                    if active_input_field == "username":
                        if event.key == pygame.K_RETURN:
                            active_input_field = "password"
                        elif event.key == pygame.K_BACKSPACE:
                            username_input = username_input[:-1]
                        else:
                            username_input += event.unicode
                    elif active_input_field == "password":
                        if event.key == pygame.K_RETURN:
                            handle_login(username_input, password_input)
                        elif event.key == pygame.K_BACKSPACE:
                            password_input = password_input[:-1]
                        else:
                            password_input += event.unicode

            elif overall_game_state == GAME_STATE_INTRO:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    now = pygame.time.get_ticks()
                    if now - last_skip_time > SKIP_COOLDOWN_MS:
                        start_game()
                        last_skip_time = now

            elif overall_game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    player_maze_state = maze_state_p1 if is_server_instance else maze_state_p2_view
                    if player_maze_state and player_maze_state.player:
                        if event.key == pygame.K_UP:
                            player_maze_state.player.desired_direction = UP
                        elif event.key == pygame.K_DOWN:
                            player_maze_state.player.desired_direction = DOWN
                        elif event.key == pygame.K_LEFT:
                            player_maze_state.player.desired_direction = LEFT
                        elif event.key == pygame.K_RIGHT:
                            player_maze_state.player.desired_direction = RIGHT
                        elif event.key == pygame.K_SPACE: # Attack key
                            # Only server processes attacks
                            if is_server_instance:
                                player_maze_state.player.attack(player_maze_state.enemies, player_maze_state.walls, player_maze_state.current_map_layout)

                elif event.type == pygame.KEYUP:
                    player_maze_state = maze_state_p1 if is_server_instance else maze_state_p2_view
                    if player_maze_state and player_maze_state.player:
                        if event.key == pygame.K_UP and player_maze_state.player.desired_direction == UP:
                            player_maze_state.player.desired_direction = NO_DIRECTION
                        elif event.key == pygame.K_DOWN and player_maze_state.player.desired_direction == DOWN:
                            player_maze_state.player.desired_direction = NO_DIRECTION
                        elif event.key == pygame.K_LEFT and player_maze_state.player.desired_direction == LEFT:
                            player_maze_state.player.desired_direction = NO_DIRECTION
                        elif event.key == pygame.K_RIGHT and player_maze_state.player.desired_direction == RIGHT:
                            player_maze_state.player.desired_direction = NO_DIRECTION

        # --- Game State Updates ---
        if overall_game_state == GAME_STATE_PLAYING:
            if is_server_instance:
                # Server updates both mazes' logic
                if maze_state_p1:
                    maze_state_p1.update_game_logic()
                    if maze_state_p1.player.health <= 0:
                        overall_game_state = GAME_STATE_GAME_OVER
                        winning_player_id = 2 # P2 wins if P1 dies
                        pygame.mixer.music.stop()
                        try:
                            pygame.mixer.music.load('game_over_music.mp3')
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print(f"Error playing game over music: {e}")

                    if maze_state_p1.level_exit_rect and maze_state_p1.player.rect.colliderect(maze_state_p1.level_exit_rect):
                        print(f"DEBUG (Server): Player 1 collided with exit. Advancing level.") # DEBUG PRINT
                        advance_level()
                
                if maze_state_p2:
                    maze_state_p2.update_game_logic()
                    if maze_state_p2.player.health <= 0:
                        overall_game_state = GAME_STATE_GAME_OVER
                        winning_player_id = 1 # P1 wins if P2 dies
                        pygame.mixer.music.stop()
                        try:
                            pygame.mixer.music.load('game_over_music.mp3')
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print(f"Error playing game over music: {e}")

                    if maze_state_p2.level_exit_rect and maze_state_p2.player.rect.colliderect(maze_state_p2.level_exit_rect):
                        print(f"DEBUG (Server): Player 2 collided with exit. Advancing level.") # DEBUG PRINT
                        advance_level()
            else:
                # Client only updates its own player's desired direction based on input
                # The actual game state is received from the server
                if maze_state_p2_view and maze_state_p2_view.player:
                    # Client's player logic (only movement input)
                    maze_state_p2_view.player.update(maze_state_p2_view.walls)
            
            # Update visual coin animations (client-side only)
            coins_to_remove_p1 = []
            for i, anim_coin in enumerate(animating_coins_p1_visual):
                if anim_coin.update():
                    coins_to_remove_p1.append(i)
                    if coin_pile_drop_sound:
                        coin_pile_drop_sound.play()
            for i in sorted(coins_to_remove_p1, reverse=True):
                del animating_coins_p1_visual[i]

            coins_to_remove_p2 = []
            for i, anim_coin in enumerate(animating_coins_p2_visual):
                if anim_coin.update():
                    coins_to_remove_p2.append(i)
                    if coin_pile_drop_sound:
                        coin_pile_drop_sound.play()
            for i in sorted(coins_to_remove_p2, reverse=True):
                del animating_coins_p2_visual[i]


        # --- Drawing ---
        screen.fill(BLACK)

        if overall_game_state == GAME_STATE_MODE_SELECT:
            draw_mode_select_screen()
        elif overall_game_state == GAME_STATE_LOGIN:
            draw_login_screen()
        elif overall_game_state == GAME_STATE_INTRO:
            draw_intro_screen()
        elif overall_game_state == GAME_STATE_PLAYING:
            # Draw Maze 1 (Server's Maze)
            current_maze_p1 = maze_state_p1 if is_server_instance else maze_state_p1_view
            if current_maze_p1:
                for r_idx, row in enumerate(current_maze_p1.current_map_layout):
                    for c_idx, tile_char in enumerate(row):
                        x, y = get_tile_pixel_coords(r_idx, c_idx)
                        pygame.draw.rect(screen, FLOOR_COLOR, (x, y, TILE_SIZE, TILE_SIZE)) # Draw floor
                
                for wall in current_maze_p1.walls:
                    wall.draw(screen)
                if current_maze_p1.level_exit_rect:
                    pygame.draw.rect(screen, EXIT_COLOR, current_maze_p1.level_exit_rect)
                    # DEBUG: Draw yellow border around exit tile
                    pygame.draw.rect(screen, (255, 255, 0), current_maze_p1.level_exit_rect, 2)
                for collectible in current_maze_p1.collectibles:
                    collectible.draw(screen)
                for enemy in current_maze_p1.enemies:
                    enemy.draw(screen)
                if current_maze_p1.player:
                    current_maze_p1.player.draw(screen)
                draw_info_bar(screen, current_maze_p1, 0)
            else:
                draw_text(screen, "Waiting for server to initialize P1 maze...", WHITE, game_width_single_maze // 2, game_area_height_single_maze // 2, center=True)


            # Draw Maze 2 (Client's Maze)
            current_maze_p2 = maze_state_p2 if is_server_instance else maze_state_p2_view
            maze2_x_offset = game_width_single_maze + MAZE_GAP
            if current_maze_p2:
                for r_idx, row in enumerate(current_maze_p2.current_map_layout):
                    for c_idx, tile_char in enumerate(row):
                        x, y = get_tile_pixel_coords(r_idx, c_idx, maze2_x_offset)
                        pygame.draw.rect(screen, FLOOR_COLOR, (x, y, TILE_SIZE, TILE_SIZE)) # Draw floor
                
                for wall in current_maze_p2.walls:
                    wall.draw(screen, maze2_x_offset)
                if current_maze_p2.level_exit_rect:
                    draw_rect = current_maze_p2.level_exit_rect.copy()
                    draw_rect.x += maze2_x_offset
                    pygame.draw.rect(screen, EXIT_COLOR, draw_rect)
                    # DEBUG: Draw yellow border around exit tile
                    pygame.draw.rect(screen, (255, 255, 0), draw_rect, 2)
                for collectible in current_maze_p2.collectibles:
                    collectible.draw(screen, maze2_x_offset)
                for enemy in current_maze_p2.enemies:
                    enemy.draw(screen, maze2_x_offset)
                if current_maze_p2.player:
                    current_maze_p2.player.draw(screen, maze2_x_offset)
                draw_info_bar(screen, current_maze_p2, maze2_x_offset)
            else:
                draw_text(screen, "Waiting for server to initialize P2 maze...", WHITE, maze2_x_offset + game_width_single_maze // 2, game_area_height_single_maze // 2, center=True)

            # Draw electricity particles (global effect)
            for p in electricity_particles_global:
                p.draw(screen)

            # Draw visual coin animations (client-side only)
            for anim_coin in animating_coins_p1_visual:
                anim_coin.draw(screen)
            for anim_coin in animating_coins_p2_visual:
                anim_coin.draw(screen)

        elif overall_game_state == GAME_STATE_LEVEL_COMPLETE:
            draw_level_complete_screen()
        elif overall_game_state == GAME_STATE_GAME_OVER:
            draw_chateau_destruction_animation()
            draw_game_over_screen()
            fireworks_manager.update()

        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup
    if server_socket:
        server_socket.close()
    if client_socket:
        client_socket.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
