# BEGIN OUTLINE
"""
This script only contains `run` for a pygame interface.
"""
# END   OUTLINE


# BEGIN IMPORTS

import pygame
import colortools as ct
from leaves_consts import Dir,DIR_DATA,DIR_DATA_ANY,PIECE_DATA,PIECE_DATA_EMPTY
# import leaves

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

def run(game):
    pygame.init()
    init = True
    win = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Leaves")
    font = pygame.font.SysFont("monospace", 0) # TODO fix size

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
            playercol = PIECE_DATA[player][2]

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
            sel_dir = Dir.WEST if msx <= fx0 else Dir.EAST
        elif fx0 <= msx <= fx1 and (msy <= fy0 or fy1 <= msy):
            sel_line = int((msx-fx0) / (fx1-fx0) * gameW)
            sel_dir = Dir.NORTH if msy <= fy0 else Dir.SOUTH
        else:
            sel_line = None
            sel_dir = None

        # Process mouse click
        if pygame.MOUSEBUTTONDOWN in events:
            match game.check_move(sel_line,sel_dir):
                case "":
                    game.make_move(sel_line,sel_dir)
                case err:
                    print(f"Whoops: {err}")

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
        if sel_dir in [Dir.NORTH,Dir.SOUTH] and valid_move:
            pygame.draw.rect(win, barcol, (fx0+tileSz*sel_line,0, tileSz,H))
        elif sel_dir in [Dir.EAST,Dir.WEST] and valid_move:
            pygame.draw.rect(win, barcol, (0,fy0+tileSz*sel_line, W,tileSz))
        else:
            pass

        # Draw tiles
        for (px,py),piecetype in game._board.pieces.items():
            (x,y) = (fx0 + px*tileSz, fy0 + py*tileSz)
            frac = 0.9
            if piecetype == -1:
                pygame.draw.rect(win, ct.mix(ct.ORANGE,ct.GRAY,0.8), (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))
                pygame.draw.rect(win, PIECE_DATA[piecetype][2], (x+tileSz*(1-frac**2)/2,y+tileSz*(1-frac**2)/2, tileSz*frac**2,tileSz*frac**2))
            else:
                pygame.draw.rect(win, PIECE_DATA[piecetype][2], (x+tileSz*(1-frac)/2,y+tileSz*(1-frac)/2, tileSz*frac,tileSz*frac))

        # Draw text
        if game.is_over:
            winners = game.compute_winners()
            if len(winners) == 1:
                fontcol = ct.mix(ct.WHITE,PIECE_DATA[winners[0]][2],8/8)
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
            (dsprite,dname) = DIR_DATA_ANY if direction is None else DIR_DATA[direction]
            text_dir = f"{dsprite} {dname}"
            win.blit(
                font.render(f"Player {1+player}",True,fontcol),
                (win_mrg/ratio,win_mrg*1/ratio)
            )
            win.blit(
                font.render(f"Direction: {text_dir}",True,fontcol),
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
# No main
# END   MAIN
