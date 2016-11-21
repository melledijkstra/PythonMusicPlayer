class Album:
    """ Album class which is used to store album information """

    def __init__(self):
        self.songlist = []

    def getsong(self, ID):
        """
        Gets a song from this album by ID or False if not found
        :rtype: Song
        """
        return self.songlist[ID] if len(self.songlist) >= id > 0 else False

