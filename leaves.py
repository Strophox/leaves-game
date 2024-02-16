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

import pygame as pg
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
    def __init__(self, log_pieces=5, players=2, pieces_per_player=10):
        self._log_pieces = log_pieces
        self._players = players
        self._pieces_per_player = pieces_per_player
        # A generator of player IDs
        self._player_sequence = self._produce_sequence()
        # A Player ID and direction, or None
        self._current_turn = (next(self._player_sequence), ANY)
        # A dictionary of board pieces with their coordinates
        self._board_pieces = { (0,y):-1 for y in range(self._log_pieces) }
        self._piecetypes = {
            -1: ("[]","Log"),
            0: ("░░","First player"),
            1: ("██","Second player"),
            2: ("▒▒","Third player"),
            3: ("▓▓","Fourth player"),
        } # TODO handle more cases, ┮┵┾┽

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
    def current_round(self):
        return (1 + len(self._board_pieces) - self._log_pieces)

    @property
    def current_board_size(self):
        return LeavesGame._board_size(self._board_pieces)

    @property
    def current_scores(self):
        pruned_board = LeavesGame._board_pruned(self._board_pieces)
        scores = dict(Counter(pruned_board.values()))
        scores.pop(-1)
        return scores

    def _compute_winner(self):
      scores = self.current_scores
      best_score = max(scores.values())
      if list(scores.values()).count(best_score) == 1:
        return max(scores, key=scores.get)
      else:
        return -1

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

    def str_tree(self):
        return LeavesGame._board_str(self._board_pieces,
                                     lambda p: self._piecetypes[p][0])

    def str_pruned(self):
        return LeavesGame._board_str(LeavesGame._board_pruned(self._board_pieces),
                                     lambda p: self._piecetypes[p][0])

    def make_move(self, offset, direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        err = self.check_move(offset, direction)
        if err:
            raise ValueError(err)
        # Modify board
        (max_x,max_y) = self.current_board_size
        move_direction = direction if self.current_direction == ANY else self.current_direction
        ((x,y),(dx,dy)) = {
            NORTH: ((offset,0),     ( 0, 1)),
            EAST : ((max_x,offset), (-1, 0)),
            SOUTH: ((offset,max_y), ( 0,-1)),
            WEST : ((0,offset),     ( 1, 0)),
        }[move_direction]
        # Skip empty tiles at the beginning
        while (x,y) not in self._board_pieces:
            x += dx
            y += dy
        # Start moving first group of pieces
        moving_piece = self.current_player
        while moving_piece is not None:
            (moving_piece, self._board_pieces[(x,y)]) = (self._board_pieces.get((x,y)), moving_piece)
            x += dx
            y += dy
        # Fix board if moved left or up
        if x < -1 or y < -1:
            (fix_x,fix_y) = (1,0) if x < -1 else (0,1)
            (self._board_pieces, broken_pieces) = (dict(), self._board_pieces)
            for ((x,y),tile) in broken_pieces.items():
                self._board_pieces[(x+fix_x,y+fix_y)] = tile
        # Update internal state of whose turn it is
        try:
            next_player = next(self._player_sequence)
            next_direction = ANY if next_player != self.current_player else (move_direction + 1) % 4
            self._current_turn = (next_player,next_direction)
        except StopIteration:
            self._current_turn = None
        return

    def check_move(self, offset, direction):
        """Check whether a given move is possible for the current player."""
        # Has game ended?
        if self.is_over:
            return "invalid move, game is over"
        # Does the chosen direction matter?
        if self.current_direction != ANY:
            direction = self.current_direction
        # Otherwise, is the chosen direction valid?
        elif direction not in [NORTH,EAST,SOUTH,WEST]:
            print()
            return f"invalid move, {NORTH} <= {direction} <= {WEST} not a valid direction."
        # Move is valid if valid offset into the correct direction
        (max_x,max_y) = self.current_board_size
        max_offset = max_y if direction in [EAST,WEST] else max_x
        if not (0 <= offset <= max_offset):
            return f"invalid move, offset is not 0 <= {offset} <= {max_offset} (for {direction=})"
        return ""

    def run_console(self):
        BAR = "~:--------------------------------------:~"
        W = len(BAR)
        main_text = fixStrs(f"""
            {BAR}
            {centered(W,"Leaves")}
            """)
        while not self.is_over:
            # Show game state
            status_text = fixStrs(
                f"""
                {BAR}
                {centered(W,f"Turn {self.current_round}")}
                """,
                centered(W,boxed(centered(W-4,str(self.str_tree())))),
            )
            print(status_text)
            while True:
                # Let user make valid move
                (sprite,playername) = self._piecetypes[self.current_player]
                playername = f"{sprite} {playername}"
                if self.current_direction == ANY:
                    query_text = fixStrs(
                        f"""
                        {playername}
                        ⟲  *any* direction
                           (e.g. 'N1' = North ↓ in 1st column,
                                 'W4' = West ⟶  in 4th row, etc.)
                        """,
                    )
                    parse = lambda user_input: (
                        int(user_input[1:]) - 1,
                        "NESW".index(user_input[0].upper()) )
                else:
                    query_text = fixStrs(
                        f"""
                        {playername}
                        {["↓ North","⟵  East","↑ South","⟶  West"][self.current_direction]}
                           (e.g. '1' = {dir} in 1st {"column" if self.current_direction in [NORTH,SOUTH] else "row"})
                        """,
                    )
                    parse = lambda user_input: (
                        int(user_input) - 1,
                        "")
                print(query_text)
                try:
                    user_input = input("> ")
                except (KeyboardInterrupt, EOFError):
                    print("Goodbye ~")
                    return
                try:
                    self.make_move(*parse(user_input))
                    break
                except Exception as e:
                    print(f"Oops: {e}")
                    continue
        winner = self._compute_winner()
        if winner != -1:
            (sprite,playername) = self._piecetypes[winner]
            winner_text = centered(W,boxed(centered(W-4,
                                   f"⋆｡ﾟ☁｡ {sprite} {playername} won the game! {sprite} ｡ ﾟ☾｡⋆")))
        else:
            (sprite,_) = self._piecetypes[winner]
            winner_text = centered(W,boxed(centered(W-4,
                                   f"{sprite} It's a Draw! {sprite}")))
        end_text = fixStrs(
            f"""
            {BAR}
            {centered(W,boxed(centered(W-4,str(self.str_tree()))))}
            {BAR}
            {centered(W,"Game Over.")}
            {centered(W,"Pruned tree:")}
            """,
            centered(W,boxed(centered(W-4,str(self.str_pruned())))),
            f"""
            {centered(W,f"Scores: {' - '.join(f'{score} {self._piecetypes[playerid][0]}' for (playerid,score) in self.current_scores.items())}")}
            {winner_text}
            {BAR}
            """,
        )
        print(end_text)

    @staticmethod
    def _board_size(board_pieces):
        max_x = max(x for (x,_) in board_pieces)
        max_y = max(y for (_,y) in board_pieces)
        return (max_x,max_y)

    @staticmethod
    def _board_str(board_pieces, sprite_of):
        def show(x,y):
            """Given a coordinate, return a way to represent the piece there."""
            if (x,y) in board_pieces:
                return sprite_of(board_pieces[(x,y)])
            else:
                return '  '
        (max_x,max_y) = LeavesGame._board_size(board_pieces)
        string = (
            "\n".join(
                "".join(
                    show(x,y)
                for x in range(max_x+1) )
            for y in range(max_y+1) )
        )
        return string

    @staticmethod
    def _board_pruned(board_pieces):
        """Remove all leaves not attached to a log piece from the board."""
        valid_pieces = dict()
        for (x,y) in board_pieces:
            is_log = board_pieces[(x,y)] == -1
            has_neighboring_logs = any(board_pieces[(x+dx,y+dy)] == -1
                                       for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]
                                       if (x+dx,y+dy) in board_pieces)
            if is_log or has_neighboring_logs:
                valid_pieces[(x,y)] = board_pieces[(x,y)]
        return valid_pieces

    def run_pygame(self):
        import pygame
        pygame.init()
        win = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Squarey")
        x = 100
        y = 100
        baddyX = 300
        baddyY = 300
        vel = 6
        baddyVel = 4
        run = True
        def draw_game():
            win.fill((0, 0, 0))
            pygame.draw.rect(win, (0, 0, 255), (x, y, 20, 20))
            pygame.draw.rect(win, (255, 0, 0), (baddyX, baddyY, 40, 40))
            pygame.display.update()

        while run:
            pygame.time.delay(100)

            if baddyX < x - 10:
                baddyX = baddyX + baddyVel
            elif baddyX > x + 10:
                baddyX = baddyX - baddyVel
            elif baddyY < y - 10:
                baddyY = baddyY + baddyVel
            elif baddyY > y + 10:
                baddyY = baddyY - baddyVel
            else:
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                x -= vel

            if keys[pygame.K_RIGHT]:
                x += vel

            if keys[pygame.K_UP]:
                y -= vel

            if keys[pygame.K_DOWN]:
                y += vel

            draw_game()

        pygame.quit()
        return # TODO

# END   CLASSES


# BEGIN FUNCTIONS

def fixStrs(*strings):
    """Remove indent and strip newlines from multiline string."""
    def dedent(string, indent_unit=1):
        lines = string.split('\n')
        indent = min(len(line) - len(line.lstrip()) for line in lines if line)
        if indent_unit != 1:
          indent %= indent_unit
        string = '\n'.join(
            line[indent:] for line in lines
        ).strip('\n')
        return string
    string = '\n'.join(
        pstring for string in strings if (pstring := dedent(string).strip('\n'))
    )
    return string

def boxed(string, spritesheet=None):
    if spritesheet is None:
        spritesheet = "rounded"
    sprites = {
        "square" : " ╶╵└╴─┘┴╷┌│├┐┬┤┼",
        "rounded": " ╶╵╰╴─╯┴╷╭│├╮┬┤┼", # TODO add more / handle better
    }[spritesheet]
    lines = string.split('\n')
    len_max = max(len(line) for line in lines)
    string = (
        f"{sprites[0b1001]}{len_max*sprites[0b0101]}{sprites[0b1100]}\n"
        + "\n".join(
            f"{sprites[0b1010]}{line:<{len(line)-len_max}}{sprites[0b1010]}"
        for line in lines )
        + f"\n{sprites[0b0011]}{len_max*sprites[0b0101]}{sprites[0b0110]}"
    )
    return string

def centered(width, string):
    lines = string.split('\n')
    string = (
        "\n".join(
            f"{line:^{width}}"
        for line in lines )
    )
    return string

# END   FUNCTIONS


# BEGIN MAIN

def main():
    game = LeavesGame(pieces_per_player=2)
    #game = LeavesGame()
    game.run_console()
    return

if __name__=="__main__": main()

# END   MAIN
