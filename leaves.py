# BEGIN OUTLINE
"""
TODO :
- Save game using game notation?
- Connected areas count?
"""
# END   OUTLINE


# BEGIN IMPORTS

from collections import Counter # Counting how many pieces of each player
from enum import Enum

# END   IMPORTS


# BEGIN CONSTANTS

# Directions

# END   CONSTANTS


# BEGIN DECORATORS
# No decorators
# END   DECORATORS


# BEGIN CLASSES

class Dir(Enum):
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

class _Board:
    def __init__(self, pieces):
        self.pieces = pieces

    def __contains__(self, coordinate):
        return self.pieces.__contains__(coordinate)

    def show(self, get_tile):
        (w,h) = self.size
        string = (
            "\n".join(
                "".join(
                    get_tile(self.pieces.get((x,y)))
                for x in range(w) )
            for y in range(h) )
        )
        return string

    @property
    def size(self):
        max_x = max(x for (x,_) in self.pieces)
        max_y = max(y for (_,y) in self.pieces)
        return (max_x + 1, max_y + 1)

    def pruned(self):
        """Remove all leaves not attached to a log piece from the board."""
        def is_log(x,y):
            return self.pieces[(x,y)] == -1
        def has_log_neighbor(x,y):
           return any(is_log(x+dx,y+dy)
                      for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]
                      if (x+dx,y+dy) in self.pieces)
        unpruned_pieces = dict()
        for (x,y),piece in self.pieces.items():
            if is_log(x,y) or has_log_neighbor(x,y):
                unpruned_pieces[(x,y)] = piece
        return _Board(unpruned_pieces)

    def counts(self):
        return dict(Counter(self.pruned().pieces.values()))

    def realign(self):
        min_x = min(x for (x,_) in self.pieces)
        min_y = min(y for (_,y) in self.pieces)
        pieces = self.pieces
        # Fix horizontal Misalignment
        if min_x < 0:
            new_pieces = dict()
            for (x,y),piece in pieces.items():
                new_pieces[(x - min_x, y)] = piece
            pieces = new_pieces
        # Fix vertical Misalignment
        if min_y < 0:
            new_pieces = dict()
            for (x,y),piece in pieces.items():
                  new_pieces[(x, y - min_y)] = piece
            pieces = new_pieces
        self.pieces = pieces
        return None

class Game:
    def __init__(self, log_pieces=5, players=2, pieces_per_player=10):
        self._log_pieces = log_pieces
        self._players = players
        self._pieces_per_player = pieces_per_player
        self._remaining_pieces = [pieces_per_player for _ in range(players)]
        def make_sequence(players, turns_per_player):
            player = 0
            while True:
                for _ in range(turns_per_player):
                    yield player
                player = (player+1) % players
        self._player_sequence = make_sequence(players, 2)
        next(self._player_sequence)
        self._current_turn = (next(self._player_sequence), None)
        self._board = _Board({ (0,y):-1 for y in range(log_pieces) })

    @property
    def players(self):
        """How many players are playing the game."""
        return self._players

    @property
    def pieces_per_player(self):
        """How many pieces each player starts with."""
        return self._pieces_per_player

    @property
    def is_over(self):
        """Whether a round of playing the game is finished."""
        return (self._current_turn is None)

    @property
    def current_turn(self):
        """Integer ID of the current player and ID of their direction."""
        return self._current_turn

    @property
    def current_turn_number(self):
        """Integer ID of the current player and ID of their direction."""
        return (self._players*self._pieces_per_player - sum(self._remaining_pieces))

    @property
    def remaining_pieces(self):
        """"""
        return self._remaining_pieces.copy()

    @property
    def current_board_size(self):
        return self._board.size

    def scores(self):
        scores = self._board.counts()
        scores.pop(-1) # Log pieces have id = -1
        return scores

    def compute_winners(self):
        if not self.is_over:
            return []
        scores = self.scores()
        best_score = max(scores.values())
        winners = [player for (player,score) in scores.items() if score == best_score]
        return winners

    def str_board(self, get_tile, pruned=False):
        board = self._board.pruned() if pruned else self._board
        string = board.show(get_tile)
        return string

    def make_move(self, offset, new_direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        err = self.check_move(offset, new_direction)
        if err:
            raise ValueError(err)
        (player,direction) = self._current_turn
        # Modify board
        (w,h) = self._board.size
        ((x,y),(dx,dy)) = {
            Dir.NORTH: ((offset,0),   ( 0, 1)),
            Dir.EAST : ((w-1,offset), (-1, 0)),
            Dir.SOUTH: ((offset,h-1), ( 0,-1)),
            Dir.WEST : ((0,offset),   ( 1, 0)),
        }[new_direction]
        # Skip empty tiles at the beginning
        while (x,y) not in self._board:
            x += dx
            y += dy
        # Start moving first group of pieces
        moving_piece = player
        while moving_piece is not None:
            (moving_piece, self._board.pieces[(x,y)]) = (self._board.pieces.get((x,y)), moving_piece)
            x += dx
            y += dy
        self._board.realign()
        # Update internal state of whose turn it is
        try:
            next_player = next(self._player_sequence)
            next_direction = None if next_player != player else Dir((new_direction.value + 1) % 4)
            self._remaining_pieces[self._current_turn[0]] -= 1
            self._current_turn = (next_player,next_direction)
            if sum(self._remaining_pieces) == 0:
                raise StopIteration
        except StopIteration:
            self._current_turn = None
        return

    def check_move(self, offset, new_direction):
        """Check whether a given move is possible for the current player."""
        # Has game ended?
        if not isinstance(offset, int):
            return f"invalid offset argument {offset} to make move with"
        elif not isinstance(new_direction, Dir):
            return f"invalid direction argument {new_direction} to make move with"
        elif self.is_over:
            return "game is over, no moves allowed"
        # Does the chosen direction matter?
        (player,direction) = self._current_turn
        if direction is not None and new_direction != direction:
            return f"invalid move, direction {new_direction} does not match {direction}"
        # Otherwise, is the chosen direction valid?
        elif new_direction not in [Dir.NORTH,Dir.EAST,Dir.SOUTH,Dir.WEST]:
            return f"invalid move, {Dir.NORTH} <= {new_direction} <= {Dir.WEST} not a valid direction"
        # Move is valid if valid offset into the correct direction
        (w,h) = self._board.size
        max_len = h if new_direction in [Dir.EAST,Dir.WEST] else w
        if not (0 <= offset < max_len):
            return f"invalid move, offset is not 0 <= {offset} <= {max_len} (for {new_direction=})"
        return ""

# END   CLASSES


# BEGIN FUNCTIONS
# No functions
# END   FUNCTIONS


# BEGIN MAIN
# No main
# END   MAIN
