# BEGIN OUTLINE
"""
If you want to recap the rules:
- place from four directions, push 1 tile
- no placing in the middle of a row
- gaps shrink
- 90 degrees rule
- ABBAABB… turns
+ 5 logs, 10 green, 10 red
"""
# END   OUTLINE


# BEGIN IMPORTS
# No imports
# END   IMPORTS


# BEGIN CONSTANTS

ANY   = -1
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

# END   CONSTANTS


# BEGIN DECORATORS
# No decorators
# END   DECORATORS


# BEGIN CLASSES

class LeavesGame:
    def __init__(self):
        self._board_pieces = {(0,y):-1 for y in range(5)} # TODO
        self._turn_sequence = self._make_sequence(2,10,2)
        self._current_player = next(self._turn_sequence)
        self._current_direction = ANY

    def __repr__(self):
        def show(x,y):
            """Given a coordinate, return a way to represent the piece there."""
            if (x,y) not in self._board_pieces:
                return ' '
            else:
                piece = self._board_pieces[(x,y)]
                return {-1:'╋',0:'░',1:'█',2:'▒',3:'▓'}.get(piece, str(piece))
        (max_x,max_y) = self.current_board_size
        string = (
          ("╭" + (max_x+1)*"─" + "╮\n")
          + "\n".join(
              "│"
              + "".join(
                  show(x,y)
              for x in range(max_x+1) )
              + "│"
          for y in range(max_y+1) )
          + ("\n╰" + (max_x+1)*"─" + "╯")
        )
        return string

    @property
    def current_player(self):
        return self._current_player

    @property
    def current_direction(self):
        return self._current_direction

    @property
    def current_board_size(self):
        max_x = max(x for (x,_) in self._board_pieces)
        max_y = max(y for (_,y) in self._board_pieces)
        return (max_x,max_y)

    def attempt_move(offset, direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        if not possible_move(offset, direction):
          return False
        if self._current_direction == ANY:
            direction = self._current_direction
        # Modify board
        return True

    def possible_move(offset, direction):
        """Check whether a given move is possible for the current player."""
        if self._current_direction == ANY:
            if direction not in [NORTH,WEST,SOUTH,WEST]:
                return False
            else:
                direction = self._current_direction
        (max_x,max_y) = self.current_board_size
        max_offset = max_x if direction in [EAST,WEST] else max_y
        return 0 <= offset <= max_offset

    def prune(self):
        """Remove all leaves not attached to a log piece from the board."""
        for (x,y) in self._board_pieces:
            any_neighboring_logs = any(self._board[(x+dx,y+dy)] == -1
                                       for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]
                                       if (x+dx,y+dy) in self._board)
            if not any_neighboring_logs:
                self._board_pieces.pop((x,y))
        return

    @staticmethod
    def _make_sequence(players, pieces_per_player, turns_per_player):
        pieces_remaining = [pieces_per_player for _ in range(players)]
        player = 0
        pieces_remaining[player] -= 1
        yield player
        while any(pieces != 0 for pieces in pieces_remaining):
            player = (player + 1) % players
            for _ in range(turns_per_player):
                if pieces_remaining[player] == 0: break
                pieces_remaining[player] -= 1
                yield player

# END   CLASSES


# BEGIN FUNCTIONS
# No functions
# END   FUNCTIONS


# BEGIN MAIN

def main():
    print("hi")

    game = LeavesGame()
    for x in game._turn_sequence:
      print(x)

    print(game)

    print("bye")

if __name__=="__main__": main()

# END   MAIN
