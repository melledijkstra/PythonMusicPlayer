import os
import unittest
from configparser import RawConfigParser

from mpserver.musicserver import MusicServer


class TestApplicationConfiguration(unittest.TestCase):
    configfile = '../config.ini'

    def setUp(self):
        # first test if config file is present
        self.test_config_file_is_present()
        # load configuration for tests
        self.config = RawConfigParser()
        with open(self.configfile, 'r') as file:
            self.config.read_file(file)

    def test_config_file_is_present(self):
        self.assertEqual(os.path.isfile(self.configfile), True, "Config file not present! you should create one "
                                                                "according to the github repository")

    def test_socket_configuration(self):
        port = self.config.get(MusicServer._config_section, 'port')
        self.assertTrue(port.isdigit(), "Port should be a number, port = " + str(port))
        self.assertTrue(0 < int(port) < 65535, "Port should be a valid port number")


if __name__ == '__main__':
    unittest.main()
