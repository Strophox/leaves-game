# BEGIN OUTLINE
"""
If you want to recap the rules:
- place from four directions, push 1 tile
- no placing in the middle of a row
- gaps shrink
- 90 degrees rule
- ABBAABB… turns
+ 5 logs, 10 green, 10 red

TODO :
- Improve main menu in console?
- Save game using game notation?
- Implement pygame interface
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

    def __str__(self):
        def show(x,y):
            """Given a coordinate, return a way to represent the piece there."""
            if (x,y) not in self._board_pieces:
                return ' '
            else:
                piece = self._board_pieces[(x,y)]
                return {-1:'╋',0:'░',1:'█',2:'▒',3:'▓'}.get(piece, str(piece))
        (max_x,max_y) = self.compute_board_size()
        string = (
            "\n".join(
                "".join(
                    show(x,y)
                for x in range(max_x+1) )
            for y in range(max_y+1) )
        )
        return string

    @property
    def is_over(self):
        return (self._current_turn is None)

    @property
    def current_player(self):
        return (None if self.is_over else self._current_turn[0])

    @property
    def current_direction(self):
        return (None if self.is_over else self._current_turn[1])

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

    def attempt_move(self, offset, direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        if not self.check_move(offset, direction):
            return False
        # Modify board
        (max_x,max_y) = self.compute_board_size()
        move_direction = direction if self.current_direction == ANY else self.current_direction
        ((x,y),(dx,dy)) = {
            NORTH: ((offset,max_y), ( 0, 1)),
            EAST : ((0,offset),     ( 1, 0)),
            SOUTH: ((offset,0),     ( 0,-1)),
            WEST : ((offset,max_x), (-1, 0)),
        }[move_direction]
        # Skip empty tiles at the beginning
        print(self._board_pieces)
        while (x,y) not in self._board_pieces:
            print(f"{(x,y)} ain't it")
            x += dx
            y += dy
        # Start moving first group of pieces
        moving_piece = self.current_player
        while moving_piece != None:
            (moving_piece, self._board_pieces[(x,y)]) = (self._board_pieces.get((x,y)), moving_piece)
            x += dx
            y += dy
        # Fix board if moved left or up
        if x < -1 or y < -1:
            (fix_x,fix_y) = (1,0) if x < -1 else (0,1)
            (self._board_pieces, broken_pieces) = (dict(), self._board_pieces)
            for ((x,y),tile) in self._board_pieces:
                self._board_pieces[(x+fix_x,y+fix_y)] = tile
        # Update internal state of whose turn it is
        try:
            next_player = next(self._player_sequence)
            next_direction = ANY if next_player != self.current_player else (self.current_direction + 1) % 4
            self._current_turn = (next_player,next_direction)
        except StopIteration:
            self._current_turn = None
        return True

    def check_move(self, offset, direction):
        """Check whether a given move is possible for the current player."""
        # Has game ended?
        if self.is_over:
            print("Check: Game Over.")
            return False
        # Does the chosen direction matter?
        if self.current_direction != ANY:
            direction = self.current_direction
        # Otherwise, is the chosen direction valid?
        elif direction not in [NORTH,EAST,SOUTH,WEST]:
            print(f"Check: {direction=} not in {[NORTH,WEST,SOUTH,WEST]}.")
            return False
        # Move is valid if valid offset into the correct direction
        (max_x,max_y) = self.compute_board_size()
        max_offset = max_x if direction in [EAST,WEST] else max_y
        if not (0 <= offset <= max_offset):
            print(f"Check: not (0 <= {offset=} <= {max_offset} for {direction=}.")
        return True

    def run_console(self):
        main_text = fixStr("""
            ~:--------------------------------------:~
                             Leaves
            """)
        while not self.is_over:
            # Show game state
            print("~:--------------------------------------:~")
            print(boxed(str(self)))
            # Let user make valid move
            player = ["First","Second"][self.current_player]
            direction = ["North","East","South","West","Any direction"][self.current_direction]
            if self.current_direction == ANY:
                print(fixStr(f"""
                    Current turn: {player} Player moves {direction}.
                    Enter initial of cardinal direction
                    and line offset on board (from top left)
                    (e.g. 'N1' = move North in 1st column,
                          'W4' = move West  in 4th row)
                    """))
            else:
                print(fixStr(f"""
                    Current turn: {player} Player moves {direction}.
                    Enter line offset on board (from top left)
                    (e.g. '1' = move {direction} in 1st column,
                          '4' = move {direction} in 4th row)
                    """))
            while True:
                user_input = input("> ")
                assert self.attempt_move("NESW".index(user_input[0]),int(user_input[1:]))
                try:
                    assert self.attempt_move("NESW".index(user_input[0])-1,int(user_input[1:]))
                    print("success")
                    break
                    print("imposibile")
                except Exception as e: print(f"Error: {e}")

    def run_pygame(self):
        return # TODO

# END   CLASSES


# BEGIN FUNCTIONS

def fixStr(string, indent_unit=1):
    """Remove indent and strip newlines from multiline string."""
    lines = string.split('\n')
    indent = min(len(line) - len(line.lstrip()) for line in lines if line)
    if indent_unit != 1:
      indent %= indent_unit
    return '\n'.join(line[indent:] for line in lines).strip('\n')

def boxed(string,rounded=False): # TODO
        lines = string.split('\n')
        len_max = max(len(line) for line in lines)
        string = (
            ("╭" + len_max*"─" + "╮\n")
            + "\n".join(
                f"│{line:<{len(line)-len_max}}│"
            for line in lines )
            + ("\n╰" + len_max*"─" + "╯")
        )
        return string

# END   FUNCTIONS


# BEGIN MAIN

def main():
    print("hi")

    game = LeavesGame()
    game.run_console()

    print("bye")

if __name__=="__main__": main()

# END   MAIN
