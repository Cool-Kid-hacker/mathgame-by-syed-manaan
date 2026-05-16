import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

# Works when this file is in the same directory as the game files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES = {
    "Car Racing (PythonCarGame)": "PythonCarGame.py",
    "Snake (PythonSnakeGame)": "PythonSnakeGame.py",
    "Platformer (bestgame)": "bestgame.py",
}


def run_game(game_path):
    full_path = os.path.join(BASE_DIR, game_path)
    if not os.path.exists(full_path):
        messagebox.showerror("Error", f"Game file not found: {full_path}")
        return

    # Start game in a new process with the same Python interpreter
    try:
        subprocess.Popen([sys.executable, full_path], cwd=BASE_DIR)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to launch game: {e}")


def create_hub():
    root = tk.Tk()
    root.title("PyGame Hub")
    root.geometry("480x360")
    root.resizable(False, False)

    heading = tk.Label(root, text="Play your games", font=("Segoe UI", 20, "bold"))
    heading.pack(pady=20)

    info = tk.Label(root, text="Click a button to open one of the games.", font=("Segoe UI", 12))
    info.pack(pady=(0, 20))

    for label, file_name in GAMES.items():
        btn = tk.Button(root, text=label, width=30, height=2, font=("Segoe UI", 11),
                        command=lambda fn=file_name: run_game(fn))
        btn.pack(pady=6)

    note = tk.Label(root, text="Close this hub window; game windows run independently.", font=("Segoe UI", 10, "italic"))
    note.pack(side="bottom", pady=10)

    root.mainloop()


if __name__ == "__main__":
    create_hub()
