# Games Options/Settings
TITTLE = "Jumper!"
WIDTH = 500
HEIGHT = 650
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "Spritesheets/spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

# Game properties
BOOST_POWER = 60
POW_SPAWN_PCT = 7
MOB_FREQ = 5000

# Platform list
PLAYER_LIST = [ (0, HEIGHT-40),
                (WIDTH/2-50, HEIGHT*3/4),
                (100, HEIGHT-350),
                (WIDTH-150, HEIGHT-500)]

# Define Colors
color = {
    "red": (255, 0, 0),
    "white": (255, 255, 255),
    "blue": (0, 0, 255),
    "green": (0,255,0),
    "black": (0, 0, 0),
    "lightblue":(0, 155, 155)}
BGCOLOR = color["lightblue"]