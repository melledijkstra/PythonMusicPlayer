import json
from configparser import RawConfigParser

from mpserver.musicplayer import MusicPlayer

# Get configuration for the application
config = RawConfigParser(defaults={})
config.read_file(open('config.ini'))
musicplayer = MusicPlayer(RawConfigParser(config))

if __name__ == '__main__':
    cmd = None
    while True:
        try:
            cmd = input('cmd: ')
            if cmd == 'quit':
                break
            msg = json.loads(cmd)
            response = musicplayer.process_message(msg)
            print(response)
        except json.JSONDecodeError as e:
            print('invalid json')
            print(e)
