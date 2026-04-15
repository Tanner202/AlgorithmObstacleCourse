# type: ignore
import serial
import threading
import time
import tkinter as tk
import subprocess
import os
from datetime import datetime


# ----------------------------
# RFID CATEGORY LOOKUP TABLES
# ----------------------------
# Each UID maps to a behavioral category that affects:
# - probability weights
# - video selection
# - serial output signals

sport_cats = [
    "321333454", "01483454", "160443354", "2401343454", "2401493454",
    "962283554", "1602443554", "32993754", "962303554", "1442463554",
    "321013754", "962323554", "1122483554", "321033754", "962343554",
    "962503554", "321053754", "1122363554", "962523554", "481073754",
]

musical_cats = [
    "1282383554", "962543554", "641093754", "1442403554", "9603654",
    "801113754", "1602423554", "9623654", "961133754", "1121153754",
    "322253854", "02413854", "961173754", "322273854", "2402423854",
    "801193754", "322293854", "2242443854", "641213754", "322313854",
]

work_cats = [
    "2082463854", "481233754", "322333854", "1762483854", "321253754",
    "322353854", "1602503854", "01273754", "162373854", "1282523854",
    "160423354", "01463454", "641313454", "160403354", "01443454",
    "961293454", "176383354", "161423454", "1601273454", "192363354",
]


# ----------------------------
# RFID READER (BACKGROUND I/O)
# ----------------------------
# Runs in a separate thread so serial reading never blocks Tkinter UI.

class RFIDReader:
    def __init__(self, port, baud, callback):
        self.ser = serial.Serial(port, baud)
        self.callback = callback

        # Background thread continuously reads RFID input
        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                line = self.ser.readline().decode().strip()

                # Ignore noise / headers from device
                if not line or line == "COUNT,UID":
                    continue
                if not line.startswith("UID:"):
                    continue

                print("LINE:", line)

                # Expected format: "UID: 1,2,3,..."
                parts = line.split(": ")[1].split(",")
                uid = "".join(parts)

                print("UID:", uid)

                # Send UID into UI layer
                self.callback(uid)

            except Exception as e:
                print("Error reading RFID:", e)


# ----------------------------
# MAIN UI / APPLICATION LOGIC
# ----------------------------
class ProbabilityUI:
    """
    Full-screen visualization app that:
    - receives RFID scans
    - adjusts category probabilities
    - plays category videos via VLC
    - sends serial feedback signals
    """

    def __init__(self, categories: list[str]) -> None:
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.categories = categories
        self.bars = []

        # Weight system drives probability changes over time
        self.weights = [1, 1, 1]

        # Tracks most recent RFID scan (used for post-video actions)
        self.current_uid = ""

        # VLC subprocess handle (prevents overlapping playback)
        self._vlc_proc = None

        # ----------------------------
        # UI CONSTRUCTION
        # ----------------------------
        container = tk.Frame(self.root, bg="black")
        container.pack(expand=True, fill="both")

        for name in categories:
            frame = tk.Frame(container, bg="black")
            frame.pack(side="left", expand=True, fill="both", padx=40, pady=40)

            canvas = tk.Canvas(frame, bg="gray20", highlightthickness=0)
            canvas.pack(expand=True, fill="both")

            # Create percent text
            percent_text = tk.Label(
                frame,
                text="0%",
                fg="white",
                bg="black",
                font=("Arial", 24),
            )
            percent_text.pack(pady=10)

            # Create label
            label = tk.Label(
                frame,
                text=name,
                fg="white",
                bg="black",
                font=("Arial", 20),
            )
            label.pack()

            # Store UI references for fast updates
            self.bars.append({
                "canvas": canvas,
                "text": percent_text
            })

        self.root.update()

        # ESC closes application
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Start RFID reader (callback safely routed into Tk thread)
        self.rfid = RFIDReader(
            port="/dev/tty.usbserial-110",
            baud=9600,
            callback=lambda uid: self.root.after(0, self.on_rfid_scan, uid)
        )

    # ----------------------------
    # RFID EVENT HANDLER
    # ----------------------------
    def on_rfid_scan(self, uid):
        print("RFID detected:", uid)

        self.current_uid = uid
        video = f"{uid}.MP4"

        prefix = ""

        # Map UID → category and bias probabilities
        if uid in musical_cats:
            prefix = "MusicalCats"
            self.weights[2] += 3
        elif uid in sport_cats:
            prefix = "SportCats"
            self.weights[1] += 3
        elif uid in work_cats:
            prefix = "WorkCats"
            self.weights[0] += 3
        else:
            print("Unknown Video")

        video_path = f"{prefix}/{video}"

        # Normalize weights into percentages for UI display
        total = sum(self.weights)
        percentages = [round((w / total) * 100, 2) for w in self.weights]

        self.play_video(video_path)
        self.update(percentages)

    # ----------------------------
    # VIDEO PLAYBACK (VLC)
    # ----------------------------
    def play_video(self, video_path) -> None:
        # Prevent stacking multiple VLC instances
        if self._vlc_proc is not None:
            return

        print("Running video:", video_path)

        # Open video
        self._vlc_proc = subprocess.Popen([
            "/Applications/VLC.app/Contents/MacOS/VLC",
            "--fullscreen",
            "--play-and-exit",
            "--no-video-title-show",
            video_path
        ])

        self._poll_vlc()

    def _poll_vlc(self) -> None:
        # Poll VLC until it exits
        if self._vlc_proc and self._vlc_proc.poll() is None:
            self.root.after(300, self._poll_vlc)
            return

        self._vlc_proc = None

        # Bring app back to foreground (macOS workaround)
        script = (
            f'tell application "System Events" to set frontmost of '
            f'every process whose unix id is {os.getpid()} to true'
        )
        subprocess.Popen(["osascript", "-e", script])
        self.root.after(150, self._raise_window)

        # Send category trigger signal back over serial
        if self.current_uid in musical_cats:
            self.rfid.ser.write(b"MUSIC ON\n")
            self.root.after(300, lambda: self.rfid.ser.write(b"MUSIC OFF\n"))

        elif self.current_uid in sport_cats:
            self.rfid.ser.write(b"SPORT ON\n")
            self.root.after(300, lambda: self.rfid.ser.write(b"SPORT OFF\n"))

        elif self.current_uid in work_cats:
            self.rfid.ser.write(b"WORK ON\n")
            self.root.after(300, lambda: self.rfid.ser.write(b"WORK OFF\n"))

    # ----------------------------
    # UI FOCUS MANAGEMENT
    # ----------------------------
    def _raise_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.after(300, lambda: self.root.attributes("-topmost", False))

    # ----------------------------
    # PROBABILITY BAR UPDATE
    # ----------------------------
    def update(self, percentages: list[int]) -> None:
        for i, percent in enumerate(percentages):
            bar = self.bars[i]
            canvas: tk.Canvas = bar["canvas"]

            canvas.delete("all")

            width = canvas.winfo_width()
            height = canvas.winfo_height()

            # Convert percentage → filled bar height
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


# ----------------------------
# MAIN PROGRAM
# ----------------------------
start_time = time.time()

ui = ProbabilityUI(["Work Cats", "Sport Cats", "Musical Cats"])
ui.update([33, 33, 33])
ui.run()

end_time = time.time()

# Log runtime for debugging / benchmarking
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("times.txt", "a", encoding="UTF-8") as f:
    print("TESTING")
    f.write(f"{timestamp} | {end_time - start_time:.2f}\n")