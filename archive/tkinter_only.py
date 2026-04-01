import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time

max_seconds = 15

class App:
    def __init__(self, root: tk.Tk, video_path: str, results: dict[str, int]):
        self.root = root
        self.video_path = video_path
        self.results = results

        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="white")

        self.root.focus_set()
        self.root.bind("<v>", lambda e: self.start_video())

    # ------------------------------
    # VIDEO PLAYER (Tkinter-based)
    # ------------------------------
    def start_video(self) -> None:
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        print("STARTED VIDEO")

        self.cap = cv2.VideoCapture(self.video_path)
        self.start_time = time.time()

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(fill="both", expand=True)

        self.update_video()

        # Resize to window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        print(f"{width}, {height}")
        img = img.resize((width, height))

    def update_video(self) -> None:
        ret, frame = self.cap.read()

        if not ret or (time.time() - self.start_time > max_seconds):
            self.cap.release()
            self.video_label.destroy()
            self.show_results()
            return

        # Convert frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)

        imgtk = ImageTk.PhotoImage(img)

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps)

        self.video_label.imgtk = imgtk  # prevent garbage collection
        self.video_label.configure(image=imgtk)

        # ~60 FPS
        self.root.after(15, self.update_video)

    # ------------------------------
    # RESULTS SCREEN
    # ------------------------------
    def show_results(self) -> None:
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Next Card Distribution!",
            font=("Arial", 36, "bold"),
            bg="white"
        ).pack(pady=20)

        canvas = tk.Canvas(self.root, bg="white")
        canvas.pack(fill="both", expand=True)

        self.root.update_idletasks()

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Load and store pattern image ONCE
        base_img = Image.open("test.png")

        num_categories = len(self.results)
        bar_width = canvas_width // (num_categories * 2)
        spacing = bar_width

        x = spacing // 2

        # Keep references so images don't disappear
        canvas.image_refs = []

        for category, percent in self.results.items():
            bar_height = int((percent / 100) * (canvas_height * 0.8))

            y_top = canvas_height - bar_height
            y_bottom = canvas_height - 50

            # Background
            canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill="lightgray", outline="black"
            )

            # Efficient image fill (ONE image, stretched)
            fill_img = base_img.resize((bar_width, bar_height))
            fill_photo = ImageTk.PhotoImage(fill_img)

            canvas.create_image(x, y_top, anchor="nw", image=fill_photo)
            canvas.image_refs.append(fill_photo)

            # Percent label
            canvas.create_text(
                x + bar_width // 2,
                y_top - 40,
                text=f"{percent}%",
                font=("Arial", 24, "bold"),
                fill="black"
            )

            # Category label
            canvas.create_text(
                x + bar_width // 2,
                y_bottom + 25,
                text=category,
                font=("Arial", 20),
                fill="black"
            )

            x += bar_width + spacing


# ------------------------------
# RUN APP
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()

    app = App(
        root,
        video_path="/Users/tanner/Downloads/test_cat_vid.MP4",
        results={"Testing": 50, "Test2": 25, "Test3": 25}
    )

    root.mainloop()