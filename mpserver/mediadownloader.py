from configparser import RawConfigParser

import youtube_dl

from mpserver.grpc import mmp_pb2_grpc as rpc
from mpserver.grpc import mmp_pb2

from mpserver.interfaces import Logger, EventFiring


class MediaDownloader(rpc.MediaDownloaderServicer, Logger, EventFiring):
    """
    Wrapper for the youtube_dl.YoutubeDL so it can be used in the mpserver package
    """

    _section = 'mediadownloader'

    def __init__(self, config: RawConfigParser):
        super(MediaDownloader, self).__init__()
        self._config = config
        # TODO: make some of these options available in ini file
        self._options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'logger': self.YTDLLogger(),
            'progress_hooks': [self.__download_hook],
        }
        self.__process_conf()

    def download(self, url, location):
        with youtube_dl.YoutubeDL(self._options) as ytdl:
            ytdl.download([url])

    def process_message(self, message: dict) -> dict:
        """
        Process the message and return a response

        :param message: the message to process
        :type message: dict
        :return: returns a response as type dictionary
        :rtype: dict
        """
        retdict = {'result': 'ok'}

        if 'cmd' in message:
            # DOWNLOAD
            if message['cmd'] == 'download':
                if 'albumid' in message and 'url' in message:
                    self.download(message['url'], )
                else:
                    retdict['result'] = 'error'
                    retdict['message'] = 'no albumid or url given'
        else:
            retdict['result'] = 'error'
            retdict['toast'] = 'Sorry, could not handle request'
        return retdict

    def __download_hook(self, info):
        self._latest_status = info
        if info['status'] == 'downloading':
            self._fire_event(self.Events.DOWNLOAD_UPDATE)
        elif info['status'] == 'finished':
            self._fire_event(self.Events.DOWNLOAD_FINISHED)

    class Events:
        DOWNLOAD_FINISHED = 1
        DOWNLOAD_UPDATE = 0

    class YTDLLogger:

        def debug(self, msg):
            # print(msg)
            pass

        def warning(self, msg):
            # print(msg)
            pass

        def error(self, msg):
            print(msg)

    def __process_conf(self):
        self._raw_download_location = self._config.get(self._section, 'download_location',
                                                       fallback='{{album}}/%(title)s.%(ext)s')
        self.log('raw_download_location: ' + self._raw_download_location)

    def DownloadMedia(self, request, context):
        return super().DownloadMedia(request, context)

    def RetrieveMDStatus(self, request, context):
        return super().RetrieveMDStatus(request, context)

    def NotifyMDStatus(self, request, context):
        return super().NotifyMDStatus(request, context)


