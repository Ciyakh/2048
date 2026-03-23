# 2048 (Python + Tkinter)

A simple 2048 implementation written in Python with a classic-style **Tkinter** GUI.
Includes an optional AI player (expectimax) with adjustable search depth and autoplay speed.

## Requirements

- Python
- Tkinter (bundled with most standard Python installs on Windows/macOS)

No third-party packages are required.

## Run

From the project root:

```bash
python main.py
```

This launches the GUI.

## Controls

- Move tiles: **Arrow keys** or **WASD**
- **New Game**: resets the board and score

## AI Features

- **AI Step**: performs a single AI-chosen move
- **Autoplay**: continuously plays until game over (press again to stop)
- **Depth**: controls how many moves ahead the AI searches (higher = stronger but slower)
- **Speed**: delay between autoplay moves (lower = faster)

The AI is implemented using an **expectimax** search with a heuristic board evaluation.

## Project Structure

- `main.py` — entrypoint (starts the UI)
- `src/game2048.py` — game engine (board, moves, scoring, spawning tiles)
- `src/ui.py` — Tkinter UI + input handling + AI controls
- `src/ai.py` — expectimax + heuristics and move selection