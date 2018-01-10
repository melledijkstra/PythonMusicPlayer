DEBUG = 1


class Commands:
    PLAYER = 'mplayer'
    YOUTUBE = 'yt-dl'

    class MPlayer:
        CTRL = 'ctrl'

        class Control:
            CHANGEVOL = "changevol"
            CHANGEPOS = "changepos"
            PAUSE = 'pause'
            PLAY = 'play'
            STOP = 'stop'

        class Data:
            LIST = 'list'
            ALBUM = 'album'
            SONG = 'song'

    class YTDL:
        DWNL = 'download'
