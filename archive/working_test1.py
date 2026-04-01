import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time

max_seconds = 3

def play_video(video_path: str) -> None:
    cap = cv2.VideoCapture(video_path)

    start_time = time.time()

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

def show_results(results: dict[str, float]) -> None:
    """
    Display card distribution as vertical bars in fullscreen.
    
    results: dict like {"Category A": 40, "Category B": 30, "Category C": 30}
    """

    # ------------------------------
    # Create fullscreen window
    # ------------------------------
    root = tk.Tk()
    root.title("Card Distribution")
    root.attributes("-fullscreen", True)  # fullscreen mode
    root.configure(bg="white")

    # ------------------------------
    # Title label
    # ------------------------------
    tk.Label(root, text="Next Card Distribution!", font=("Arial", 36, "bold"), bg="white").pack(pady=20)

    # ------------------------------
    # Create canvas to fill window
    # ------------------------------
    canvas = tk.Canvas(root, bg="white")
    canvas.pack(fill="both", expand=True)

    # Force canvas update so we can get its size
    root.update_idletasks()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    # ------------------------------
    # Load a single pattern image for bar fill
    # ------------------------------
    fill_image = Image.open("test.png").resize((50, 50))  # adjust size if needed
    fill_photo = ImageTk.PhotoImage(fill_image)

    # ------------------------------
    # Draw bars dynamically
    # ------------------------------
    num_categories = len(results)
    bar_width = canvas_width // (num_categories * 2)  # bars take half of available space, spacing in between
    spacing = bar_width  # equal spacing between bars

    x = spacing // 2  # start offset
    for category, percent in results.items():
        # Bar height proportional to percent
        bar_height = int((percent / 100) * (canvas_height * 0.8))  # leave top space for label
        y_top = canvas_height - bar_height
        y_bottom = canvas_height - 50  # leave space at bottom for category label

        # Draw background rectangle
        canvas.create_rectangle(x, y_top, x + bar_width, y_bottom, fill="lightgray", outline="black")

        # Fill with tiled pattern image
        img_h = fill_photo.height()
        img_w = fill_photo.width()
        for i in range(y_bottom, y_top, -img_h):
            for j in range(x, x + bar_width, img_w):
                canvas.create_image(j, i, anchor="sw", image=fill_photo)

        # Label percent on top
        canvas.create_text(x + bar_width // 2, y_top - 50, text=f"{percent}%", font=("Arial", 24, "bold"), fill="black")

        # Label category under bar
        canvas.create_text(x + bar_width // 2, y_bottom + 25, text=category, font=("Arial", 20), fill="black")

        x += bar_width + spacing

    root.mainloop()

#play_video("/Users/tanner/Desktop/Screenshots/RunewildEditorDemo.mov")
show_results({"Testing": 50, "Test2": 25, "Test3": 25})