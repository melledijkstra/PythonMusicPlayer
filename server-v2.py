#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
from configparser import RawConfigParser
from datetime import datetime

from mpserver.musicserver import MusicServer
from mpserver.tools import Colors
from mpserver.tools import colorstring as c

musicserver = None  # type: musicserver.MusicServer

# Start main program
banner = c("\n\tMelonMusicPlayer made by Melle Dijkstra © " + str(datetime.now().year) + "\n", Colors.BLUE)

if __name__ == '__main__':
    # Check if program is run with root privileges, which is needed for socket communication
    try:
        if hasattr(os, 'getuid') and not os.getuid() == 0:
            sys.exit(
                c(
                    "root priveleges needed for the server, try restarting with this command: 'sudo python " + __file__ + "'",
                    Colors.WARNING))

        print(banner)

        # Get configuration for the application
        config = RawConfigParser(defaults={})
        config.read_file(open('config.ini'))

        musicserver = MusicServer(config)
        # This method will start the server and wait for anyone to connect
        musicserver.serve()
    except KeyboardInterrupt as e:
        print(c("trying to abort program...", Colors.BOLD))
        musicserver.set_listen_state(False)
        musicserver.shutdown()

musicserver.shutdown()
