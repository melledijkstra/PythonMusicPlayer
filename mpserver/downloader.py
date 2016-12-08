import youtube_dl


class YoutubeDownloader():
    """
    Wrapper for the youtube_dl.YoutubeDL so it can be used in the mpserver package
    """

    _options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        # 'logger': YTDLLogger(),
        # 'progress_hooks': [my_hook],
    }

    def __init__(self):
        self._ytdl = youtube_dl.YoutubeDL()

    def status(self):
        # get download queue and progress of each download
        pass

    def download(self, url, location):
        pass

    def process_message(self, message: dict) -> dict:
        """
        Process the message and return a response

        :param message: the message to process
        :type message: dict
        :return: returns a response as type dictionary
        :rtype: dict
        """
        retdict = {'result': 'ok'}
        return retdict
