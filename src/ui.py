from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .ai import get_best_move
from .game2048 import Direction, Game2048


APP_BG = "#faf8ef"
TEXT_DARK = "#776e65"
TEXT_LIGHT = "#f9f6f2"
BOARD_BG = "#bbada0"
EMPTY_BG = "#cdc1b4"

TILE_COLORS = {
    0: (EMPTY_BG, TEXT_DARK),
    2: ("#eee4da", TEXT_DARK),
    4: ("#ede0c8", TEXT_DARK),
    8: ("#f2b179", TEXT_LIGHT),
    16: ("#f59563", TEXT_LIGHT),
    32: ("#f67c5f", TEXT_LIGHT),
    64: ("#f65e3b", TEXT_LIGHT),
    128: ("#edcf72", TEXT_LIGHT),
    256: ("#edcc61", TEXT_LIGHT),
    512: ("#edc850", TEXT_LIGHT),
    1024: ("#edc53f", TEXT_LIGHT),
    2048: ("#edc22e", TEXT_LIGHT),
}


class GameWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("2048")
        self.root.configure(bg=APP_BG)
        self.root.geometry("500x620")
        self.root.minsize(470, 580)

        self.game = Game2048()
        self.auto_play = False
        self.move_count = 0

        self.score_var = tk.StringVar(value="0")
        self.best_tile_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="Use arrows or WASD")
        self.depth_var = tk.IntVar(value=3)

        self.tile_labels: list[list[tk.Label]] = []

        self._build_ui()
        self._bind_keys()
        self._refresh()

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, bg=APP_BG)
        top.pack(fill="x", padx=18, pady=(14, 8))

        left = tk.Frame(top, bg=APP_BG)
        left.pack(side="left", anchor="n")

        title = tk.Label(
            left,
            text="2048",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Helvetica", 38, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            left,
            text="Join the tiles, get to 2048!",
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Helvetica", 10),
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        right = tk.Frame(top, bg=APP_BG)
        right.pack(side="right", anchor="n")

        self._score_box(right, "SCORE", self.score_var).pack(side="left", padx=(0, 8))
        self._score_box(right, "MAX", self.best_tile_var).pack(side="left")

        controls = tk.Frame(self.root, bg=APP_BG)
        controls.pack(fill="x", padx=18, pady=(0, 8))

        tk.Button(
            controls,
            text="New Game",
            command=self.restart,
            bg="#8f7a66",
            fg="white",
            activebackground="#9f8b78",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=7,
            font=("Helvetica", 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            controls,
            text="AI Step",
            command=self.ai_step,
            bg="#8f7a66",
            fg="white",
            activebackground="#9f8b78",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=7,
            font=("Helvetica", 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))

        self.auto_button = tk.Button(
            controls,
            text="Autoplay",
            command=self.toggle_auto,
            bg="#8f7a66",
            fg="white",
            activebackground="#9f8b78",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=7,
            font=("Helvetica", 9, "bold"),
            cursor="hand2",
        )
        self.auto_button.pack(side="left", padx=(0, 8))

        tk.Label(controls, text="Depth", bg=APP_BG, fg=TEXT_DARK, font=("Helvetica", 10, "bold")).pack(side="left")
        ttk.Spinbox(controls, from_=1, to=6, width=3, textvariable=self.depth_var).pack(side="left", padx=(6, 0))

        board_outer = tk.Frame(self.root, bg=BOARD_BG)
        board_outer.pack(fill="both", expand=True, padx=18, pady=(0, 8))

        for r in range(4):
            board_outer.grid_rowconfigure(r, weight=1, uniform="r")
            board_outer.grid_columnconfigure(r, weight=1, uniform="c")

        for r in range(4):
            row: list[tk.Label] = []
            for c in range(4):
                tile = tk.Label(
                    board_outer,
                    text="",
                    bg=EMPTY_BG,
                    fg=TEXT_DARK,
                    font=("Helvetica", 26, "bold"),
                    bd=0,
                    relief="flat",
                )
                tile.grid(row=r, column=c, sticky="nsew", padx=6, pady=6)
                row.append(tile)
            self.tile_labels.append(row)

        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=APP_BG,
            fg=TEXT_DARK,
            font=("Helvetica", 10),
        )
        status.pack(anchor="w", padx=18, pady=(0, 14))

    def _score_box(self, parent: tk.Widget, title: str, value: tk.StringVar) -> tk.Frame:
        box = tk.Frame(parent, bg="#bbada0", padx=10, pady=5)
        tk.Label(box, text=title, bg="#bbada0", fg="#eee4da", font=("Helvetica", 8, "bold")).pack()
        tk.Label(box, textvariable=value, bg="#bbada0", fg="white", font=("Helvetica", 12, "bold")).pack()
        return box

    def _bind_keys(self) -> None:
        self.root.bind("<Up>", lambda _e: self.try_move("up"))
        self.root.bind("<Down>", lambda _e: self.try_move("down"))
        self.root.bind("<Left>", lambda _e: self.try_move("left"))
        self.root.bind("<Right>", lambda _e: self.try_move("right"))
        self.root.bind("w", lambda _e: self.try_move("up"))
        self.root.bind("s", lambda _e: self.try_move("down"))
        self.root.bind("a", lambda _e: self.try_move("left"))
        self.root.bind("d", lambda _e: self.try_move("right"))

    def _refresh(self) -> None:
        for r in range(4):
            for c in range(4):
                v = self.game.board[r][c]
                bg, fg = TILE_COLORS.get(v, ("#3c3a32", TEXT_LIGHT))
                text = str(v) if v else ""
                font_size = 26
                if v >= 1024:
                    font_size = 21
                if v >= 16384:
                    font_size = 16

                self.tile_labels[r][c].config(text=text, bg=bg, fg=fg, font=("Helvetica", font_size, "bold"))

        self.score_var.set(str(self.game.score))
        self.best_tile_var.set(str(self.game.max_tile()))

        if not self.game.can_move():
            self.status_var.set("Game over - click New Game")
            self.auto_play = False
            self.auto_button.config(text="Autoplay")
        elif self.auto_play:
            self.status_var.set(f"Autoplay running (depth {self.depth_var.get()})")
        else:
            self.status_var.set(f"Ready - depth {self.depth_var.get()} - moves {self.move_count}")

    def try_move(self, direction: Direction) -> None:
        if self.game.move(direction, spawn_tile=True):
            self.move_count += 1
            self._refresh()

    def ai_step(self) -> None:
        if not self.game.can_move():
            return
        move = get_best_move(self.game, depth=self.depth_var.get())
        if self.game.move(move, spawn_tile=True):
            self.move_count += 1
        self._refresh()

    def toggle_auto(self) -> None:
        self.auto_play = not self.auto_play
        self.auto_button.config(text="Stop" if self.auto_play else "Autoplay")
        if self.auto_play:
            self._auto_tick()
        else:
            self._refresh()

    def _auto_tick(self) -> None:
        if not self.auto_play:
            return
        if not self.game.can_move():
            self.auto_play = False
            self.auto_button.config(text="Autoplay")
            self._refresh()
            return

        move = get_best_move(self.game, depth=self.depth_var.get())
        if self.game.move(move, spawn_tile=True):
            self.move_count += 1

        self._refresh()
        self.root.after(85, self._auto_tick)

    def restart(self) -> None:
        self.game.reset()
        self.move_count = 0
        self.auto_play = False
        self.auto_button.config(text="Autoplay")
        self._refresh()

    def run(self) -> None:
        self.root.mainloop()


def run_gui() -> None:
    GameWindow().run()


def run_cli() -> None:
    # Kept for backward compatibility with earlier imports.
    run_gui()


if __name__ == "__main__":
    run_gui()
