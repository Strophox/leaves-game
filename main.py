# BEGIN OUTLINE
"""
This script is to be executed as main and allows playing the game in console and in pygame.
"""
# END   OUTLINE


# BEGIN IMPORTS

import leaves
import leaves_console
import leaves_pygame

# END   IMPORTS


# BEGIN CONSTANTS
# No constants
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

def main():
    #game = LeavesGame()
    game = leaves.Game(log_pieces=5, players=2, pieces_per_player=10)
    leaves_console.run(game)
    leaves_pygame.run(game)
    return

if __name__=="__main__": main()

# END   MAIN
