1. Board & Piece Evaluation
Material Values: The bot assigns points to every piece (Pawn = 100, Knight/Bishop = 300, Rook = 500, Queen = 900).

Piece-Square Tables: It uses 8x8 grids to score how "good" a square is for a specific piece. For example, knights get penalized for sitting on the edge of the board, while pawns get bonuses for pushing forward.

The Perspective: White pieces add to the total score, and Black pieces subtract from it. The bot tries to maximize this score if it is playing White, and minimize it if it is playing Black.

2. Move Ordering
Before deeply calculating any moves, the bot quickly pre-scores and sorts them.

It prioritizes checks, pawn promotions, and valuable captures (like a bishop taking a rook) so they are calculated first. Sorting moves first makes the main search process dramatically faster.

3. Minimax with Alpha-Beta Pruning
Deep Lookahead: The bot simulates future moves up to 5 turns ahead. It assumes both players will make their absolute best moves.

Pruning (Alpha-Beta): If the bot spots a branch of moves that is guaranteed to be worse than a line it has already calculated, it discards that branch immediately. This saves massive amounts of computing time.

4. Quiescence Search (The Peacekeeper)
When the main 5-turn search limit is reached, the bot doesn't just stop. Stopping in the middle of a chaotic trade would cause the bot to blunder.

Instead, it enters a mini-search that continues evaluating only capture moves until the board is "quiet" (no immediate captures are left). This ensures it only makes decisions based on stable, safe positions.
