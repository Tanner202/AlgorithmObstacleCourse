import tkinter as tk
import subprocess
import sys
import os

VIDEO_PATH = "/Users/tanner/Downloads/test_cat_vid.MP4"

class ProbabilityUI:
    def __init__(self, categories: list[str]) -> None:
        self.root = tk.Tk()
        
        # Get screen size
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        self.root.focus_force()

        # Borderless fullscreen (NO macOS Spaces fullscreen)
        self.root.overrideredirect(True)
        self.root.geometry(f"{w}x{h}+0+0")
        self.root.configure(bg="black")

        self.categories = categories
        self.bars = []

        container = tk.Frame(self.root, bg="black")
        container.pack(expand=True, fill="both")

        for name in categories:
            frame = tk.Frame(container, bg="black")
            frame.pack(side="left", expand=True, fill="both", padx=40, pady=40)

            canvas = tk.Canvas(frame, bg="gray20", highlightthickness=0)
            canvas.pack(expand=True, fill="both")

            percent_text = tk.Label(frame, text="0%", fg="white", bg="black", font=("Arial", 24))
            percent_text.pack(pady=10)

            label = tk.Label(frame, text=name, fg="white", bg="black", font=("Arial", 20))
            label.pack()

            self.bars.append({
                "canvas": canvas,
                "rect": None,
                "text": percent_text
            })

        self.root.update()
    
        # KEYBIND
        self.root.bind("<space>", self.play_video)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
    
    def play_video(self, event: tk.Event) -> None:
        print("Running video")
        subprocess.run([
            "open", "-a", "VLC", "--args",
            "--fullscreen",
            "--play-and-exit",
            VIDEO_PATH
        ], check=False)

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.update_idletasks()

    def update(self, percentages: list[int]) -> None:
        for i, percent in enumerate(percentages):
            bar = self.bars[i]
            canvas: tk.Canvas = bar["canvas"]

            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            fill_height = int((percent / 100) * height)

            # Draw bar (from bottom up)
            rect = canvas.create_rectangle(
                0,
                height - fill_height,
                width,
                height,
                fill="lime green"
            )

            bar["rect"] = rect
            percent_label = bar["text"]
            percent_label.config(text=f"{percent}%")

        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()

ui = ProbabilityUI(["Animals", "Space", "Ocean"])

ui.update([30, 50, 20])

ui.run()