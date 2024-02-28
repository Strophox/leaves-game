# BEGIN OUTLINE
"""
This script contains a `run` function to play a `leaves.Game` in a pygame widget.
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
    win = pygame.display.set_mode((1280, 720), pygame.RESIZABLE) # Main window
    pygame.display.set_caption("Leaves")
    font = pygame.font.SysFont("monospace", 24) # Might be resized
    show_pruned = False

    # Main fetch-evaluate-draw game loop
    running = True
    while running:
        pygame.time.wait(32) # 32ms = 31.25fps

        # Process input
        events = set() # List of events to be used later
        keys   = set() # List of pressed keys
        mods   = set() # List of pressed key modifiers
        for event in pygame.event.get():
            # Add to sensed key presses
            if event.type == pygame.KEYDOWN:
                keys.add(event.key)
            else:
                events.add(event.type)
        flags_set = pygame.key.get_mods()
        for flag in [pygame.KMOD_CTRL,pygame.KMOD_SHIFT,pygame.KMOD_ALT]:
            # Add to sense key modifiers
            if flag & flags_set:
                mods.add(flag)

        # Figure out basic margin for board drawing
        # -> "(x|y)m(0|1)" are the (row|column) margin (start|end) coordinates
        (W,H) = pygame.display.get_surface().get_size()
        (gameW,gameH) = game.current_board_size
        fraction = 0.70
        win_mrg = int( min(W,H)/2 * (1-fraction) )
        ((xm0,ym0), (xm1,ym1)) = ((win_mrg,win_mrg), (W-win_mrg,H-win_mrg))

        # Figure out exact frame within which to draw game
        # -> "(x|y)f(0|1)" are the (row|column) game board frame (start|end) coordinates
        # Game board has wider aspect ratio than allowed frame:
        if ((xm1-xm0)/(ym1-ym0)) <= gameW/gameH:
            sidemrg = int( ((ym1-ym0) - gameH * (xm1-xm0)/gameW) / 2 )
            ((xf0,yf0), (xf1,yf1)) = ((xm0,ym0+sidemrg), (xm1,ym1-sidemrg))
        # Game board has lower aspect ratio than allowed frame:
        elif ((xm1-xm0)/(ym1-ym0)) > gameW/gameH:
            sidemrg = int( ((xm1-xm0) - gameW * (ym1-ym0)/gameH) / 2 )
            ((xf0,yf0), (xf1,yf1)) = ((xm0+sidemrg,ym0), (xm1-sidemrg,ym1))

        # Ctrl + r: Reset game
        if pygame.KMOD_CTRL in mods and pygame.K_r in keys:
            game.reset()
        # quit | Ctrl + c: Quit game
        if pygame.QUIT in events or (pygame.KMOD_CTRL in mods and pygame.K_c in keys):
            running = False
        # Ctrl + p: Toggle show_pruned
        if pygame.KMOD_CTRL in mods and pygame.K_p in keys:
            show_pruned ^= True
        # Ctrl + s: Show turn history
        if pygame.KMOD_CTRL in mods and pygame.K_s in keys:
            print(f"Turn history:\n---\n{game.current_turn_history}\n---")

        # Process mouse
        (xms,yms) = pygame.mouse.get_pos()
        # Mouse is on vertical sides:
        if (xms <= xf0 or xf1 <= xms) and yf0 <= yms <= yf1:
            sel_line = int((yms-yf0) / (yf1-yf0) * gameH)
            sel_dir  = Dir.WEST if xms <= xf0 else Dir.EAST
        # Mouse is on horizontal sides:
        elif (yms <= yf0 or yf1 <= yms) and xf0 <= xms <= xf1:
            sel_line = int((xms-xf0) / (xf1-xf0) * gameW)
            sel_dir  = Dir.NORTH if yms <= yf0 else Dir.SOUTH
        # Mouse is not selecting a game row or column:
        else:
            sel_line = None
            sel_dir  = None

        # Process mouse click
        if pygame.MOUSEBUTTONDOWN in events:
            match game.check_move(sel_line,sel_dir):
                case "":
                    game.make_move(sel_line,sel_dir)
                case err:
                    print(f"Whoops: {err}") # TODO make error feedback better?

        # Set window caption
        pygame.display.set_caption(f"Leaves - Turn {game.current_turn_number+1}")

        # Accent color used
        accentcol = ct.LIGHT_GRAY if game.is_over else PIECE_DATA[game.current_turn[0]][2][0][2]

        # Draw background
        bgcol = ct.mix(ct.mix(accentcol,ct.BLACK,6/8),ct.DARK_GRAY,1/8)
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
        tileSz = int((xf1-xf0) / gameW) # Available square length (px) per piece
        barcol1 = ct.mix(bgcol, ct.mix(ct.WHITE,accentcol,2/8), 0.25) # Low pulse
        barcol2 = ct.mix(bgcol, ct.mix(ct.WHITE,accentcol,2/8), 0.4) # High pulse
        rate = 2500 # Blinking rate
        timeparam = pygame.time.get_ticks()%rate/rate
        barcol = ct.interpolate([barcol1,barcol2,barcol1],timeparam)
        # Invalid move: Don't select line
        if not game.check_move(sel_line,sel_dir) == "":
            pass
        # Selected column:
        elif sel_dir in [Dir.NORTH,Dir.SOUTH]:
            pygame.draw.rect(win, barcol, (xf0+tileSz*sel_line,0, tileSz,H))
        # Selected row:
        elif sel_dir in [Dir.EAST,Dir.WEST]:
            pygame.draw.rect(win, barcol, (0,yf0+tileSz*sel_line, W,tileSz))

        # Draw all board tiles
        psize = 0.9 # Scaled piece size (so they dont stick to each other directly)
        pmarg = tileSz*(1-psize)/2 # Resulting piece margin
        board = game.board.pruned() if show_pruned else game.board
        for (xp,yp),piecetype in board.pieces.items():
            (xa,ya) = (xf0 + xp*tileSz, yf0 + yp*tileSz) # Piece (tile) anchor
            # Draw each of the piece layers
            for ((xo,yo),(xl,yl),color) in PIECE_DATA[piecetype][2]:
                offset_size = (
                    xo*tileSz*psize + pmarg + xa, # Texture offset
                    xo*tileSz*psize + pmarg + ya, #
                    xl*tileSz*psize, # Texture length
                    yl*tileSz*psize) #
                pygame.draw.rect(win, color, offset_size)

        # Draw texts
        if not game.is_over:
            (player,direction) = game.current_turn
            (dsprite,dname) = DIR_DATA_ANY if direction is None else DIR_DATA[direction]
            ratio = 5 # Split remaining vertical space into equal sections
            # Window resized: Reload (resize) font
            if pygame.VIDEORESIZE in events:
                font = pygame.font.SysFont("monospace", round(win_mrg/ratio))
            fontcol = ct.mix(ct.WHITE,accentcol,2/8)
            win.blit( # Current player text
                font.render(f"Player {1+player}",True,fontcol),
                (win_mrg/ratio,win_mrg*1/ratio))
            win.blit( # Current direction text
                font.render(f"Direction: {dsprite} {dname}",True,fontcol),
                (win_mrg/ratio,win_mrg*2/ratio))
            win.blit( # Pieces per player left text
                font.render(f"Pieces left: {', '.join(f'Player {1+player} = {remaining}' for (player,remaining) in enumerate(game.remaining_pieces))}",True,fontcol),
                (win_mrg/ratio,yf1+win_mrg*3/ratio))
        # Game over - name winners:
        else:
            winners = game.compute_winners()
            # Unique winner:
            if len(winners) == 1:
                winnercol = PIECE_DATA[winners[0]][2][0][2]
                text_winners = f"Player {1+winners[0]} wins!"
            # Draw between several players:
            else:
                winnercol = ct.LIGHT_GRAY
                text_winners = f"It's a Draw between {', '.join(f'Player {1+winner}' for winner in winners)}!"
            fontcol = ct.mix(ct.WHITE,winnercol,7/8)
            win.blit(
                font.render(text_winners,True,fontcol),
                (win_mrg/ratio,win_mrg/ratio))

        # Update display and restart loop
        pygame.display.update()

    # Cleanup
    pygame.quit()
    return

# END   FUNCTIONS


# BEGIN MAIN
# No main
# END   MAIN
