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
        self.piecetypes = {
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
    def current_turn(self):
        return (1 + len(self._board_pieces) - self._log_pieces)

    @property
    def total_turns(self):
        return (self._players * self._pieces_per_player)

    @property
    def current_board_size(self):
        return LeavesGame._board_size(self._board_pieces)

    @property
    def current_scores(self):
        pruned_board = LeavesGame._board_pruned(self._board_pieces)
        scores = dict(Counter(pruned_board.values()))
        scores.pop(-1)
        return scores

    def compute_winner(self):
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
                                     lambda p: self.piecetypes[p][0])

    def str_pruned(self):
        return LeavesGame._board_str(LeavesGame._board_pruned(self._board_pieces),
                                     lambda p: self.piecetypes[p][0])

    def make_move(self, offset, direction):
        """Try to make a move for the current player, return True if successful and False otherwise."""
        err = self.check_move(offset, direction)
        if err:
            raise ValueError(err)
        # Modify board
        (max_x,max_y) = self.current_board_size
        ((x,y),(dx,dy)) = {
            NORTH: ((offset,0),     ( 0, 1)),
            EAST : ((max_x,offset), (-1, 0)),
            SOUTH: ((offset,max_y), ( 0,-1)),
            WEST : ((0,offset),     ( 1, 0)),
        }[direction]
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
        self._board_pieces = LeavesGame._board_realigned(self._board_pieces)
        # Update internal state of whose turn it is
        try:
            next_player = next(self._player_sequence)
            next_direction = ANY if next_player != self.current_player else (direction + 1) % 4
            self._current_turn = (next_player,next_direction)
        except StopIteration:
            self._current_turn = None
        return

    def check_move(self, offset, direction):
        """Check whether a given move is possible for the current player."""
        # Has game ended?
        if not isinstance(offset, int) or not isinstance(direction, int):
            return "invalid arguments to function expecting two ints"
        if self.is_over:
            return "invalid move, game is over"
        # Does the chosen direction matter?
        if self.current_direction != ANY and direction != self.current_direction:
            return f"invalid move, direction {direction} != {self.current_direction}"
        # Otherwise, is the chosen direction valid?
        elif direction not in [NORTH,EAST,SOUTH,WEST]:
            return f"invalid move, {NORTH} <= {direction} <= {WEST} not a valid direction"
        # Move is valid if valid offset into the correct direction
        (max_x,max_y) = self.current_board_size
        max_offset = max_y if direction in [EAST,WEST] else max_x
        if not (0 <= offset <= max_offset):
            return f"invalid move, offset is not 0 <= {offset} <= {max_offset} (for {direction=})"
        return ""

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
    def _board_realigned(board_pieces):
        min_x = min(x for (x,_) in board_pieces)
        min_y = min(y for (_,y) in board_pieces)
        # Fix horizontal Misalignment
        if min_x < 0:
            new_board_pieces = dict()
            for (x,y), tile in board_pieces.items():
                  new_board_pieces[(x - min_x, y)] = tile
            board_pieces = new_board_pieces
        # Fix vertical Misalignment
        if min_y < 0:
            new_board_pieces = dict()
            for (x,y), tile in board_pieces.items():
                  new_board_pieces[(x, y - min_y)] = tile
            board_pieces = new_board_pieces
        return board_pieces

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

# END   CLASSES


# BEGIN FUNCTIONS

def boxStr(string, spritesheet=None):
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
            f"{sprites[0b1010]}{line:x^{len_max-len(line)}}{sprites[0b1010]}"
        for line in lines )
        + f"\n{sprites[0b0011]}{len_max*sprites[0b0101]}{sprites[0b0110]}"
    )
    return string

def dedentStr(string, indent_unit=1):
    lines = string.split('\n')
    indent = min(len(line) - len(line.lstrip()) for line in lines if line)
    if indent_unit != 1:
      indent %= indent_unit
    string = (
        '\n'.join(
        line[indent:] for line in lines )
    )
    return string

def alnStr(spec, string):
    string = (
        '\n'.join(
            f"{line:{spec}}"
        for line in string.split('\n') )
    )
    return string

def glueStrs(*strings):
    """Takes several strings/text chunks with individual format specs and:
    - """
    string = (
        '\n'.join(
            line
        for string in strings
        for line in string.split('\n')
        if line and not line.isspace() )
    )
    return string

def run_console(game):
    BAR = "~:--------------------------------------:~"
    W = len(BAR)
    main_text = glueStrs(
        alnStr('', BAR),
        alnStr(f'^{W}', "Leaves"),
    )
    print(main_text)
    while not game.is_over:
        # Show game state
        (sprite,playername) = game.piecetypes[game.current_player]
        playername = f"{sprite} {playername}"
        if game.current_direction == ANY:
            player_text = (
                alnStr(f'^{W}', dedentStr(f"""
                {playername}
                ⟳  *any* direction
                """))
            )
            ps_text = (
                alnStr(f'<', dedentStr(f"""
                (e.g. 'N1' = North ↓ in 1st column,
                      'W4' = West ⟶  in 4th row, etc.)
                """))
            )
            parse = lambda user_input: (
                int(user_input[1:]) - 1,
                "NESW".index(user_input[0].upper()) )
        else:
            direction = ["↓ North","⟵  East","↑ South","⟶  West"][game.current_direction]
            player_text = glueStrs(
                alnStr(f'^{W}', dedentStr(f"""
                {playername}
                {direction}
                """))
            )
            ps_text = (
                alnStr('<', dedentStr(f"""
                (e.g. '1' = {direction} in 1st {"column" if game.current_direction in [NORTH,SOUTH] else "row"})
                """))
            )
            parse = lambda user_input: (
                int(user_input) - 1,
                game.current_direction)
        status_text = glueStrs(
            alnStr('<', BAR),
            alnStr(f'^{W}', f"Turn {game.current_turn}"),
            alnStr(f'^{W}', player_text),
            alnStr(f'^{W}', boxStr(alnStr(f'^{W-4}', game.str_tree()))),
            alnStr('<',ps_text),
        )
        print(status_text)
        while True:
            try:
                user_input = input("> ")
                game.make_move(*parse(user_input))
                break
            except (KeyboardInterrupt, EOFError):
                print("Goodbye")
                return
            except Exception as e:
                print(f"Oops: {e}")
                continue
    winner = game.compute_winner()
    if winner != -1:
        (sprite,playername) = game.piecetypes[winner]
        winner_text = f"⋆｡ﾟ☁｡ {sprite} {playername} won the game! {sprite} ｡ ﾟ☾｡⋆"
    else:
        (sprite,_) = game.piecetypes[winner]
        winner_text = f"{sprite} It's a Draw! {sprite}"
    end_text = glueStrs(
        alnStr('<',BAR),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_tree()))),
        alnStr(f'^{W}',"Game Over."),
        alnStr(f'^{W}',"Pruned tree:"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_pruned()))),
        alnStr(f'^{W}',f"Player scores: {' - '.join(f'{score} {game.piecetypes[playerid][0]}' for (playerid,score) in game.current_scores.items())}"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', winner_text))),
        alnStr(f'^{W}',BAR),
    )
    print(end_text)
    return

def run_pygame(game):
    import colortools as ct
    import pygame
    pygame.init()
    init = True
    win = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Leaves")
    font = pygame.font.SysFont("monospace", 0) # TODO fix size
    playercols = [ct.PINK,ct.MINT,ct.COLORS['earth']]

    # Main fetch-evaluate-draw gameloop
    running = True
    while running:
        pygame.time.wait(32)

        # Process events
        events = []
        sentinels = [pygame.VIDEORESIZE,pygame.MOUSEBUTTONDOWN]
        pygame_events = pygame.event.get()
        pygame.key.get_mods()
        for event in pygame_events:
            if event.type in sentinels:
                events.append(event.type)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and pygame.KMOD_CTRL:
                game = LeavesGame()
            if (event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN and event.key == pygame.K_c and pygame.KMOD_CTRL):
                running = False

        # Set variables based on game state
        if game.is_over:
            playercol = ct.WHITE
        else:
            playercol = playercols[game.current_player]

        # Figure out basic margin for board drawing
        # -> m(x|y)(0|1) are the start/end coordinates for the margin
        (W,H) = pygame.display.get_surface().get_size()
        (gameW,gameH) = game.current_board_size
        (gameW,gameH) = (gameW+1,gameH+1)
        fraction = 0.75
        win_mrg = int( min(W,H)/2 * (1-fraction) )
        ((mx0,my0), (mx1,my1)) = ((win_mrg,win_mrg), (W-win_mrg,H-win_mrg))

        # Figure out exact frame within which to draw game
        # -> f(x|y)(0|1) are the start/end coordinates for the game board frame
        # Game board has wider aspect ratio than allowed frame
        if ((mx1-mx0)/(my1-my0)) <= gameW/gameH:
            sidemrg = int( ((my1-my0) - gameH * (mx1-mx0)/gameW) / 2 )
            ((fx0,fy0), (fx1,fy1)) = ((mx0,my0+sidemrg), (mx1,my1-sidemrg))
        # Game board has lower aspect ratio than allowed frame
        elif ((mx1-mx0)/(my1-my0)) > gameW/gameH:
            sidemrg = int( ((mx1-mx0) - gameW * (my1-my0)/gameH) / 2 )
            ((fx0,fy0), (fx1,fy1)) = ((mx0+sidemrg,my0), (mx1-sidemrg,my1))

        """# Draw debug.
        pygame.draw.rect(win, ct.RGB_RED, (mx0-1,my0-1, 1,1))
        pygame.draw.rect(win, ct.RGB_GREEN, (mx1,my0-1, 1,1))
        pygame.draw.rect(win, ct.RGB_BLUE, (mx0-1,my1, 1,1))
        pygame.draw.rect(win, ct.RGB_YELLOW, (mx1,my1, 1,1))
        pygame.draw.rect(win, ct.RED, (fx0-2,fy0-2, 2,2))
        pygame.draw.rect(win, ct.GREEN, (fx1,fy0-2, 2,2))
        pygame.draw.rect(win, ct.BLUE, (fx0-2,fy1, 2,2))
        pygame.draw.rect(win, ct.YELLOW, (fx1,fy1, 2,2))"""

        # Process mouse
        (msx,msy) = pygame.mouse.get_pos()
        if fy0 <= msy <= fy1 and (msx <= fx0 or fx1 <= msx):
            sel_line = int((msy-fy0) / (fy1-fy0) * gameH)
            sel_dir = WEST if msx <= fx0 else EAST
        elif fx0 <= msx <= fx1 and (msy <= fy0 or fy1 <= msy):
            sel_line = int((msx-fx0) / (fx1-fx0) * gameW)
            sel_dir = NORTH if msy <= fy0 else SOUTH
        else:
            sel_line = None
            sel_dir = None

        # Process mouse click
        if pygame.MOUSEBUTTONDOWN in events:
            match game.check_move(sel_line,sel_dir):
                case "":
                    game.make_move(sel_line,sel_dir)
                case err:
                    print(f"uh: {err}")

        # Draw background
        bgcol = ct.mix(ct.BLACK,playercol,1/8)
        win.fill(bgcol)

        # Draw selected line
        tileSz = int((fx1-fx0) / gameW)
        barcol1 = ct.mix(bgcol, ct.mix(ct.WHITE,playercol,2/8), 0.25)
        barcol2 = ct.mix(bgcol, ct.mix(ct.WHITE,playercol,2/8), 0.4)
        rate = 2500
        t = pygame.time.get_ticks()%rate/rate
        barcol = ct.interpolate([barcol1,barcol2,barcol1],t)
        valid_move = game.check_move(sel_line,sel_dir) == ""
        if sel_dir in [NORTH,SOUTH] and valid_move:
            pygame.draw.rect(win, barcol, (fx0+tileSz*sel_line,0, tileSz,H))
        elif sel_dir in [EAST,WEST] and valid_move:
            pygame.draw.rect(win, barcol, (0,fy0+tileSz*sel_line, W,tileSz))
        else:
            pass

        # Draw tiles
        for (px,py),piecetype in game._board_pieces.items():
            (x,y) = (fx0 + px*tileSz, fy0 + py*tileSz)
            frac = 0.9
            if piecetype == -1:
                pygame.draw.rect(win, ct.ORANGE, (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))
                pygame.draw.rect(win, playercols[piecetype], (x+tileSz*(1-frac**2)/2,y+tileSz*(1-frac**2)/2, tileSz*frac**2,tileSz*frac**2))
            else:
                pygame.draw.rect(win, playercols[piecetype], (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))

        # Draw text
        if game.is_over:
            winner = game.compute_winner()
            if winner == -1:
                fontcol = ct.mix(ct.WHITE,ct.BLACK,2/8)
                win.blit(
                  font.render(f"It's a draw!",True,fontcol),
                  (win_mrg/ratio,win_mrg/ratio)
                )
            else:
                fontcol = ct.mix(ct.WHITE,playercols[winner],8/8)
                win.blit(
                  font.render(f"Player {winner} wins!",True,fontcol),
                  (win_mrg/ratio,win_mrg/ratio)
                )
        else:
            ratio = 5
            if pygame.VIDEORESIZE in events or init:
                font = pygame.font.SysFont("monospace", round(win_mrg/ratio))
            fontcol = ct.mix(ct.WHITE,playercol,2/8)
            win.blit(
              font.render(f"Turn {game.current_turn} / {game.total_turns}",True,fontcol),
              (win_mrg/ratio,win_mrg*1/ratio)
            )
            win.blit(
              font.render(f"Player {game.current_player}",True,fontcol),
              (win_mrg/ratio,win_mrg*2/ratio)
            )
            directionname = ["↓ North","⟵  East","↑ South","⟶  West","⟳ *any*"][game.current_direction]
            win.blit(
              font.render(f"Direction: {directionname}",True,fontcol),
              (win_mrg/ratio,win_mrg*3/ratio)
            )

        # End stage:
        # Update display immediately and re-enter loop
        pygame.display.update()
        init = False

    # Cleanup
    pygame.quit()
    return

# END   FUNCTIONS


# BEGIN MAIN

def main():
    #game = LeavesGame(pieces_per_player=2)
    game = LeavesGame()
    run_console(game)
    run_pygame(game)
    return

if __name__=="__main__": main()

# END   MAIN
