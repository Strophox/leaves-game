# BEGIN OUTLINE
"""
This file contains constant declarations for some cosmetic leaves.Game data.
"""
# END   OUTLINE


# BEGIN IMPORTS

from leaves import Dir
import colortools as ct

# END   IMPORTS


# BEGIN CONSTANTS

DIR_DATA = {
    Dir.NORTH: ("↓", "North"),
    Dir.EAST:  ("⟵ ", "East"),
    Dir.SOUTH: ("↑", "South"),
    Dir.WEST:  ("⟶ ", "West"),
}
"""Data dictionary for each direction variant."""

DIR_DATA_ANY = ("⟳", "*any direction*")
"""Data dictionary for a designated "any" direction variant."""

PIECE_DATA = {
    -1: ("[]","Log", [
          ((0.0,0.0), (1.0,1.0), ct.mix(ct.ORANGE,ct.GRAY,0.8)),
              (m:=0.875)and()or
          (((1-m)/2,(1-m)/2), (m,m), ct.COLORS['earth']),
        ]),
    0: ("░░", "First player", [
          ((0.0,0.0), (1.0,1.0), ct.mix(ct.PINK,ct.VIOLET,0.125)),
       ]),
    1: ("██", "Second player", [
          ((0.0,0.0), (1.0,1.0), ct.mix(ct.MINT,ct.MOSS,0.25)),
       ]),
    2: ("▒▒", "Third player", [
          ((0.0,0.0), (1.0,1.0), ct.mix(ct.PERIWINKLE,ct.BLUE,0.25)),
       ]),
    3: ("▓▓", "Fourth player", [
          ((0.0,0.0), (1.0,1.0), ct.mix(ct.SALMON,ct.YELLOW,0.25)),
       ]),
}
"""Data dictionary for each player piece variant."""

PIECE_DATA_EMPTY = ('  ',"(empty)", ct.BLACK)
"""Data dictionary for a designated "empty" player piece variant."""

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
