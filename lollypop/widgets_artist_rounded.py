# Copyright (c) 2014-2018 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import Gdk, Gtk

from gettext import gettext as _
from random import shuffle

from lollypop.define import App, STATIC_ALBUM_NAME
from lollypop.utils import get_icon_name
from lollypop.objects import Album
from lollypop.widgets_flowbox_rounded import RoundedFlowBoxWidget
from lollypop.helper_art import ArtHelper


class RoundedArtistWidget(RoundedFlowBoxWidget):
    """
        Artist photo or artist's albums in a rounded widget
    """

    def __init__(self, artist_id, art_size):
        """
            Init widget
            @param artist_id as int
            @param art_size as int
        """
        RoundedFlowBoxWidget.__init__(self, artist_id, art_size)
        self.__artist_name = ""
        self.__art_helper = ArtHelper()
        self._artwork.connect("notify::surface", self.__on_artwork_set)
        self._artwork.connect("notify::icon-name", self.__on_artwork_set)
        self.connect("realize", self.__on_realize)

    def populate(self):
        """
            Populate widget content
        """
        if self._data < 0:
            self.__artist_name = _(STATIC_ALBUM_NAME[self._data])
        else:
            self.__artist_name = App().artists.get_name(self._data)
        RoundedFlowBoxWidget.populate(self, self.__artist_name)

    def show_overlay(self, show):
        """
            Show overlay
            @param show as bool
        """
        pass

    def set_filtered(self, b):
        """
            Set widget filtered
        """
        self.__filtered = b

    def set_artwork(self):
        """
            Set artist artwork
        """
        self._set_artwork()

    @property
    def artist_name(self):
        """
            Get artist name
            @return str
        """
        return self.__artist_name

    @property
    def is_overlay(self):
        """
            True if widget is overlayed
            @return bool
        """
        return False

    @property
    def filtered(self):
        """
            True if filtered by parent
        """
        return self.__filtered

    @property
    def filter(self):
        return App().artists.get_name(self._data).lower()

#######################
# PROTECTED           #
#######################
    def _set_artwork(self):
        """
            Set artist artwork
        """
        if self._data < 0:
            icon_name = get_icon_name(self._data) or "avatar-default-symbolic"
            self._artwork.set_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
            self.emit("populated")
            self._artwork.get_style_context().add_class("artwork-icon-large")
        elif App().settings.get_value("artist-artwork"):
            self.__art_helper.set_artist_artwork(self._artwork,
                                                 self.__artist_name,
                                                 self._art_size,
                                                 self._art_size,
                                                 self._scale_factor)
        else:
            album_ids = App().albums.get_ids([self._data], [])
            shuffle(album_ids)
            self.__art_helper.set_album_artwork(self._artwork,
                                                Album(album_ids[0]),
                                                self._art_size,
                                                self._art_size,
                                                self._scale_factor)

#######################
# PRIVATE             #
#######################
    def __on_realize(self, widget):
        """
            Change cursor over eventbox
            @param widget as Gtk.Widget
        """
        window = widget.get_window()
        if window is not None:
            window.set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))

    def __on_artwork_set(self, helper):
        """
            Finish widget initialisation
            @param helper as ArtHelper
        """
        if self._artwork.props.surface is None:
            self._artwork.get_style_context().add_class("artwork-icon")
        self.emit("populated")
