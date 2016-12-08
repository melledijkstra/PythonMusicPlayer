try:
    from setuptools import setup
except ImportError as e:
    from distutils.core import setup

config = {
    'description': 'A MusicPlayer which can be controlled by the Android App',
    'author': 'Melle Dijkstra',
    'url': 'http://melledijkstra.nl',
    'download_url': '',
    'author_email': 'melle210202@gmail.com',
    'version': '1.0',
    'install_requires': ['nose', 'python-vlc'],
    'packages': ['mpserver'],
    'scripts': [],
    'name': 'Melle\'s MusicPlayer'
}

setup(**config)
