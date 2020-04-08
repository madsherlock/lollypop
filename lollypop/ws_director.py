# Copyright (c) 2014-2017 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gio, GLib

# from lollypop.utils import get_network_available
from lollypop.define import NetworkAccessACL, App, Type
from lollypop.logger import Logger


class DirectorWebService:
    """
        Manage web services
    """

    def __init__(self):
        """
            Init object
        """
        self.__spotify_ws = None
        self.__spotify_timeout_id = None
        App().settings.connect("changed::network-access-acl",
                               self.__on_network_access_acl_changed)
        self.__on_network_access_acl_changed()

    def stop(self):
        """
            Stop all web services
            @return bool
        """
        stopped = True
        if self.__spotify_ws.is_running:
            self.__spotify_ws.stop()
            Logger.info("Spotify web service stopped")
            stopped = False
        return stopped

    @property
    def spotify_ws(self):
        """
            Get Spotify web service
            @return SpotifyWebService
        """
        return self.__spotify_ws

#######################
# PRIVATE             #
#######################
    def __handle_spotify(self, acl):
        """
            Update Spotify based on acl
            @param acl as int
        """
        show_album_lists = App().settings.get_value("shown-album-lists")
        if Type.SUGGESTIONS in show_album_lists and\
                acl & NetworkAccessACL["SPOTIFY"] and\
                self.__spotify_timeout_id is None:
            from lollypop.ws_spotify import SpotifyWebService
            self.__spotify_ws = SpotifyWebService()
            Logger.info("Spotify web service started")
            self.__spotify_ws.start()
            self.__spotify_timeout_id = GLib.timeout_add_seconds(
                3600, self.__spotify_ws.start)
        else:
            if self.__spotify_timeout_id is not None:
                GLib.source_remove(self.__spotify_timeout_id)
                self.__spotify_timeout_id = None
            self.__spotify_ws.stop()
            self.__spotify_ws.destroy()
            self.__spotify_ws = None
            Logger.info("Spotify web service stopped")

    def __on_network_access_acl_changed(self, *ignore):
        """
            Update available webservices
        """
        monitor = Gio.NetworkMonitor.get_default()
        if monitor.get_network_metered():
            network_acl = 0
        else:
            network_acl = App().settings.get_value(
                "network-access-acl").get_int32()
        self.__handle_spotify(network_acl)
