# Copyright (c) 2014-2019 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import GLib, Gio

from gettext import gettext as _

from lollypop.helper_web_youtube import YouTubeHelper
from lollypop.define import App
from lollypop.utils import create_dir, escape


class WebHelper:
    """
        Web helper
    """

    __WEB_CACHE = GLib.get_user_cache_dir() + "/lollypop_web"

    def __init__(self):
        """
            Init helper
        """
        create_dir(self.__WEB_CACHE)
        self.__helpers = [YouTubeHelper()]

    def set_uri(self, track, cancellable):
        """
            Set uri for track
            @param cancellable as Gio.Cancellable
        """
        if track.is_http:
            return
        for helper in self.__helpers:
            uri = helper.get_uri(track, cancellable)
            if uri:
                App().tracks.set_uri(track.id, uri)
                track.set_uri(uri)
                return

    def get_local_path(self, track):
        """
            Get local file path
            @return str
        """
        dirname = "%s/%s" % (escape(",".join(track.artists)),
                             escape(track.album.name))
        create_dir("%s/%s" % (self.__WEB_CACHE, dirname))
        return "%s/%s/%s.mp3" % (self.__WEB_CACHE,
                                 dirname,
                                 escape(track.name))

    def download_track_content(self, track):
        """
            Download track content to cache
            @param track as Track
        """
        filepath = self.get_local_path(track)
        f = Gio.File.new_for_path(filepath)

        for helper in self.__helpers:
            if f.query_exists():
                return
            helper.download_uri_content(track, filepath)
            if GLib.find_program_in_path("flatpak-spawn") is not None:
                argv = ["flatpak-spawn", "--host", "kid3-cli",
                        "-c", "set title '%s'" % track.name,
                        "-c", "set album '%s'" % track.album.name,
                        "-c", "set artist '%s'" % ";".join(track.artists),
                        filepath,
                        None]
            else:
                argv = ["kid3-cli",
                        "-c", "set title '%s'" % track.name,
                        "-c", "set album '%s'" % track.album.name,
                        "-c", "set artist '%s'" % ";".join(track.artists),
                        filepath,
                        None]
            (s, o, e, s) = GLib.spawn_sync(None,
                                           argv,
                                           None,
                                           GLib.SpawnFlags.SEARCH_PATH,
                                           None)
            if f.query_exists():
                App().tracks.set_uri(track.id, "file://" + filepath)
            elif App().notify is not None:
                App().notify.send(_("Can't download %s") % track.name)

    def get_track_content(self, track):
        """
            Get content uri
            @param track as Track
            @return content uri as str
        """
        for helper in self.__helpers:
            uri = helper.get_uri_content(track)
            if uri:
                return uri
        return ""
