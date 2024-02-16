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

from collections import Counter # Counting how many pieces of each player

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
        self._log_pieces = 5
        self._players = 2
        self._pieces_per_player = 10
        # A generator of player IDs
        self._player_sequence = self._produce_sequence()
        # A Player ID and direction, or None
        self._current_turn = (next(self._player_sequence), ANY)
        # A dictionary of board pieces with their coordinates
        self._board_pieces = { (0,y):-1 for y in range(self._log_pieces) }

    def __repr__(self):
        def show(x,y):
            """Given a coordinate, return a way to represent the piece there."""
            if (x,y) not in self._board_pieces:
                return ' '
            else:
                piece = self._board_pieces[(x,y)]
                return {-1:'╋',0:'░',1:'█',2:'▒',3:'▓'}.get(piece, str(piece))
        (max_x,max_y) = self.compute_board_size()
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
        return (self._current_turn[0] if self._current_turn else None)

    @property
    def current_direction(self):
        return (self._current_turn[1] if self._current_turn else None)

    @property
    def current_turn_number(self):
        return (1 + len(self._board_pieces) - self._log_pieces)

    def compute_board_size(self):
        max_x = max(x for (x,_) in self._board_pieces)
        max_y = max(y for (_,y) in self._board_pieces)
        return (max_x,max_y)

    def compute_scores(self):
        scores = Counter(self._pruned().values())
        scores.pop(-1)
        return scores

    def _produce_sequence(self, players=None, pieces_per_player=None):
        if players is None:
            players = self._players
        if pieces_per_player is None:
            pieces_per_player = self._pieces_per_player
        turns_per_player = 2
        player = 0
        pieces_remaining = [pieces_per_player for _ in range(players)]
        pieces_remaining[player] -= 1
        yield player
        while any(pieces != 0 for pieces in pieces_remaining):
            player = (player + 1) % players
            for _ in range(turns_per_player):
                if pieces_remaining[player] == 0: break
                pieces_remaining[player] -= 1
                yield player

    def attempt_move(self, offset, direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        if not check_move(offset, direction):
            return False
        # Modify board
        current_piece = self.current_player
        match (direction if self.current_direction == ANY else self.current_direction):
        case "NORTH":
            pass # TODO
        case "EAST":
            pass
        case "SOUTH":
            pass
        case "WEST":
            pass
        try:
            next_player = next(self._turn_sequence)
            self._current_turn =
        except StopIteration:
            self._current_turn = None
        return True

    def check_move(self, offset, direction):
        """Check whether a given move is possible for the current player."""
        # Has game ended?
        if self._current_turn is None:
            return False
        # Is the direction forced?
        if self.current_direction != ANY:
            direction = self.current_direction
        # Otherwise, is the chosen direction valid?
        elif direction not in [NORTH,WEST,SOUTH,WEST]:
            return False
        # Move is valid if valid offset into the correct direction
        (max_x,max_y) = self.compute_board_size()
        max_offset = max_x if direction in [EAST,WEST] else max_y
        return (0 <= offset <= max_offset)

    def _pruned(self):
        """Remove all leaves not attached to a log piece from the board."""
        valid_pieces = self._board_pieces.copy()
        for (x,y) in self._board_pieces:
            #is_log_itself = self._board_pieces[(x+dx,y+dy)] == -1
            has_neighboring_logs = any(self._board_pieces[(x+dx,y+dy)] == -1
                                       for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]
                                       if (x+dx,y+dy) in self._board_pieces)
            if not has_neighboring_logs:
                valid_pieces.pop((x,y))
        return valid_pieces

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
