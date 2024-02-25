# BEGIN OUTLINE
"""
TODO :
- Save game using game notation?
- Connected areas count?
"""
# END   OUTLINE


# BEGIN IMPORTS

from leaves import Dir
import pygame
import colortools as ct

# END   IMPORTS


# BEGIN CONSTANTS

DIR_DATA = {
    Dir.NORTH: ("↓", "North"),
    Dir.EAST:  ("⟵ ", "East"),
    Dir.SOUTH: ("↑", "South"),
    Dir.WEST:  ("⟶ ", "West"),
}

DIR_DATA_ANY = ("⟳", "*any direction*")

PIECE_DATA = {
    -1: ("[]","Log",           ct.COLORS['earth']),
    0: ("░░", "First player",  ct.mix(ct.PINK,ct.VIOLET,0.25)),
    1: ("██", "Second player", ct.mix(ct.MINT,ct.MOSS,0.25)),
    2: ("▒▒", "Third player",  ct.mix(ct.PERIWINKLE,ct.BLUE,0.25)),
    3: ("▓▓", "Fourth player", ct.mix(ct.SALMON,ct.YELLOW,0.25)),
}

PIECE_DATA_EMPTY = ('  ',"(empty)", ct.BLACK)

# END   CONSTANTS


# BEGIN DECORATORS
# No decorators
# END   DECORATORS


# BEGIN CLASSES
# No classes
# END   CLASSES


# BEGIN FUNCTIONS
# No functions
# END   FUNCTIONS


# BEGIN MAIN
# No main
# END   MAIN
