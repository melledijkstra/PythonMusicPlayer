try:
    from setuptools import setup
except ImportError as e:
    from distutils.core import setup

config = {
    'name': 'MelonMusicPlayer',
    'version': '2.1',
    'description': 'A MusicPlayer which can be controlled by the Android App',
    'author': 'Melle Dijkstra',
    'author_email': 'dev.melle@gmail.com',
    'url': 'https://melledijkstra.nl',
    'download_url': 'https://github.com/MelleDijkstra/PythonMusicPlayer',
    'license': 'MIT',
    'install_requires': [
        'python-vlc>=2.2.6100',
        'tinytag>=0.18.0',
        'typing>=3.6.2',
        'youtube-dl>=2016.12.1'
    ],
    'packages': ['mpserver'],
}

setup(**config)
