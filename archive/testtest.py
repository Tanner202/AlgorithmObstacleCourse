import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
from typing import Dict, List

class CardUI:
    def __init__(self, results: Dict[str, float], pattern_image_path: str):
        self.results = results
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="white")
        self.root.withdraw()  # hide initially

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.pattern_image = Image.open(pattern_image_path).resize((50, 50))
        self.fill_photos: List[ImageTk.PhotoImage] = []  # keep references
        self._draw_bars()

    def _draw_bars(self) -> None:
        self.canvas.delete("all")
        self.fill_photos.clear()

        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        num_categories = len(self.results)
        bar_width = canvas_width // (num_categories * 2)
        spacing = bar_width
        x = spacing // 2

        for category, percent in self.results.items():
            bar_height = int((percent / 100) * (canvas_height * 0.8))
            y_top = canvas_height - bar_height
            y_bottom = canvas_height - 50

            self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom, fill="lightgray", outline="black")

            img_h = ImageTk.PhotoImage(self.pattern_image).height()
            img_w = ImageTk.PhotoImage(self.pattern_image).width()

            for i in range(y_bottom, y_top, -self.pattern_image.height):
                for j in range(x, x + bar_width, self.pattern_image.width):
                    photo = ImageTk.PhotoImage(self.pattern_image)
                    self.fill_photos.append(photo)
                    self.canvas.create_image(j, i, anchor="sw", image=photo)

            self.canvas.create_text(x + bar_width // 2, y_top - 50, text=f"{percent}%", font=("Arial", 24, "bold"))
            self.canvas.create_text(x + bar_width // 2, y_bottom + 25, text=category, font=("Arial", 20))
            x += bar_width + spacing

    def update_results(self, new_results: Dict[str, float]) -> None:
        self.results = new_results
        self._draw_bars()

    def show(self, duration_ms:int) -> None:
        self.root.deiconify()
        if duration_ms:
            self.root.after(duration_ms, self.hide)

    def hide(self) -> None:
        self.root.withdraw()

def play_video_threaded(video_path: str, max_seconds: int = 3) -> None:
    """Run OpenCV video in a separate thread."""
    def _play() -> None:
        cap = cv2.VideoCapture(video_path)
        import time
        start_time = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Video", frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
            if time.time() - start_time > max_seconds:
                break
        cap.release()
        cv2.destroyAllWindows()

    t = Thread(target=_play)
    t.start()
    t.join()  # wait for video to finish

# -------------------------------
# Example usage
# -------------------------------
results_rounds: List[Dict[str, float]] = [
    {"A": 25, "B": 25, "C": 25, "D": 25},
    {"A": 40, "B": 20, "C": 20, "D": 20},
]

ui = CardUI(results_rounds[0], "test.png")

def run_round(round_index: int=0) -> None:
    if round_index >= len(results_rounds):
        return
    # Play video in thread
    play_video_threaded("/Users/tanner/Desktop/video.mov", max_seconds=3)
    # Update results
    ui.update_results(results_rounds[round_index])
    # Show UI for 3s
    ui.show(duration_ms=3000)
    # Schedule next round after UI duration
    ui.root.after(3000, lambda: run_round(round_index + 1))

# Start the first round
run_round()
ui.root.mainloop()