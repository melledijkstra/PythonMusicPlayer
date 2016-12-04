DEBUG = 1

class commands:
    PLAYER = 'mplayer'
    YOUTUBE = 'yt-dl'

    class mplayer:
        CTRL = 'ctrl'

        class ctrl:
            CHANGEVOL = "changevol"
            CHANGEPOS = "changepos"
            PAUSE = 'pause'
            PLAY = 'play'
            STOP = 'stop'

        class data:
            LIST = 'list'
            ALBUM = 'album'
            SONG = 'song'

    class yt_dl:
        DWNL = 'download'
