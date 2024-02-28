# BEGIN OUTLINE
"""
TODO :
- Save game using game notation?
- Connected areas count?
"""
# END   OUTLINE


# BEGIN IMPORTS

from collections import Counter # Counting how many pieces of each player present
from enum import Enum # Direction ADT

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
        """Check whether a coordinate is active on the board."""
        return self.pieces.__contains__(coordinate)

    def show(self, get_tile):
        """Print the board as string using a tileset for the piece types."""
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
        """Active (width,height) of the board."""
        max_x = max(x for (x,_) in self.pieces)
        max_y = max(y for (_,y) in self.pieces)
        return (max_x + 1, max_y + 1)

    def pruned(self):
        """Return a copy of board with all leaves not attached to log pieces removed."""
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
        """Return how many pieces of each type are present on the board."""
        return dict(Counter(self.pruned().pieces.values()))

    def realign(self):
        """Normalize the coordinates of all pieces to range from 0 to (board width/height) - 1."""
        min_x = min(x for (x,_) in self.pieces)
        min_y = min(y for (_,y) in self.pieces)
        pieces = self.pieces
        # Fix horizontal misalignment
        if min_x < 0:
            new_pieces = dict()
            for (x,y),piece in pieces.items():
                new_pieces[(x - min_x, y)] = piece
            pieces = new_pieces
        # Fix vertical misalignment
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
        self.reset()

    def reset(self):
        """Reset the state of the game to the beginning."""
        self._board = _Board({ (0,y):-1 for y in range(self._log_pieces) })
        self._remaining_pieces = [self._pieces_per_player for _ in range(self._players)]
        def make_sequence(players, turns_per_player):
            player = 0
            while True:
                for _ in range(turns_per_player):
                    yield player
                player = (player+1) % players
        self._player_sequence = make_sequence(self._players, 2)
        next(self._player_sequence)
        self._current_turn = (next(self._player_sequence), None)
        self._turn_history = []
        return

    @property
    def players(self):
        """How many players are playing the game."""
        return self._players

    @property
    def pieces_per_player(self):
        """How many pieces each player starts the game with."""
        return self._pieces_per_player

    @property
    def board(self):
        """The current game board pieces."""
        return self._board

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
        """The number of turns already played."""
        return (self._players*self._pieces_per_player - sum(self._remaining_pieces))

    @property
    def current_turn_history(self):
        """The turns already played."""
        return '\n'.join(self._turn_history)

    @property
    def remaining_pieces(self):
        """A list of how many pieces each player has left to play."""
        return self._remaining_pieces.copy()

    @property
    def current_board_size(self):
        """Active (width,height) of the board."""
        return self._board.size

    def scores(self):
        """Return how many pieces of each player are present on the board."""
        scores = self._board.counts()
        scores.pop(-1) # Log pieces have id = -1
        return scores

    def compute_winners(self):
        """Compute the winners of the game. Several if there is a draw, none if the game is not over yet."""
        if not self.is_over:
            return []
        scores = self.scores()
        best_score = max(scores.values())
        winners = [player for (player,score) in scores.items() if score == best_score]
        return winners

    def make_move(self, offset, new_direction):
        """Try to make a move for the current player given a line offset and the intended direction."""
        # Abort if move is invalid
        err = self.check_move(offset, new_direction)
        if err:
            raise ValueError(err)
        # Prepare to modify board
        (player,direction) = self._current_turn
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
        # Sequentially move consecutive pieces we find
        moving_piece = player
        while moving_piece is not None:
            (moving_piece, self._board.pieces[(x,y)]) = (self._board.pieces.get((x,y)), moving_piece)
            x += dx
            y += dy
        self._board.realign()
        # Update internal game state
        self._remaining_pieces[player] -= 1
        self._turn_history.append(f"{(new_direction.name[0] if direction is None else '')}{offset+1}") # Game notation not 100% same as in original manual
        try:
            next_player = next(self._player_sequence)
            next_direction = None if next_player != player else Dir((new_direction.value + 1) % 4)
            self._current_turn = (next_player,next_direction)
            # No pieces left = out of turns
            if sum(self._remaining_pieces) == 0:
                raise StopIteration
        except StopIteration:
            self._current_turn = None
        return

    def check_move(self, offset, new_direction):
        """Check whether a given move is possible for the current player given a line offset and the intended direction."""
        # Invalid argument types or game over
        if not isinstance(offset, int):
            return f"invalid offset argument {offset} to make move with"
        elif not isinstance(new_direction, Dir):
            return f"invalid direction argument {new_direction} to make move with"
        elif self.is_over:
            return "game is over, no moves allowed"
        # Check whether chosen direction matches actual direction
        (player,direction) = self._current_turn
        if direction is not None and new_direction != direction:
            return f"invalid move, direction {new_direction} does not match {direction}"
        # Check whether chosen offset is valid into chosen direction
        (w,h) = self._board.size
        max_offset = h if new_direction in [Dir.EAST,Dir.WEST] else w
        if not (0 <= offset < max_offset):
            return f"invalid move, offset is not 0 <= {offset} <= {max_offset} (for {new_direction=})"
        return ""

# END   CLASSES


# BEGIN FUNCTIONS
# No functions
# END   FUNCTIONS


# BEGIN MAIN
# No main
# END   MAIN
