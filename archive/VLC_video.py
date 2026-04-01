import vlc
import time

VIDEO_PATH = "/Users/tanner/Downloads/test_cat_vid.MP4"

instance = vlc.Instance(
    "--no-video-title-show",
    "--vout=macosx",
    "--avcodec-hw=videotoolbox"
)

player = instance.media_player_new()
media = instance.media_new(VIDEO_PATH)
player.set_media(media)

# IMPORTANT: force video window creation
player.set_fullscreen(False)

player.play()

time.sleep(2)

# sometimes macOS needs a nudge
player.set_pause(0)

while True:
    time.sleep(1)