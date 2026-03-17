import math
from .game2048 import Game2048, Direction

DIRECTIONS: list[Direction] = ["up", "down", "left", "right"]

def eval_state(game: Game2048) -> float:
    """Cutoff test evaluation"""
    empty_cells = len(game.empty_cells())
    max_tile = game.max_tile()
    
    # dummy heuristic: more empty cells and higher max tile is better
    return (empty_cells * 10) + max_tile

def expectimax(game: Game2048, depth: int, is_max_player: bool) -> float:
    # Cutoff test
    if depth == 0 or not game.can_move():
        return eval_state(game)

    if is_max_player:
        best_val = -math.inf
        
        for d in DIRECTIONS:
            sim_game = game.clone()
            # max player only slides the tiles, doesn't spawn new ones
            if sim_game.move(d, spawn_tile=False):
                # Pass to "chanche" node
                val = expectimax(sim_game, depth - 1, False)
                best_val = max(best_val, val)
                
        # If no valid moves, return evaluation
        if best_val == -math.inf:
            return eval_state(game)
            
        return best_val

    else:
        # chance player
        empties = game.empty_cells()
        if not empties:
            return eval_state(game)
            
        total_expected_val = 0.0
        prob = 1.0 / len(empties)
        
        for r, c in empties:
            # 90% chance of a 2 appearing
            sim_game_2 = game.clone()
            sim_game_2.board[r][c] = 2
            total_expected_val += (0.9 * prob) * expectimax(sim_game_2, depth - 1, True)
            
            # 10% chance of a 4 appearing
            sim_game_4 = game.clone()
            sim_game_4.board[r][c] = 4
            total_expected_val += (0.1 * prob) * expectimax(sim_game_4, depth - 1, True)
            
        return total_expected_val

def get_best_move(game: Game2048, depth: int = 3) -> Direction:
    """
    Entry point for the AI. Evaluates the 4 possible root actions.
    """
    best_val = -math.inf
    best_move: Direction = "up"
    
    for d in DIRECTIONS:
        sim_game = game.clone()
        if sim_game.move(d, spawn_tile=False):
            # Evaluate the resulting chance nodes
            val = expectimax(sim_game, depth - 1, False)
            if val > best_val:
                best_val = val
                best_move = d
                
    return best_move