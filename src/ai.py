import math
from game2048 import Game2048, Direction

DIRECTIONS: list[Direction] = ["up", "down", "left", "right"]

SCORE_LOST_PENALTY        = 200000.0
SCORE_MONOTONICITY_POWER  = 4.0
SCORE_MONOTONICITY_WEIGHT = 47.0
SCORE_SUM_POWER           = 3.5
SCORE_SUM_WEIGHT          = 11.0
SCORE_MERGES_WEIGHT       = 700.0
SCORE_EMPTY_WEIGHT        = 270.0


def _tile_rank(tile: int) -> float:
    """Convert an actual tile value to its log2 rank (0 for empty)."""
    if tile <= 0:
        return 0.0
    return math.log2(tile)


def _score_line(line: list[int]) -> float:
    """Score a single row or column using the C++ heuristic."""
    ranks = [_tile_rank(t) for t in line]

    # Sum component
    total_sum = sum(r ** SCORE_SUM_POWER for r in ranks)

    # Empty count
    empty = sum(1 for r in ranks if r == 0)

    # Merges: count runs of equal non-zero ranks
    merges = 0
    prev = 0
    counter = 0
    for r in ranks:
        if r == 0:
            continue
        if prev == r:
            counter += 1
        else:
            if counter > 0:
                merges += 1 + counter
            counter = 0
        prev = r
    if counter > 0:
        merges += 1 + counter

    # Monotonicity
    mono_left = 0.0
    mono_right = 0.0
    for i in range(1, len(ranks)):
        if ranks[i - 1] > ranks[i]:
            mono_left += ranks[i - 1] ** SCORE_MONOTONICITY_POWER - ranks[i] ** SCORE_MONOTONICITY_POWER
        else:
            mono_right += ranks[i] ** SCORE_MONOTONICITY_POWER - ranks[i - 1] ** SCORE_MONOTONICITY_POWER

    return (
        SCORE_LOST_PENALTY
        + SCORE_EMPTY_WEIGHT * empty
        + SCORE_MERGES_WEIGHT * merges
        - SCORE_MONOTONICITY_WEIGHT * min(mono_left, mono_right)
        - SCORE_SUM_WEIGHT * total_sum
    )


def score_heur_board(game: Game2048) -> float:
    board = game.board
    size = game.size
    total = 0.0

    # Score each row
    for r in range(size):
        total += _score_line(board[r])

    # Score each column (transpose)
    for c in range(size):
        col = [board[r][c] for r in range(size)]
        total += _score_line(col)

    return total


def eval_state(game: Game2048) -> float:
    return score_heur_board(game)

def monotonicity_heuristic(game: Game2048) -> float:
    def rotate_90_cw(board: list[list[int]]) -> list[list[int]]:
        size = len(board)
        return [[board[size - 1 - y][x] for y in range(size)] for x in range(size)]

    def score_board(board: list[list[int]]) -> int:
        size = len(board)
        current = 0
        # Check rows (non-increasing left→right)
        for row in range(size):
            for col in range(size - 1):
                if board[row][col] >= board[row][col + 1]:
                    current += 1
        # Check columns (non-increasing top→bottom)
        for col in range(size):
            for row in range(size - 1):
                if board[row][col] >= board[row + 1][col]:
                    current += 1
        return current

    board = [row[:] for row in game.board]
    best = -1
    for _ in range(4):
        best = max(best, score_board(board))
        board = rotate_90_cw(board)

    return float(best)


def empty_cells_heuristic(game: Game2048) -> float:
    """Scores by number of empty cells plus a small bonus for the current score."""
    empties = len(game.empty_cells())
    return empties * 100.0 + game.score * 0.1


def combined_heuristic(game: Game2048) -> float:
    mono = monotonicity_heuristic(game)
    empties = len(game.empty_cells())
    return mono * 50.0 + empties * 200.0 + score_heur_board(game) * 0.5


HEURISTICS: dict[str, callable] = {
    "score_heur_board": score_heur_board,
    "monotonicity": monotonicity_heuristic,
    "empty_cells": empty_cells_heuristic,
    "combined": combined_heuristic,
}


def expectimax(
    game: Game2048,
    depth: int,
    is_max_player: bool,
    heuristic: callable = eval_state,
) -> float:
    if depth == 0 or not game.can_move():
        return heuristic(game)

    if is_max_player:
        best_val = -math.inf

        for d in DIRECTIONS:
            sim_game = game.clone()
            if sim_game.move(d, spawn_tile=False):
                val = expectimax(sim_game, depth - 1, False, heuristic)
                best_val = max(best_val, val)

        if best_val == -math.inf:
            return heuristic(game)

        return best_val

    else:
        empties = game.empty_cells()
        if not empties:
            return heuristic(game)

        total_expected_val = 0.0
        prob = 1.0 / len(empties)

        for r, c in empties:
            sim_game_2 = game.clone()
            sim_game_2.board[r][c] = 2
            total_expected_val += (0.9 * prob) * expectimax(sim_game_2, depth - 1, True, heuristic)

            sim_game_4 = game.clone()
            sim_game_4.board[r][c] = 4
            total_expected_val += (0.1 * prob) * expectimax(sim_game_4, depth - 1, True, heuristic)

        return total_expected_val


def get_best_move(
    game: Game2048,
    depth: int = 3,
    heuristic: callable = eval_state,
) -> Direction:
    best_val = -math.inf
    best_move: Direction = "up"

    for d in DIRECTIONS:
        sim_game = game.clone()
        if sim_game.move(d, spawn_tile=False):
            val = expectimax(sim_game, depth - 1, False, heuristic)
            if val > best_val:
                best_val = val
                best_move = d

    return best_move