import pygame as p
import ChessEngine
from stockfish import Stockfish
import chess

stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2.exe", depth=18)
print(stockfish.get_fen_position())
mt = []
b = chess.Board()


WIDTH = HEIGHT = 700
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():

    IMAGES['wp'] = p.image.load("Images/white_pawn.png")
    IMAGES['wR'] = p.image.load("Images/white_rook.png")
    IMAGES['wN'] = p.image.load("Images/white_knight.png")
    IMAGES['wB'] = p.image.load("Images/white_bishop.png")
    IMAGES['wQ'] = p.image.load("Images/white_queen.png")
    IMAGES['wK'] = p.image.load("Images/white_king.png")

    IMAGES['bp'] = p.image.load("Images/black_pawn.png")
    IMAGES['bR'] = p.image.load("Images/black_rook.png")
    IMAGES['bN'] = p.image.load("Images/black_knight.png")
    IMAGES['bB'] = p.image.load("Images/black_bishop.png")
    IMAGES['bQ'] = p.image.load("Images/black_queen.png")
    IMAGES['bK'] = p.image.load("Images/black_king.png")

def main():

    p.init()
    p.display.set_caption('Subhojit Ghosh Chess')
    p.display.set_icon(p.image.load("Images/white_king.png"))
    screen = p.display.set_mode((WIDTH + 350, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("yellow"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    move_log_font = p.font.SysFont("cambria", 16, False, True)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []

                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.move_log[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if not gameOver:
            drawMoveLog(screen, gs, move_log_font)

        if gs.checkmate:

            gameOver = True
            if gs.white_to_move:
                drawText(screen, "Black Wins By CHECKMATE")
            else:
                drawText(screen, "White Wins By CHECKMATE")
            #analyze()


        elif gs.stalemate:
            gameOver = True
            drawText(screen, "STALEMATE")


        clock.tick(MAX_FPS)
        p.display.flip()

# def analyze():
#
#     print(mt)
#     for i in mt:
#         b.push(b.parse_san(i))
#     print(b)
#     stockfish.set_fen_position(b.fen())
#     #print(stockfish.get_evaluation())

def drawMoveLog(screen, game_state, font):

    move_log_rect = p.Rect(WIDTH+5, 5, 340, 570)

    p.draw.rect(screen, p.Color('white'), move_log_rect)
    p.draw.rect(screen, p.Color('black'), move_log_rect, 5)

    text_object = p.font.SysFont("bahnschrift", 18, True, ).render("Moves Log", True, p.Color('black'))
    text_location = move_log_rect.move(move_log_rect.width/3, 10)
    screen.blit(text_object, text_location)

    move_log = game_state.move_log
    move_texts = []

    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if str(move_log[i]) not in mt:
            mt.append(str(move_log[i]))
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
            if str(move_log[i+1]) not in mt:
                mt.append(str(move_log[i+1]))

        move_texts.append(move_string)

    moves_per_row = 3
    padding = 10
    line_spacing = 10
    text_y = 50
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('black'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

def hightlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.start_col == c and move.start_row == r:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    hightlightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    p.draw.rect(screen, p.Color("black"), p.Rect(0,0,WIDTH,HEIGHT),5)
    global colors
    colors = [p.Color("#ebecd0"), p.Color("#739552")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    coords = []
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC))*framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.start_row + dR*frame/frameCount, move.start_col + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        endSquare = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], endSquare)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)

def drawText(screen, text):
    font = p.font.SysFont("bahnschrift", 22 )
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(730, 620)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()


