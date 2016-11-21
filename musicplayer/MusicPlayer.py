import vlc

class MusicPlayer:
    """ This class can play music with the pygame library
        it keeps track of which file it is playing and has play, pause, etc. controls
        Also it has a list of files it can play
    """

    def __init__(self):
        self.v = vlc.Instance()
        self._player = self.v.media_player_new()
        self._player.audio_set_volume(80)
        self._albums = []

    def get_albums_and_songs(self, rootdir):
        """ Get albums and song from a specific folder and generates a dictionary from it

        :param rootdir:
        :return:
        """
        albums = self.album_list_from_folder(rootdir)
        for album in albums:
            album['songlist'] = self.music_list_from_folder(album['location'])
            print(album)
        return albums

    def album_list_from_folder(self, rootname):
        """ Generates a list of albums from specific directory
            every folder in the specified directory counts a an album.
            A list with dictionaries like this will be returned:
            Example:
            [ {'name': "House", 'location': "/music/House", song_count: 13},
            {name': "Rap", 'location': "/music/rap"} ]

        :param rootname:
        :return list:
        """
        albums = []

        if os.path.isdir(rootname):
            for selfdir, subdirs, files in os.walk(rootname):
                album = {'name': selfdir.split("\\")[-1], 'location': selfdir}
                song_count = 0
                for extension in allowed_extensions:
                    song_count += len(glob.glob1(selfdir, "*." + extension))
                album['song_count'] = song_count
                albums.append(album)

        self._albums = albums
        return albums

    def music_list_from_folder_recursive(self, rootdir):
        """ Sets internal musiclist of FileManager instance, and returns that list with music names in the directory specified.
            currently searches for ".mp3", ".wav"

            Returns a list with dictionaries
            like so: musiclist[{"name":"Best Music by someone","file":"path/to/file.mp3"}]

            :param rootdir: Folder to search for music files
            :type rootdir: str
            :return: The list with all music names in the specified folder
            :rtype: list
        """
        musiclist = []
        if os.path.isdir(rootdir):
            for subdir, dirs, files in os.walk(rootdir):
                for musicfile in files:
                    if musicfile.endswith(allowed_extensions):
                        musiclist.append(
                            {"name": os.path.splitext(musicfile)[0], "file": subdir + "\\" + musicfile})
            # update instance musiclist and also return it
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def play(self, song_id):
        song = self._musiclist[song_id]
        print(
            "Trying to play " + c.OKGREEN + song['name'] + c.CLEAR + " with id: " + c.OKGREEN + str(
                song_id) + c.CLEAR
        )
        self._current_song = v.media_new(song['file'].encode('utf-8', 'replace'))
        self._current_song.parse()
        print("\tDuration: " + str(self._current_song.get_duration()))
        self._player.set_media(self._current_song)
        self._player.play()
        pre_info = {"cur_song": song_id, "length": self._current_song.get_duration()}
        print("\tsending pre_info: " + json.dumps(pre_info))
        conn.sendall(json.dumps(pre_info) + "\n")
        while not self._player.is_playing():
            continue
        self.updateSongInfoThread = UpdateSongInfoThread(self._player)
        self.updateSongInfoThread.start()

    def change_vol(self, vol):
        """
        Change the volume of the musicplayer
        :param float vol:
        :return:
        """
        # TODO: send confirmation that volume changed
        if type(vol) is int:
            new_vol = tools.constrain(vol, 0, 100)
        elif vol == "down":
            new_vol = tools.constrain(self._player.audio_get_volume() - 3, 0, 100)
        elif vol == "up":
            new_vol = tools.constrain(self._player.audio_get_volume() + 3, 0, 100)
        else:
            print("volume type not accepted (" + str(vol) + ")")
            return
        print("Setting volume to: " + str(new_vol))
        self._player.audio_set_volume(new_vol)

    def change_pos(self, pos):
        # TODO: change position of song and send update
        self._player.set_time(tools.constrain(pos, 0, self._player.get_media().get_duration()))
        if not self._player.is_playing():
            self._player.play()

    def pause(self):
        if self._player.is_playing():
            self._player.pause()
        elif self._player.get_time() < self._player.get_media().get_duration():
            print(str(self._player.get_time()) + " - " + str(self._player.get_media().get_duration()))
            self._player.pause()
            self.updateSongInfoThread = UpdateSongInfoThread(self._player)
            self.updateSongInfoThread.start()

    def stop(self):
        self._player.stop()
        self._current_song = None

    def music_list_from_folder(self, rootdir):
        """ returns a list with music names in the directory specified.
            see allowed_extensions in config file for allowed extensions

            Returns a list with dictionaries
            like so: musiclist[{"name":"Best Music by someone","file":"path/to/file.mp3"}]

            :param rootdir: Folder to search for music files
            :type rootdir: str
            :return: The list with all music names in the specified folder
            :rtype: list
        """
        musiclist = []
        if os.path.isdir(rootdir):
            for musicfile in os.listdir(rootdir):
                if musicfile.endswith(allowed_extensions):
                    musiclist.append({"name": os.path.splitext(musicfile)[0], "file": rootdir + "\\" + musicfile})
            # update instance musiclist and also return it
            return musiclist
        else:
            raise IOError("Folder '" + rootdir + "' does not exist!")

    def music_list_from_album(self, albumid):
        # TODO create this functionality. A song list from an album should be generated
        if len(self._albums) > albumid >= 0:
            return self.music_list_from_folder(self._albums[albumid]['location'])
        else:
            raise IndexError('This album doesn\'t exists')

    def init(self):
        """ Initializing musicplayer, scanning directory for albums and song, etc. """
        self._albums = self.album_list_from_folder(MUSIC_DIR)

    def get_album_by_id(self, albumid):
        """
        Get an album by ID

        :param int albumid:
        :return:
        :rtype: dict
        """
        return self._albums[albumid] if len(self._albums) > albumid > 0 else False