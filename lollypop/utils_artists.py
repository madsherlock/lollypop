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

from gi.repository import GLib

from lollypop.logger import Logger
from lollypop.define import App
from lollypop.objects_album import Album


def play_artists(artist_ids, genre_ids):
    """
        Play artists
        @param artist_ids as [int]
        @param genre_ids as [int]
    """
    try:
        if App().player.is_party:
            App().lookup_action("party").change_state(
                GLib.Variant("b", False))
        album_ids = App().albums.get_ids(artist_ids, genre_ids)
        albums = [Album(album_id) for album_id in album_ids]
        App().player.play_albums(albums)
    except Exception as e:
        Logger.error("play_artists(): %s" % e)


def add_artist_to_playback(artist_ids, genre_ids, add):
    """
        Add artist to current playback
        @param artist_ids as [int]
        @param genre_ids as [int]
        @param add as bool
    """
    try:
        if App().settings.get_value("show-performers"):
            album_ids = App().tracks.get_album_ids(artist_ids, genre_ids)
        else:
            album_ids = App().albums.get_ids(artist_ids, genre_ids)
        for album_id in album_ids:
            if add and album_id not in App().player.album_ids:
                App().player.add_album(Album(album_id, genre_ids, artist_ids))
            elif not add and album_id in App().player.album_ids:
                App().player.remove_album_by_id(album_id)
        if len(App().player.album_ids) == 0:
            App().player.stop()
        elif App().player.current_track.album.id\
                not in App().player.album_ids:
            App().player.skip_album()
    except Exception as e:
        Logger.error("add_artist_to_playback(): %s" % e)
    App().player.update_next_prev()