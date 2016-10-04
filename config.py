HOST = ''
PORT = 1010

MUSIC_DIR = "music"

allowed_extensions = ("mp3", "wav")


class commands:
    PLAYER = 'mplayer'
    YOUTUBE = 'yt-dl'

    class mplayer:
        CTRL = 'ctrl'

        class ctrl:
            CHANGEVOL = "changevol"
            CHANGEPOS = "changepos"
            PLAY = 'play'
            PAUSE = 'pause'
            STOP = 'stop'

        class data:
            LIST = 'list'
            ALBUM = 'album'
            SONG = 'song'

    class yt_dl:
        DWNL = 'download'
