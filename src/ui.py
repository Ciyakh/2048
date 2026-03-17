from __future__ import annotations

import os
import sys
import time
from typing import Optional

from .game2048 import Game2048
from .ai import get_best_move


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def format_board(game: Game2048) -> str:
    size = game.size
    cell_w = 6
    h = "+" + "+".join(["-" * cell_w] * size) + "+"

    lines = [h]
    for r in range(size):
        row = []
        for c in range(size):
            v = game.board[r][c]
            row.append((str(v) if v else "").center(cell_w))
        lines.append("|" + "|".join(row) + "|")
        lines.append(h)
    return "\n".join(lines)


def _read_key_windows() -> Optional[str]:
    # Immediate key reading for Windows.
    import msvcrt  # type: ignore

    ch = msvcrt.getwch()

    # Arrow keys are two-part sequences.
    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()
        return {
            "H": "up",     # up arrow
            "P": "down",   # down arrow
            "K": "left",   # left arrow
            "M": "right",  # right arrow
        }.get(ch2)

    ch = ch.lower()
    if ch in ("w", "a", "s", "d"):
        return {"w": "up", "a": "left", "s": "down", "d": "right"}[ch]
    if ch in ("e",):
        return "e"
    if ch in ("q",):
        return "quit"
    if ch in ("r",):
        return "restart"

    return None


def _read_key_fallback() -> Optional[str]:
    # Line-based input fallback (non-Windows or if msvcrt fails).
    line = input("Move (w/a/s/d), r=restart, q=quit: ").strip().lower()
    if not line:
        return None
    ch = line[0]
    if ch in ("w", "a", "s", "d"):
        return {"w": "up", "a": "left", "s": "down", "d": "right"}[ch]
    if ch == "q":
        return "quit"
    if ch == "r":
        return "restart"
    return None


def read_action() -> Optional[str]:
    if os.name == "nt":
        try:
            return _read_key_windows()
        except Exception:
            return _read_key_fallback()
    return _read_key_fallback()


def run_cli() -> None:
    game = Game2048()

    while True:
        clear_screen()
        print("2048 (terminal UI)")
        print("Controls: WASD or Arrow Keys | r=restart | q=quit | e=expectimax AI move")
        print(f"Score: {game.score}   Max tile: {game.max_tile()}")
        print()
        print(format_board(game))

        if not game.can_move():
            print("\nGame over. Press r to restart or q to quit.")

        action = read_action()
        if action is None:
            continue
        if action == "quit":
            return
        if action == "restart":
            game.reset()
            continue

        if action in {"up", "down", "left", "right"}:
            game.move(action, spawn_tile=True)
            continue
        
        if action == "e":
            print("AI is thinking...")
            best_move = get_best_move(game)
            print(f"AI recommends: {best_move}")
            game.move(best_move, spawn_tile=True)
            continue
        # Any other key: ignore


if __name__ == "__main__":
    run_cli()
