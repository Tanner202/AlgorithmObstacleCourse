import cv2
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
import time
from typing import Dict, List


# ------------------------------
# Video function (runs in a thread)
# ------------------------------
def play_video(video_path: str, max_seconds: int = 3) -> None:
    """
    Play a video in an OpenCV window for up to max_seconds.
    This function blocks until the video finishes.
    """
    cap: cv2.VideoCapture = cv2.VideoCapture(video_path)
    start_time: float = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Video", frame)

        # press q to skip (optional)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        # Stop after max_seconds
        if time.time() - start_time > max_seconds:
            break

    cap.release()
    cv2.destroyAllWindows()


def play_video_threaded(video_path: str, max_seconds: int = 3) -> None:
    """
    Play a video in a separate thread, blocking until done.
    """
    thread: Thread = Thread(target=play_video, args=(video_path, max_seconds))
    thread.start()
    thread.join()  # wait for the video to finish before continuing


# ------------------------------
# Card UI Class
# ------------------------------
class CardUI:
    def __init__(self, results: Dict[str, float], pattern_image_path: str = "test.png") -> None:
        """
        Initialize the Card Distribution UI.
        """
        self.results: Dict[str, float] = results
        self.pattern_image_path: str = pattern_image_path

        self.root: tk.Tk = tk.Tk()
        self.root.title("Card Distribution")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="white")
        self.root.withdraw()  # hide initially

        self.title_label: tk.Label
        self.canvas: tk.Canvas
        self.fill_image: Image.Image
        self.fill_photos: List[ImageTk.PhotoImage] = []  # keep references

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup UI elements and canvas."""
        self.title_label = tk.Label(
            self.root, text="Next Card Distribution!", font=("Arial", 36, "bold"), bg="white"
        )
        self.title_label.pack(pady=20)

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.fill_image = Image.open(self.pattern_image_path).resize((50, 50))

        self._draw_bars()

    def _draw_bars(self) -> None:
        """Draw bars with pattern fills and labels."""
        self.root.update_idletasks()
        self.canvas.delete("all")
        self.fill_photos.clear()

        canvas_width: int = self.canvas.winfo_width()
        canvas_height: int = self.canvas.winfo_height()

        num_categories: int = len(self.results)
        bar_width: int = canvas_width // (num_categories * 2)
        spacing: int = bar_width
        x: int = spacing // 2

        for category, percent in self.results.items():
            bar_height: int = int((percent / 100) * (canvas_height * 0.8))
            y_top: int = canvas_height - bar_height
            y_bottom: int = canvas_height - 50

            # Background rectangle
            self.canvas.create_rectangle(x, y_top, x + bar_width, y_bottom, fill="lightgray", outline="black")

            # Pattern fill (keep references!)
            img_h: int = self.fill_image.height
            img_w: int = self.fill_image.width
            for i in range(y_bottom, y_top, -img_h):
                for j in range(x, x + bar_width, img_w):
                    photo: ImageTk.PhotoImage = ImageTk.PhotoImage(self.fill_image)
                    self.fill_photos.append(photo)
                    self.canvas.create_image(j, i, anchor="sw", image=photo)

            # Percent label
            self.canvas.create_text(
                x + bar_width // 2, y_top - 50, text=f"{percent}%", font=("Arial", 24, "bold"), fill="black"
            )

            # Category label
            self.canvas.create_text(
                x + bar_width // 2, y_bottom + 25, text=category, font=("Arial", 20), fill="black"
            )

            x += bar_width + spacing

    def update_results(self, new_results: Dict[str, float]) -> None:
        """Update the bar results and redraw."""
        self.results = new_results
        self._draw_bars()

    def show(self, duration: int = 10) -> None:
        """
        Show the UI. If duration is set, auto-hide after duration seconds.
        """
        self.root.deiconify()
        if duration:
            self.root.after(duration * 1000, self.hide)
        self.root.update()

    def hide(self) -> None:
        """Hide the UI."""
        self.root.withdraw()


# ------------------------------
# Example loop: Video -> UI -> Video -> UI
# ------------------------------
def run_exhibit(results_rounds: List[Dict[str, float]], video_path: str) -> None:
    """
    Run a sequence of Video -> UI rounds for the exhibit.
    """
    ui: CardUI = CardUI(results_rounds[0], pattern_image_path="test.png")

    for round_index, results in enumerate(results_rounds):
        print(f"Round {round_index + 1}: Playing video...")
        play_video_threaded(video_path, max_seconds=10)

        print(f"Round {round_index + 1}: Showing UI...")
        ui.update_results(results)
        ui.show(duration=10)  # auto-hide after 10 seconds

        # Let Tkinter process events while UI is visible
        ui.root.update()
        time.sleep(10)

    print("Exhibit rounds complete.")
    ui.root.destroy()


# ------------------------------
# Run example
# ------------------------------
if __name__ == "__main__":
    results_rounds: List[Dict[str, float]] = [
        {"Category A": 25, "Category B": 25, "Category C": 25, "Category D": 25},
        {"Category A": 40, "Category B": 20, "Category C": 20, "Category D": 20},
    ]
    video_path: str = "/Users/tanner/Desktop/Screenshots/RunewildEditorDemo.mov"

    run_exhibit(results_rounds, video_path)