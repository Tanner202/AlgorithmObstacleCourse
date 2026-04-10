# type: ignore
import serial
import threading
import time

sport_cats = [
    "321333454",
    "01483454",
    "160443354",
    "2401343454",
    "2401493454",
    "962283554",
    "1602443554",
    "32993754",
    "962303554",
    "1442463554",
    "321013754",
    "962323554",
    "1122483554",
    "321033754",
    "962343554",
    "962503554",
    "321053754",
    "1122363554",
    "962523554",
    "481073754",
]

musical_cats = [
    "1282383554",
    "962543554",
    "641093754",
    "1442403554",
    "9603654",
    "801113754",
    "1602423554",
    "9623654",
    "961133754",
    "1121153754",
    "322253854",
    "02413854",
    "961173754",
    "322273854",
    "2402423854",
    "801193754",
    "322293854",
    "2242443854",
    "641213754",
    "322313854",
]

work_cats = [
    "2082463854",
    "481233754",
    "322333854",
    "1762483854",
    "321253754",
    "322353854",
    "1602503854",
    "01273754",
    "162373854",
    "1282523854",
    "160423354",
    "01463454",
    "641313454",
    "160403354",
    "01443454",
    "961293454",
    "176383354",
    "161423454",
    "1601273454",
    "192363354"
]

start_time = 0
end_time = 0

class RFIDReader:
    def __init__(self, port, baud, callback):
        self.ser = serial.Serial(port, baud)
        self.callback = callback

        threading.Thread(target=self.listen, daemon=True).start()

    def listen(self):
        while True:
            try:
                line = self.ser.readline().decode().strip()

                if not line or line == "COUNT,UID":
                    continue

                if not line.startswith("UID:"):
                    continue
                print("LINE: " + line)
                parts = line.split(": ")[1].split(",")

                # Ignore first value (count)
                uid_numbers = parts

                uid = "".join(uid_numbers)

                print(f"UID: {uid}")

                self.callback(uid)

            except Exception as e:
                print("Error reading RFID:", e)

import tkinter as tk
import subprocess
import os

VIDEO_PATH = "/Users/tanner/Downloads/test_cat_vid.MP4"

class ProbabilityUI:
    def __init__(self, categories: list[str]) -> None:
        self.root = tk.Tk()
        self._vlc_proc = None

        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.categories = categories
        self.bars = []
        self.percentages = [33, 33, 33]

        self.current_uid = ""
        self.weights = [1,1,1]

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
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.rfid = RFIDReader(
            port="/dev/tty.usbserial-110",
            baud=9600,  
            callback=lambda uid: self.root.after(0, self.on_rfid_scan, uid))
    
    def on_rfid_scan(self, uid):
        print("RFID detected:", uid)

        video = f"{uid}.MP4"
        self.current_uid = uid

        prefix = ""
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
        video_path = prefix + "/" + video
        total = sum(self.weights)

        self.play_video(video_path)
        self.update([round((num/total) * 100, 2) for num in self.weights])

    def play_video(self, video_path) -> None:
        if self._vlc_proc is not None:
            return  # already playing

        print("Running video")
        self._vlc_proc = subprocess.Popen([
            "/Applications/VLC.app/Contents/MacOS/VLC",
            "--fullscreen",
            "--play-and-exit",
            "--no-video-title-show",
            video_path
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

            if self.current_uid in musical_cats:
                self.rfid.ser.write(b"MUSIC ON\n")
                self.root.after(300, lambda: self.rfid.ser.write(b"MUSIC OFF\n"))
            elif self.current_uid in sport_cats:
                self.rfid.ser.write(b"SPORT ON\n")
                self.root.after(300, lambda: self.rfid.ser.write(b"SPORT OFF\n"))
            elif self.current_uid in work_cats:
                self.rfid.ser.write(b"WORK ON\n")
                self.root.after(300, lambda: self.rfid.ser.write(b"WORK OFF\n"))

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


start_time = time.time()
ui = ProbabilityUI(["Work Cats", "Sport Cats", "Musical Cats"])
ui.update([33, 33, 33])
ui.run()
end_time = time.time()

from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open("times.txt", "a", encoding="UTF-8") as f:
    print("TESTING")
    f.write(f"{timestamp} | {end_time - start_time:.2f}\n")
