# -*- coding: utf-8 -*-
import os
import sys
from configparser import ConfigParser

from mpserver.musicserver import MusicServer
from mpserver.tools import printcolor as c
from mpserver.tools import Colors

musicserver = None  # type: musicserver.MusicServer

# Start main program
if __name__ == '__main__':
    # Check if program is run with root privileges, which is needed for socket communication
    try:
        if hasattr(os, 'getuid') and not os.getuid() == 0:
            sys.exit(
                c("root priveleges needed, try restarting with this command: 'sudo python server-v2.py'", Colors.WARNING))
        # Get configuration for the application
        config = ConfigParser(defaults={})
        config.read_file(open('config.ini'))

        musicserver = MusicServer(config)
        # This method will start the server and wait for anyone to connect
        musicserver.serve()
    except KeyboardInterrupt as e:
        print(c("trying to abort program...", Colors.BOLD))
        musicserver.set_listen_state(False)
        musicserver.shutdown()

musicserver.shutdown()
