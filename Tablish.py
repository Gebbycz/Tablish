import os
import random
import pygame
import chess
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

pygame.init()

WIDTH = 640
HEIGHT = 640
SQUARE = WIDTH // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tablish Bot")

font = pygame.font.SysFont(["segoeuisymbol", "applesymbols", "dejavusans", "arialunicode", "microsoftyahei"], 70)
menu_font = pygame.font.SysFont("arial", 40)
game_over_font = pygame.font.SysFont("arial", 60, bold=True)

board = chess.Board()

pieces = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
}
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  5,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0,  0,
    -10,  5,  5,  5,  5,  5,  5,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

def evaluate_board(b):
    if b.is_checkmate():
        if b.turn == chess.WHITE:
            return -99999
        else:
            return 99999
    if b.is_stalemate() or b.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = b.piece_at(square)
        if piece:
            val = PIECE_VALUES[piece.piece_type]           
            idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
            if piece.piece_type == chess.PAWN:
                val += PAWN_TABLE[idx]
            elif piece.piece_type == chess.KNIGHT:
                val += KNIGHT_TABLE[idx]
            elif piece.piece_type == chess.BISHOP:
                val += BISHOP_TABLE[idx]
            elif piece.piece_type == chess.ROOK:
                val += ROOK_TABLE[idx]
            elif piece.piece_type == chess.QUEEN:
                val += QUEEN_TABLE[idx]

            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
    return score

def score_move(b, move):
    score = 0
    if b.gives_check(move):
        score += 50
    if move.promotion:
        score += 40
    if b.is_capture(move):
        attacker = b.piece_at(move.from_square)
        target = b.piece_at(move.to_square)
        if attacker and target:
            score += (PIECE_VALUES[target.piece_type] * 10) - PIECE_VALUES[attacker.piece_type]
        else:
            score += 10
    return score

def quiescence_search(b, alpha, beta, maximizing_player):
    stand_pat = evaluate_board(b)
    
    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
            
        for move in b.legal_moves:
            if b.is_capture(move):
                b.push(move)
                score = quiescence_search(b, alpha, beta, False)
                b.pop()
                
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat
            
        for move in b.legal_moves:
            if b.is_capture(move):
                b.push(move)
                score = quiescence_search(b, alpha, beta, True)
                b.pop()
                
                if score <= alpha:
                    return alpha
                if score < beta:
                    beta = score
        return beta

def alpha_beta(b, depth, alpha, beta, maximizing_player):
    if b.is_game_over():
        return evaluate_board(b), None
        
    if depth == 0:
        return quiescence_search(b, alpha, beta, maximizing_player), None

    moves = list(b.legal_moves)
    moves.sort(key=lambda m: score_move(b, m), reverse=True)
    
    best_move = None

    if maximizing_player:
        max_eval = -float('inf')
        for move in moves:
            b.push(move)
            evaluation, _ = alpha_beta(b, depth - 1, alpha, beta, False)
            b.pop()
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            b.push(move)
            evaluation, _ = alpha_beta(b, depth - 1, alpha, beta, True)
            b.pop()
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def smart_move(b):
    is_maximizing = b.turn == chess.WHITE
    _, move = alpha_beta(b, 5, -float('inf'), float('inf'), is_maximizing)
    if move is None:
        move = random.choice(list(b.legal_moves))
    return move

def draw_board():
    colors = [(240, 217, 181), (181, 136, 99)]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, (col * SQUARE, row * SQUARE, SQUARE, SQUARE))

def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - chess.square_rank(square)
            col = chess.square_file(square)
            symbol = pieces[piece.symbol()]
            text = font.render(symbol, True, (0, 0, 0))
            rect = text.get_rect(center=(col * SQUARE + SQUARE // 2, row * SQUARE + SQUARE // 2))
            screen.blit(text, rect)

def select_color():
    selecting = True
    white_rect = pygame.Rect(80, 270, 200, 100)
    black_rect = pygame.Rect(360, 270, 200, 100)
    
    while selecting:
        screen.fill((50, 50, 50))
        
        title_text = menu_font.render("Choose Your Side", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        pygame.draw.rect(screen, (240, 240, 240), white_rect, border_radius=10)
        pygame.draw.rect(screen, (20, 20, 20), black_rect, border_radius=10)
        
        w_text = menu_font.render("White", True, (0, 0, 0))
        b_text = menu_font.render("Black", True, (255, 255, 255))
        
        screen.blit(w_text, w_text.get_rect(center=white_rect.center))
        screen.blit(b_text, b_text.get_rect(center=black_rect.center))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if white_rect.collidepoint(pos):
                    return chess.WHITE
                if black_rect.collidepoint(pos):
                    return chess.BLACK

def get_promotion_choice(color):
    options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    symbols = ["♛", "♜", "♝", "♞"] if color == chess.BLACK else ["♕", "♖", "♗", "♘"]
    
    box_width, box_height = 400, 120
    popup_rect = pygame.Rect((WIDTH - box_width) // 2, (HEIGHT - box_height) // 2, box_width, box_height)
    
    buttons = []
    for i in range(4):
        btn_x = popup_rect.x + 20 + i * 90
        btn_y = popup_rect.y + 20
        buttons.append(pygame.Rect(btn_x, btn_y, 80, 80))
        
    while True:
        pygame.draw.rect(screen, (200, 200, 200), popup_rect, border_radius=10)
        pygame.draw.rect(screen, (50, 50, 50), popup_rect, 4, border_radius=10)
        
        for i, rect in enumerate(buttons):
            pygame.draw.rect(screen, (240, 240, 240), rect, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), rect, 2, border_radius=5)
            sym_text = font.render(symbols[i], True, (0, 0, 0))
            sym_rect = sym_text.get_rect(center=rect.center)
            screen.blit(sym_text, sym_rect)
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, rect in enumerate(buttons):
                    if rect.collidepoint(pos):
                        return options[i]

def display_game_over(message):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    text = game_over_font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(3000)

player = select_color()

if player == chess.BLACK:
    bot_move = smart_move(board)
    board.push(bot_move)

selected = None
running = True

while running:
    draw_board()
    draw_pieces()
    pygame.display.flip()

    if board.is_checkmate():
        display_game_over("CHECKMATE")
        running = False
        continue
    elif board.is_stalemate():
        display_game_over("STALEMATE")
        running = False
        continue
    elif board.is_game_over():
        display_game_over("GAME OVER")
        running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            col = x // SQUARE
            row = 7 - (y // SQUARE)
            square = chess.square(col, row)

            if selected is None:
                piece = board.piece_at(square)
                if piece and piece.color == player:
                    selected = square
            else:
                move = chess.Move(selected, square)
                piece = board.piece_at(selected)
                
                is_promotion = False
                if piece and piece.piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
                    move.promotion = chess.QUEEN
                    if move in board.legal_moves:
                        is_promotion = True

                if is_promotion:
                    chosen_piece = get_promotion_choice(player)
                    move.promotion = chosen_piece

                if move in board.legal_moves:
                    board.push(move)
                    
                    draw_board()
                    draw_pieces()
                    pygame.display.flip()

                if not board.is_game_over() and board.turn != player:
                    bot = smart_move(board)
                    board.push(bot)

                selected = None

pygame.quit()
