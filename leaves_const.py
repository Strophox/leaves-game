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

"""

            direction_dict = {
                0: "↓ North",
                1:  "⟵  East",
                2: "↑ South",
                3:  "⟶  West",
            }
            any_dir_text = "any direction*"
"""

ANY   = None
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

# END   CONSTANTS


# BEGIN DECORATORS
# No decorators
# END   DECORATORS


# BEGIN CLASSES

class LeavesBoard:
    def __init__(self, pieces):
        self._pieces = pieces

    def __contains__(self, coordinate):
        return self._pieces.__contains__(coordinate)

    def show(self, tilemap):
        (w,h) = self.size
        string = (
            "\n".join(
                "".join(
                    tilemap(self._pieces.get((x,y)))
                for x in range(w) )
            for y in range(h) )
        )
        return string

    @property
    def size(self):
        max_x = max(x for (x,_) in self._pieces)
        max_y = max(y for (_,y) in self._pieces)
        return (max_x + 1, max_y + 1)

    def pruned(self):
        """Remove all leaves not attached to a log piece from the board."""
        def is_log(x,y):
            return self._pieces[(x,y)] == -1
        def has_log_neighbor(x,y):
           return any(is_log(x+dx,y+dy)
                      for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]
                      if (x+dx,y+dy) in self._pieces)
        unpruned_pieces = dict()
        for (x,y),piece in self._pieces.items():
            if is_log(x,y) or has_log_neighbor(x,y):
                unpruned_pieces[(x,y)] = piece
        return LeavesBoard(unpruned_pieces)

    def counts(self):
        return dict(Counter(self.pruned()._pieces.values()))

    def realign(self):
        min_x = min(x for (x,_) in self._pieces)
        min_y = min(y for (_,y) in self._pieces)
        pieces = self._pieces
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
        self._pieces = pieces
        return None

class LeavesGame:
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
        self._current_turn = (next(self._player_sequence), ANY)
        self._board = LeavesBoard({ (0,y):-1 for y in range(log_pieces) })

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

    def str_board(self, pruned=False, tilemap=None):
        if tilemap is None:
            tilemap = {None: '  ', -1: '[]', 0: '░░', 1: '██'}.get
        board = self._board.pruned() if pruned else self._board
        string = board.show(tilemap)
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
            NORTH: ((offset,0),   ( 0, 1)),
            EAST : ((w-1,offset), (-1, 0)),
            SOUTH: ((offset,h-1), ( 0,-1)),
            WEST : ((0,offset),   ( 1, 0)),
        }[new_direction]
        # Skip empty tiles at the beginning
        while (x,y) not in self._board:
            x += dx
            y += dy
        # Start moving first group of pieces
        moving_piece = player
        while moving_piece is not None:
            (moving_piece, self._board._pieces[(x,y)]) = (self._board._pieces.get((x,y)), moving_piece)
            x += dx
            y += dy
        self._board.realign()
        # Update internal state of whose turn it is
        try:
            next_player = next(self._player_sequence)
            next_direction = ANY if next_player != player else (new_direction + 1) % 4
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
        if not isinstance(offset, int) or not isinstance(new_direction, int):
            return "invalid arguments to make move with"
        if self.is_over:
            return "game is over, no moves allowed"
        # Does the chosen direction matter?
        (player,direction) = self._current_turn
        if direction != ANY and new_direction != direction:
            return f"invalid move, direction {new_direction} does not match {direction}"
        # Otherwise, is the chosen direction valid?
        elif new_direction not in [NORTH,EAST,SOUTH,WEST]:
            return f"invalid move, {NORTH} <= {new_direction} <= {WEST} not a valid direction"
        # Move is valid if valid offset into the correct direction
        (w,h) = self._board.size
        max_len = h if new_direction in [EAST,WEST] else w
        if not (0 <= offset < max_len):
            return f"invalid move, offset is not 0 <= {offset} <= {max_len} (for {new_direction=})"
        return ""

# END   CLASSES


# BEGIN FUNCTIONS

def boxStr(string, style=None):
    if style is None:
        style = "rounded"
    sprites = {
        "square" : " ╶╵└╴─┘┴╷┌│├┐┬┤┼",
        "rounded": " ╶╵╰╴─╯┴╷╭│├╮┬┤┼", # TODO add more / handle better
    }[style]
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
    PIECETYPES = {
        None: (' ',"(empty)"),
        -1: ("[]","Log"),
        0: ("░░","First player"),
        1: ("██","Second player"),
        2: ("▒▒","Third player"),
        3: ("▓▓","Fourth player"),
    }
    tilemap = lambda piece: PIECETYPES[piece][0]
    BAR = "~:-------------------------------------------:~"
    W = len(BAR)
    text_title = glueStrs(
        alnStr('', BAR),
        alnStr(f'^{W}', dedentStr(f"""
        ,_,   ,____   __   ,_    ,,____  ___
        | |   | |_   / /\  \ \  / | |_  ( (`
        |_|__ |_|__ /_/--\  \_\/  |_|__ _)_)
        """)),
        alnStr(f'^{W}', "Leaves - abstract strategy game."),
    )
    print(text_title)
    while not game.is_over:
        (player,direction) = game.current_turn
        # Show game state
        (psprite,pname) = PIECETYPES[player]
        text_player = f"{psprite} {pname}"
        if direction == ANY:
            text_turn = (
                alnStr(f'^{W}', dedentStr(f"""
                {text_player}
                ⟳  *any* direction
                """))
            )
            text_ex = (
                alnStr(f'<', dedentStr(f"""
                -> e.g. 'N1' = North ↓ in 1st column,
                        'W4' = West ⟶  in 4th row, etc.)
                """))
            )
            parse = lambda user_input: (
                int(user_input[1:]) - 1,
                "NESW".index(user_input[0].upper()) )
        else:
            text_dir = {
                NORTH: "↓ North",
                EAST:  "⟵  East",
                SOUTH: "↑ South",
                WEST:  "⟶  West",
                ANY:   "⟳ *any direction*"
            }[direction]
            text_turn = glueStrs(
                alnStr(f'^{W}', dedentStr(f"""
                {text_player}
                {text_dir}
                """))
            )
            text_ex = (
                alnStr('<', dedentStr(f"""
                -> e.g. '1' = {direction} in 1st {"column" if direction in [NORTH,SOUTH] else "row"})
                """))
            )
            parse = lambda user_input: (
                int(user_input) - 1,
                direction)
        text_status = glueStrs(
            alnStr('<', BAR),
            alnStr(f'^{W}', f"Turn {game.current_turn_number}"),
            alnStr(f'^{W}', text_turn),
            alnStr(f'^{W}', boxStr(alnStr(f'^{W-4}', game.str_board()))),
            alnStr(f'^{W}', f"[pieces left: {' - '.join(f'{remaining} {PIECETYPES[player][0]}' for (player,remaining) in enumerate(game.remaining_pieces))}]"),
            alnStr('<',(text_ex if game.current_turn_number <= 3 else '')),
        )
        print(text_status)
        while True:
            try:
                user_input = input("> ")
                move = parse(user_input)
                game.make_move(*move)
                break
            except (KeyboardInterrupt, EOFError):
                print("Goodbye")
                return
            except Exception as e:
                print(f"Oops: {e}")
                continue
    winners = game.compute_winners()
    if len(winners) == 1:
        (psprite,pname) = PIECETYPES[winners[0]]
        text_winners = f"⋆｡ﾟ☁｡ {psprite} {pname} won the game! {psprite} ｡ ﾟ☾｡⋆"
    else:
        text_winners = f"It's a Draw between {', '.join(PIECETYPES[winner][1] for winner in winners)}!"
    end_text = glueStrs(
        alnStr('<',BAR),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_board()))),
        alnStr(f'^{W}',"Game Over."),
        alnStr(f'^{W}',"Resulting pruned tree:"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_board(pruned=True)))),
        alnStr(f'^{W}',f"Player scores: {' - '.join(f'{score} {PIECETYPES[player][0]}' for (player,score) in enumerate(game.scores()))}"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', text_winners))),
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
    playercols = [
        ct.mix(ct.PINK,ct.VIOLET,0.25),
        ct.mix(ct.MINT,ct.MOSS,0.25),
        ct.COLORS['earth']
    ]

    # Main fetch-evaluate-draw gameloop
    running = True
    while running:
        pygame.time.wait(32)

        # Process events
        events = []
        sentinels = [pygame.VIDEORESIZE, pygame.MOUSEBUTTONDOWN]
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
            (player,direction) = game.current_turn
            playercol = playercols[player]

        pygame.display.set_caption(f"Leaves - Turn {game.current_turn_number}")

        # Figure out basic margin for board drawing
        (W,H) = pygame.display.get_surface().get_size()
        (gameW,gameH) = game.current_board_size
        fraction = 0.75
        win_mrg = int( min(W,H)/2 * (1-fraction) )
        ((mx0,my0), (mx1,my1)) = ((win_mrg,win_mrg), (W-win_mrg,H-win_mrg))
        # -> m(x|y)(0|1) are the start/end coordinates for the margin

        # Figure out exact frame within which to draw game
        # Game board has wider aspect ratio than allowed frame
        if ((mx1-mx0)/(my1-my0)) <= gameW/gameH:
            sidemrg = int( ((my1-my0) - gameH * (mx1-mx0)/gameW) / 2 )
            ((fx0,fy0), (fx1,fy1)) = ((mx0,my0+sidemrg), (mx1,my1-sidemrg))
        # Game board has lower aspect ratio than allowed frame
        elif ((mx1-mx0)/(my1-my0)) > gameW/gameH:
            sidemrg = int( ((mx1-mx0) - gameW * (my1-my0)/gameH) / 2 )
            ((fx0,fy0), (fx1,fy1)) = ((mx0+sidemrg,my0), (mx1-sidemrg,my1))
        # -> f(x|y)(0|1) are the start/end coordinates for the game board frame

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
        for (px,py),piecetype in game._board._pieces.items():
            (x,y) = (fx0 + px*tileSz, fy0 + py*tileSz)
            frac = 0.9
            if piecetype == -1:
                pygame.draw.rect(win, ct.mix(ct.ORANGE,ct.GRAY,0.8), (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))
                pygame.draw.rect(win, playercols[piecetype], (x+tileSz*(1-frac**2)/2,y+tileSz*(1-frac**2)/2, tileSz*frac**2,tileSz*frac**2))
            else:
                pygame.draw.rect(win, playercols[piecetype], (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))

        # Draw text
        if game.is_over:
            winners = game.compute_winners()
            if len(winners) == 1:
                fontcol = ct.mix(ct.WHITE,playercols[winners[0]],8/8)
                text_winners = f"Player {1+winners[0]} wins!"
            else:
                fontcol = ct.mix(ct.WHITE,ct.BLACK,2/8)
                text_winners = f"It's a Draw between {', '.join(f'Player {1+winner}' for winner in winners)}!"
            win.blit(
                font.render(text_winners,True,fontcol),
                (win_mrg/ratio,win_mrg/ratio)
            )
        else:
            ratio = 5
            if (pygame.VIDEORESIZE in events) or init:
                font = pygame.font.SysFont("monospace", round(win_mrg/ratio))
            fontcol = ct.mix(ct.WHITE,playercol,2/8)
            directionname = {
                NORTH: "↓ North",
                EAST:  "⟵  East",
                SOUTH: "↑ South",
                WEST:  "⟶  West",
                ANY:   "⟳ *any direction*"
            }[direction]
            win.blit(
                font.render(f"Player {1+player}",True,fontcol),
                (win_mrg/ratio,win_mrg*1/ratio)
            )
            win.blit(
                font.render(f"Direction: {directionname}",True,fontcol),
                (win_mrg/ratio,win_mrg*2/ratio)
            )
            win.blit(
                font.render(f"Pieces left: {', '.join(f'Player {1+player} = {remaining}' for (player,remaining) in enumerate(game.remaining_pieces))}",True,fontcol),
                (win_mrg/ratio,fy1+win_mrg*3/ratio)
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
    game = LeavesGame(pieces_per_player=2)
    #game = LeavesGame()
    run_console(game)
    run_pygame(game)
    return

if __name__=="__main__": main()

# END   MAIN
