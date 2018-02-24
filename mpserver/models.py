from abc import abstractmethod
from typing import List

from tinytag import TinyTag

from mpserver.grpc import mmp_pb2 as proto


class Protoble:
    """
    This class makes sure the extended class is able to represent as a protobuf object
    Which then can be used to transfer over a network
    """

    @abstractmethod
    def to_protobuf(self):
        """
        This method makes a protobuf object from this class

        :return: this class as protobuf object
        """
        return None


class SongModel(Protoble):
    """ A song model which is used to store song information """

    def __init__(self, title: str, filepath: str):
        super(SongModel, self).__init__()
        self.id = id(self)
        self.title = title
        self.filepath = filepath
        # This operation can go wrong when another program is using the filepath
        try:
            self._tags = TinyTag.get(self.filepath, False, True)
            self.duration = round(self._tags.duration)
        except PermissionError as e:
            self.duration = None
            print(e)

    def to_protobuf(self) -> proto.Song:
        s = proto.Song()
        s.id = self.id
        s.title = self.title
        s.duration = self.duration
        return s


class AlbumModel(Protoble):
    """ Album class which is used to store album information """

    def __init__(self, title: str, location: str):
        """
        :param title:
        :param location:
        """
        super(AlbumModel, self).__init__()
        self.id = id(self)
        self.title = title
        self.location = location
        self.songlist = []  # type: List[SongModel]

    def getsong(self, song_id: int):
        """
        Gets a song from this album by ID or False if not found
        :rtype: SongModel
        """
        return self.songlist[song_id] if len(self.songlist) >= song_id > 0 else None

    def getsonglist(self) -> List[SongModel]:
        return self.songlist

    def set_song_list(self, songlist: list):
        self.songlist = songlist

    def to_protobuf(self) -> proto.Album:
        a = proto.Album()
        a.id = self.id
        a.title = self.title
        a.song_list.extend([song.to_protobuf() for song in self.songlist])
        return a
