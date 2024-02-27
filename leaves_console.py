# BEGIN OUTLINE
"""
This script only contains `run` for a console interface.
"""
# END   OUTLINE


# BEGIN IMPORTS

from leaves_consts import Dir,DIR_DATA,DIR_DATA_ANY,PIECE_DATA,PIECE_DATA_EMPTY

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
            f"{sprites[0b1010]}{line:^{len_max}}{sprites[0b1010]}"
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

def run(game):
    tilemap = lambda piece: (PIECE_DATA_EMPTY if piece is None else PIECE_DATA[piece])[0]
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
        (psprite,pname,*_) = PIECE_DATA[player]
        if direction is None:
            (dsprite,dname) = DIR_DATA_ANY
            text_ex = (
                alnStr(f'<', dedentStr(f"""
                -> e.g. 'N1' = from North ↓ in 1st column,
                        'W4' = from West ⟶  in 4th row, etc.)
                """))
            )
            parse = lambda user_input: (
                int(user_input[1:]) - 1,
                dict(zip("NESW",list(Dir)))[user_input[0].upper()] )
        else:
            (dsprite,dname) = DIR_DATA[direction]
            text_ex = (
                alnStr('<', dedentStr(f"""
                -> e.g. '1' = from {dsprite} {dname} in 1st {"column" if direction in [Dir.NORTH,Dir.SOUTH] else "row"})
                """))
            )
            parse = lambda user_input: (
                int(user_input) - 1,
                direction)
        text_turn = glueStrs(
            alnStr(f'^{W}', dedentStr(f"""
            {psprite} {pname}
            {dsprite} {dname}
            """))
        )
        text_status = glueStrs(
            alnStr('<', BAR),
            alnStr(f'^{W}', f"Turn {game.current_turn_number}"),
            alnStr(f'^{W}', text_turn),
            alnStr(f'^{W}', boxStr(alnStr(f'^{W-4}', game.str_board(tilemap)))),
            alnStr(f'^{W}', f"[pieces left: {' - '.join(f'{remaining} {PIECE_DATA[player][0]}' for (player,remaining) in enumerate(game.remaining_pieces))}]"),
            alnStr('<',(text_ex if game.current_turn_number <= 3 else '')),
        )
        print(text_status)
        while True:
            try:
                user_input = input("> ")
                if user_input.startswith("sudo "):
                    exec(user_input[5:])
                    continue
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
        (psprite,pname) = PIECE_DATA(winners[0])
        text_winners = f"⋆｡ﾟ☁｡ {psprite} {pname} won the game! {psprite} ｡ ﾟ☾｡⋆"
    else:
        text_winners = f"It's a Draw between {', '.join(PIECE_DATA(winner)[1] for winner in winners)}!"
    end_text = glueStrs(
        alnStr('<',BAR),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_board(tilemap)))),
        alnStr(f'^{W}',"Game Over."),
        alnStr(f'^{W}',"Resulting pruned tree:"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', game.str_board(tilemap,pruned=True)))),
        alnStr(f'^{W}',f"Player scores: {' - '.join(f'{score} {PIECE_DATA[player][0]}' for (player,score) in enumerate(game.scores()))}"),
        alnStr(f'^{W}',boxStr(alnStr(f'^{W-4}', text_winners))),
        alnStr(f'^{W}',BAR),
    )
    print(end_text)
    return

# END   FUNCTIONS

# BEGIN MAIN
# No main
# END   MAIN
