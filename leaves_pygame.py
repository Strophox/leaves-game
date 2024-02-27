# BEGIN OUTLINE
"""
This script only contains `run` for a pygame interface.
"""
# END   OUTLINE


# BEGIN IMPORTS

import pygame
import colortools as ct
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
                game.reset()
            if (event.type == pygame.QUIT
            or event.type == pygame.KEYDOWN and event.key == pygame.K_c and pygame.KMOD_CTRL):
                running = False

        # Set variables based on game state
        if game.is_over:
            playercol = ct.WHITE
        else:
            (player,direction) = game.current_turn
            playercol = PIECE_DATA[player][2][0][2]

        pygame.display.set_caption(f"Leaves - Turn {game.current_turn_number}")

        # Figure out basic margin for board drawing
        (W,H) = pygame.display.get_surface().get_size()
        (gameW,gameH) = game.current_board_size
        fraction = 0.70
        win_mrg = int( min(W,H)/2 * (1-fraction) )
        ((xm0,ym0), (xm1,ym1)) = ((win_mrg,win_mrg), (W-win_mrg,H-win_mrg))
        # -> m(x|y)(0|1) are the start/end coordinates for the margin

        # Figure out exact frame within which to draw game
        # Game board has wider aspect ratio than allowed frame
        if ((xm1-xm0)/(ym1-ym0)) <= gameW/gameH:
            sidemrg = int( ((ym1-ym0) - gameH * (xm1-xm0)/gameW) / 2 )
            ((xf0,yf0), (xf1,yf1)) = ((xm0,ym0+sidemrg), (xm1,ym1-sidemrg))
        # Game board has lower aspect ratio than allowed frame
        elif ((xm1-xm0)/(ym1-ym0)) > gameW/gameH:
            sidemrg = int( ((xm1-xm0) - gameW * (ym1-ym0)/gameH) / 2 )
            ((xf0,yf0), (xf1,yf1)) = ((xm0+sidemrg,ym0), (xm1-sidemrg,ym1))
        # -> f(x|y)(0|1) are the start/end coordinates for the game board frame

        # Process mouse
        (xms,yms) = pygame.mouse.get_pos()
        if yf0 <= yms <= yf1 and (xms <= xf0 or xf1 <= xms):
            sel_line = int((yms-yf0) / (yf1-yf0) * gameH)
            sel_dir = Dir.WEST if xms <= xf0 else Dir.EAST
        elif xf0 <= xms <= xf1 and (yms <= yf0 or yf1 <= yms):
            sel_line = int((xms-xf0) / (xf1-xf0) * gameW)
            sel_dir = Dir.NORTH if yms <= yf0 else Dir.SOUTH
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

        # Draw debug.
        """pygame.draw.rect(win, ct.RGB_RED, (xm0-1,ym0-1, 1,1))
        pygame.draw.rect(win, ct.RGB_GREEN, (xm1,ym0-1, 1,1))
        pygame.draw.rect(win, ct.RGB_BLUE, (xm0-1,ym1, 1,1))
        pygame.draw.rect(win, ct.RGB_YELLOW, (xm1,ym1, 1,1))
        pygame.draw.rect(win, ct.RED, (xf0-2,yf0-2, 2,2))
        pygame.draw.rect(win, ct.GREEN, (xf1,yf0-2, 2,2))
        pygame.draw.rect(win, ct.BLUE, (xf0-2,yf1, 2,2))
        pygame.draw.rect(win, ct.YELLOW, (xf1,yf1, 2,2))"""

        # Draw selected line
        tileSz = int((xf1-xf0) / gameW)
        barcol1 = ct.mix(bgcol, ct.mix(ct.WHITE,playercol,2/8), 0.25)
        barcol2 = ct.mix(bgcol, ct.mix(ct.WHITE,playercol,2/8), 0.4)
        rate = 2500
        t = pygame.time.get_ticks()%rate/rate
        barcol = ct.interpolate([barcol1,barcol2,barcol1],t)
        valid_move = game.check_move(sel_line,sel_dir) == ""
        if sel_dir in [Dir.NORTH,Dir.SOUTH] and valid_move:
            pygame.draw.rect(win, barcol, (xf0+tileSz*sel_line,0, tileSz,H))
        elif sel_dir in [Dir.EAST,Dir.WEST] and valid_move:
            pygame.draw.rect(win, barcol, (0,yf0+tileSz*sel_line, W,tileSz))
        else:
            pass

        # Draw tiles
        psize = 0.9
        for (xp,yp),piecetype in game._board.pieces.items():
            (xt,yt) = (xf0 + xp*tileSz, yf0 + yp*tileSz)
            for ((xd,yd),(xl,yl),col) in PIECE_DATA[piecetype][2]:
                pygame.draw.rect(win, col, (
                    xd*tileSz*psize + tileSz*(1-psize)/2 + xt,
                    xd*tileSz*psize + tileSz*(1-psize)/2 + yt,
                    xl*tileSz*psize,
                    yl*tileSz*psize,
                ))

        # Draw text
        if game.is_over:
            winners = game.compute_winners()
            if len(winners) == 1:
                fontcol = ct.mix(ct.WHITE,PIECE_DATA[winners[0]][2][0][2],8/8)
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
                (win_mrg/ratio,yf1+win_mrg*3/ratio)
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
