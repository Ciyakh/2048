from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Iterable, List, Optional, Sequence, Tuple


Direction = str  # one of: 'up', 'down', 'left', 'right'


def _compress_and_merge_line(line: Sequence[int]) -> Tuple[List[int], int, bool]:
    """Return (new_line, score_gained, changed) for a single row/col moved left."""
    size = len(line)
    tiles = [x for x in line if x != 0]

    merged: List[int] = []
    score_gained = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            new_val = tiles[i] * 2
            merged.append(new_val)
            score_gained += new_val
            i += 2
        else:
            merged.append(tiles[i])
            i += 1

    merged += [0] * (size - len(merged))
    changed = list(line) != merged
    return merged, score_gained, changed


@dataclass
class Game2048:
    size: int = 4
    rng: random.Random = random.Random()

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board: List[List[int]] = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score: int = 0
        self._spawn_random_tile()
        self._spawn_random_tile()

    def clone(self) -> "Game2048":
        g = Game2048(size=self.size, rng=self.rng)
        g.board = [row[:] for row in self.board]
        g.score = self.score
        return g

    def empty_cells(self) -> List[Tuple[int, int]]:
        empties: List[Tuple[int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    empties.append((r, c))
        return empties

    def _spawn_random_tile(self) -> bool:
        empties = self.empty_cells()
        if not empties:
            return False
        r, c = self.rng.choice(empties)
        # Standard 2048: 90% 2, 10% 4
        self.board[r][c] = 4 if self.rng.random() < 0.1 else 2
        return True

    def can_move(self) -> bool:
        if self.empty_cells():
            return True
        for r in range(self.size):
            for c in range(self.size):
                v = self.board[r][c]
                if r + 1 < self.size and self.board[r + 1][c] == v:
                    return True
                if c + 1 < self.size and self.board[r][c + 1] == v:
                    return True
        return False

    def move(self, direction: Direction) -> bool:
        """Apply a move. Returns True if the board changed (then spawns a tile)."""
        if direction not in {"up", "down", "left", "right"}:
            raise ValueError(f"Invalid direction: {direction}")

        changed_any = False
        score_gained_total = 0

        if direction in {"left", "right"}:
            for r in range(self.size):
                line = self.board[r]
                if direction == "right":
                    line = list(reversed(line))
                new_line, gained, changed = _compress_and_merge_line(line)
                if direction == "right":
                    new_line = list(reversed(new_line))
                self.board[r] = new_line
                score_gained_total += gained
                changed_any = changed_any or changed

        else:  # up/down
            for c in range(self.size):
                col = [self.board[r][c] for r in range(self.size)]
                if direction == "down":
                    col = list(reversed(col))
                new_col, gained, changed = _compress_and_merge_line(col)
                if direction == "down":
                    new_col = list(reversed(new_col))
                for r in range(self.size):
                    self.board[r][c] = new_col[r]
                score_gained_total += gained
                changed_any = changed_any or changed

        if not changed_any:
            return False

        self.score += score_gained_total
        self._spawn_random_tile()
        return True

    def max_tile(self) -> int:
        return max(max(row) for row in self.board)
