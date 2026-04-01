import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time

# ---------- UI setup ----------
def setup_ui(results: dict[str, int]) -> tk.Tk:
    root = tk.Tk()
    root.title("Card Distribution")
    root.attributes("-fullscreen", True)
    root.configure(bg="white")

    tk.Label(root, text="Next Card Distribution!", font=("Arial", 36, "bold"), bg="white").pack(pady=20)

    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill="both", expand=True)

    # Simple vertical bars
    canvas_width = canvas.winfo_width() or 800
    canvas_height = canvas.winfo_height() or 600
    num_categories = len(results)
    bar_width = canvas_width // (num_categories * 2)
    spacing = bar_width
    x = spacing // 2

    for category, percent in results.items():
        bar_height = int((percent / 100) * (canvas_height * 0.8))
        y_top = canvas_height - bar_height
        y_bottom = canvas_height - 50
        canvas.create_rectangle(x, y_top, x + bar_width, y_bottom, fill="lightgray", outline="black")
        canvas.create_text(x + bar_width // 2, y_top - 30, text=f"{percent}%", font=("Arial", 24, "bold"))
        canvas.create_text(x + bar_width // 2, y_bottom + 25, text=category, font=("Arial", 20))
        x += bar_width + spacing

    return root

# ---------- Video playback ----------
def play_video(video_path: str, max_seconds: int =10) -> None:
    cap = cv2.VideoCapture(video_path)
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

# ---------- Main flow ----------
results = {"Category A": 25, "Category B": 50, "Category C": 25}

# Step 1: Setup UI in memory
root = setup_ui(results)

# Step 2: Play video on top
play_video("video.mp4", max_seconds=10)

# Step 3: Show UI (already created, just start mainloop)
root.mainloop()