import unittest
import os
from ConfigParser import SafeConfigParser


class TestApplicationConfiguration(unittest.TestCase):

    configfile = '../config.ini'

    def setUp(self):
        # first test if config file is present
        self.test_config_file_is_present()
        # load configuration for tests
        self.config = SafeConfigParser()
        self.config.readfp(open(self.configfile))

    def test_config_file_is_present(self):
        self.assertEqual(os.path.isfile(self.configfile), True, "Config file not present! create one if possible")

    def test_socket_configuration(self):
        port = self.config.get('socket', 'port')
        self.assertTrue(port.isdigit(), "Port should be a number, port = "+str(port))
        self.assertTrue(len(str(port)) == 4, "Port should be 4 numbers long")


if __name__ == '__main__':
    unittest.main()
