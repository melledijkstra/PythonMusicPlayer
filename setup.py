try:
    from setuptools import setup, find_packages
except ImportError as e:
    from distutils.core import setup

__version__ = "3.0.0-alpha"

config = {
    'name': 'melon-music-player',
    'version': __version__,
    'description': 'A MusicPlayer which can be controlled by different controllers',
    'long_description': open('README.md').read(),
    'author': 'Melle Dijkstra',
    'author_email': 'dev.melle@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
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
        'protobuf==3.15.0',
        'mutagen==1.40.0',
    ],
    'packages': find_packages(exclude=['docs', 'tests']),
}

setup(**config)
