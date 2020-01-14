#!/usr/bin/env python3

import os
import sys
import logging
import logging.handlers
from sys import platform

import dbus
from dbus import DBusException
from typing import List,Tuple

class SpotifySong:
    def __init__(self, trackId: str, length: int, artUrl:str, album: str, albumArtist: List[str], artists: List[str], autoRating: float, discNumber: int, title: str, trackNumber: int, url: str, playbackStatus: str):
        self.trackId: str = trackId
        self.length: int = length
        self.artUrl: str = artUrl
        self.album: str = album
        self.albumArtist: List[str] = [str(x) for x in albumArtist if albumArtist]
        self.artists: List[str] = [str(x) for x in artists if artists]
        self.autoRating: float = autoRating
        self.discNumber: int = discNumber
        self.title: str = title
        self.trackNumber: int = trackNumber
        self.url: str = url
        self.playbackStatus: str = playbackStatus
        self.isPlaying = self.playbackStatus and self.playbackStatus == "Playing"
    def __str__(self):
        return  "trackId: " + self.trackId + os.linesep + \
                "length: " + str(self.length) + os.linesep + \
                "artUrl: " + self.artUrl + os.linesep + \
                "album: " + self.album + os.linesep + \
                "albumArtist: " + ','.join(self.albumArtist) + os.linesep + \
                "artists: " + ','.join(self.artists) + os.linesep + \
                "autoRating: " + str(self.autoRating) + os.linesep + \
                "discNumber: " + str(self.discNumber) + os.linesep + \
                "title: " + self.title + os.linesep + \
                "trackNumber: " + str(self.trackNumber) + os.linesep + \
                "url: " + self.url + os.linesep + \
                "playbackStatus: " + self.playbackStatus + os.linesep + \
                "isPlaying: " + str(self.isPlaying)
class DbusAPI:
    def __init__(self):
        self.session_bus = dbus.SessionBus()

        # Spotify Properties
        self.spotify_bus = None
        self.spotify_properties = None
        self.spotify_is_loaded = False

    def __init_spotify(self):

        try:
            # Load spotify DBUS information
            self.spotify_bus = self.session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
            self.spotify_properties = dbus.Interface(self.spotify_bus, "org.freedesktop.DBus.Properties")
            self.spotify_is_loaded = True
        except DBusException:
            self.spotify_is_loaded = False

    def get_spotify_now_playing(self) -> Tuple[str, SpotifySong]:
        self.__init_spotify()
        if not self.spotify_is_loaded:
            return "Failed to initiate spotify dbus, is spotify running?", None

        try:
            # Attempt to get metadata
            metadata = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            playback_status = self.spotify_properties.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
        except DBusException:
            return "Failed to retrieve spotify metadata, is spotify running?", None

        # Extract information from metadata
        trackId = metadata['mpris:trackid']
        length = metadata['mpris:length']
        artUrl = metadata['mpris:artUrl']
        album = metadata['xesam:album']
        albumArtist = metadata['xesam:albumArtist']
        artists = metadata['xesam:artist']
        autoRating = metadata['xesam:autoRating']
        discNumber = metadata['xesam:discNumber']
        title = metadata['xesam:title']
        trackNumber = metadata['xesam:trackNumber']
        url = metadata['xesam:url']

        return None, SpotifySong(trackId, length, artUrl, album, albumArtist, artists, autoRating, discNumber, title, trackNumber, url, playback_status)
def get_syslog():

    syslogger = logging.getLogger('SysLogger')
    syslogger.setLevel(logging.DEBUG)

    if platform == 'linux' or platform == 'linux2':
        handler = logging.handlers.SysLogHandler(address = '/dev/log')
    elif platform == 'darwin':
        handler = logging.handlers.SysLogHandler(address = '/var/run/syslog')

    syslogger.addHandler(handler)
    return syslogger
if __name__ == "__main__":
# Example usage for i3 bar 
    logger = get_syslog()
    db_api = DbusAPI()
    error, res = db_api.get_spotify_now_playing()
    if error:
        logger.error("Spotipy : {}".format(error))
        sys.exit(1)
    if res.isPlaying:
        print('♫ '+'{} - {}'.format(','.join(res.artists),res.title))
