import tkinter as tk
import subprocess
import os

VIDEO_PATH = "export_1774386610557.MOV"

class ProbabilityUI:
    def __init__(self, categories: list[str]) -> None:
        self.root = tk.Tk()
        self._vlc_proc = None

        self.root.attributes("-fullscreen", True)
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
        if self._vlc_proc is not None:
            return  # already playing

        print("Running video")
        self._vlc_proc = subprocess.Popen([
            "/Applications/VLC.app/Contents/MacOS/VLC",
            "--fullscreen",
            "--play-and-exit",
            "--no-video-title-show",
            VIDEO_PATH
        ])
        self._poll_vlc()

    def _poll_vlc(self) -> None:
        if self._vlc_proc and self._vlc_proc.poll() is None:
            self.root.after(300, self._poll_vlc)
        else:
            self._vlc_proc = None
            # AppleScript brings this process back to front by PID
            script = (
                f"tell application \"System Events\" to set frontmost of "
                f"every process whose unix id is {os.getpid()} to true"
            )
            subprocess.Popen(["osascript", "-e", script])
            self.root.after(150, self._raise_window)

    def _raise_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.after(300, lambda: self.root.attributes("-topmost", False))

    def update(self, percentages: list[int]) -> None:
        for i, percent in enumerate(percentages):
            bar = self.bars[i]
            canvas: tk.Canvas = bar["canvas"]

            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            fill_height = int((percent / 100) * height)

            canvas.create_rectangle(
                0,
                height - fill_height,
                width,
                height,
                fill="lime green"
            )

            bar["text"].config(text=f"{percent}%")

        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()


ui = ProbabilityUI(["Animals", "Space", "Ocean"])
ui.update([75, 10, 15])
ui.run()