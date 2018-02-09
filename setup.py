try:
    from setuptools import setup
except ImportError as e:
    from distutils.core import setup

__version__ = "3"

config = {
    'name': 'MelonMusicPlayer',
    'version': __version__,
    'description': 'A MusicPlayer which can be controlled by the Android App',
    'author': 'Melle Dijkstra',
    'author_email': 'dev.melle@gmail.com',
    'url': 'https://melledijkstra.nl',
    'download_url': 'https://github.com/MelleDijkstra/PythonMusicPlayer',
    'license': 'MIT',
    'install_requires': [
        'typing==3.6.4',
        'youtube_dl==2016.12.1',
        'python_vlc==3.0.101',
        'setuptools==38.4.0',
        'tinytag==0.18.0',
        'grpcio==1.8.4',
        'grpcio-tools==1.8.4',
        'protobuf==3.5.1',
        'mutagen==1.40.0',
    ],
    'packages': ['mpserver'],
}

setup(**config)
