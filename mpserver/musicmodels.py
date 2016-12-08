from abc import abstractmethod
from typing import List


class Dictable:
    """
    This class makes sure the extended class is able to represent as a dictionary which in turn can be used to generate
    a json representation of this class. Which then also can be used to transfer over a network
    """

    @abstractmethod
    def toDict(self, verbose=False) -> dict:
        """
        This method makes a dictionary from this class

        :param verbose: verbose means that every collection this class is also generated to dict and put into the dictionary
        :type verbose: bool
        :return: this class as dictionary
        :rtype: dict
        """
        return {}

    def __repr__(self):
        return str(self.toDict(False))


class Song(Dictable):
    """
    A song model which is used to store song information
    """

    def __init__(self, title: str, filepath: str):
        self.id = id(self)
        self.title = title
        self.filepath = filepath

    def toDict(self, verbose=False) -> dict:
        return {'id': self.id, 'title': self.title}


class Album(Dictable):
    """ Album class which is used to store album information """

    def __init__(self, title: str, location: str):
        # // TODO: document these classes
        """
        :param title:
        :param location:
        """
        self.id = id(self)
        self.title = title
        self.location = location
        self.songlist = []  # type: List[Song]

    def getsong(self, ID):
        """
        Gets a song from this album by ID or False if not found
        :rtype: Song
        """
        return self.songlist[ID] if len(self.songlist) >= id > 0 else None

    def getsonglist(self) -> List[Song]:
        return self.songlist

    def set_song_list(self, songlist: list):
        self.songlist = songlist

    def toDict(self, verbose=False) -> dict:
        retdict = {'id': self.id, 'title': self.title, 'location': self.location}
        if verbose:
            for song in self.songlist:
                retdict['songlist'] = song.toDict(verbose)
        else:
            retdict['songcount'] = len(self.songlist)
        return retdict

    def get_songlist(self):
        return self.songlist
