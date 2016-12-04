# Python Music Player

## Introduction

This repository contains a python music player which acts as a server. It uses the vlc python bindings to play the music and socket communication to communicate with the Android Application which can be found [here](https://github.com/MelleDijkstra/AndroidMusicPlayerClient)

## Installation

If you want to run this program you need:

* The actual VLC program which can be found here ([VLC](http://www.videolan.org/vlc/)).
Windows can just install the executable and for linux system it should be as easy as running `$ sudo apt-get install vlc`. **Check their site for correct installation**
* Make sure you have installed python 3.5 or higher. [Python install](https://www.python.org/downloads/)
* Clone the project if you haven't already `git clone https://github.com/MelleDijkstra/PythonMusicPlayer`
* Go to cloned folder `cd PythonMusicPlayer`
* Then run `pip install -r requirements.txt` to install the packages needed
* Change any settings needed in `config.ini`
* Start the music server by running `python server-v2.py`. And then use the application to connect to the server