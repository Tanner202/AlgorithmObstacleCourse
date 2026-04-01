import tkinter as tk
import vlc

VIDEO_PATH = "/Users/tanner/Downloads/test_cat_vid.MP4"

class App:
    def __init__(self, root):
        self.root = root

        self.instance = vlc.Instance("--vout=opengl", "--no-video-title-show")
        self.player = self.instance.media_player_new()

        media = self.instance.media_new(VIDEO_PATH)
        self.player.set_media(media)

        btn_play = tk.Button(root, text="Play", command=self.play)
        btn_play.pack()

        btn_pause = tk.Button(root, text="Pause", command=self.pause)
        btn_pause.pack()

        btn_stop = tk.Button(root, text="Stop", command=self.stop)
        btn_stop.pack()

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

root = tk.Tk()
root.title("Tkinter + VLC Controller")
App(root)
root.mainloop()