from abc import abstractmethod
from typing import List


class Dictable:
    """
    This class makes sure the extended class is able to represent as a dictionary which in turn can be used to generate
    a json representation of this class. Which then also can be used to transfer over a network
    """

    @abstractmethod
    def toDict(self, verbose: bool) -> dict:
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


class Album(Dictable):
    """ Album class which is used to store album information """

    def __init__(self, name: str, location: str):
        # // TODO: document these classes
        """
        :param name:
        :param location:
        """
        self.id = id(self)
        self.name = name
        self.location = location
        self.songlist = []  # type: List[Song]

    def getsong(self, ID):
        """
        Gets a song from this album by ID or False if not found
        :rtype: Song
        """
        return self.songlist[ID] if len(self.songlist) >= id > 0 else None

    def getsonglist(self):
        pass

    def set_song_list(self, songlist: list):
        self.songlist = songlist

    def toDict(self, verbose: bool) -> dict:
        retdict = {'id': self.id, 'name': self.name, 'location': self.location}
        if verbose:
            for song in self.songlist:
                retdict['songlist'] = song.toDict(verbose)
        else:
            retdict['songcount'] =len(self.songlist)
        return retdict



class Song(Dictable):
    """
    A song model which is used to store song information
    """

    def __init__(self, name: str, location: str):
        self.id = id(self)
        self.name = name
        self.location = location

    def toDict(self, verbose) -> dict:
        return {'id': self.id, 'name': self.name, 'location': self.location}
