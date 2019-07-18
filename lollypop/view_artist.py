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

from gi.repository import Gtk, Gdk, GLib

from gettext import gettext as _

from lollypop.define import App, ArtSize, ViewType, MARGIN, ArtBehaviour, Type
from lollypop.pop_artwork import ArtworkPopover
from lollypop.objects_album import Album
from lollypop.view_artist_albums import ArtistAlbumsView
from lollypop.view_artist_common import ArtistViewCommon
from lollypop.logger import Logger


class ArtistView(ArtistAlbumsView, ArtistViewCommon):
    """
        Show artist albums and tracks
    """

    def __init__(self, genre_ids, artist_ids, view_type):
        """
            Init ArtistView
            @param genre_ids as [int]
            @param artist_ids as [int]
            @param view_type as ViewType
        """
        ArtistAlbumsView.__init__(self, artist_ids, genre_ids, view_type)
        self.__art_signal_id = None
        self.__allocation_timeout_id = None
        self.__width = 0
        self.__show_artwork = len(artist_ids) == 1 and\
            App().settings.get_value("artist-artwork")
        ArtistViewCommon.__init__(self)
        self._overlay.add_overlay(self._banner)
        if self.__show_artwork:
            self._title_label.get_style_context().add_class("text-xx-large")
        else:
            self._title_label.get_style_context().add_class("text-x-large")
        self._box.set_margin_start(MARGIN)
        self._box.set_margin_end(MARGIN)
        self.__set_artwork()
        if view_type & ViewType.SCROLLED:
            self._scrolled.get_vscrollbar().set_margin_top(self._banner.height)
        if len(self._artist_ids) > 1:
            self._banner.collapse(True)

    def populate(self):
        """
            Populate view
        """
        def on_load(items):
            ArtistAlbumsView.populate(self, items)

        def load():
            if App().settings.get_value("show-performers"):
                items = App().tracks.get_album_ids(self._artist_ids,
                                                   self._genre_ids)
            else:
                items = App().albums.get_ids(self._artist_ids,
                                             self._genre_ids)
            return [Album(album_id, self._genre_ids, self._artist_ids)
                    for album_id in items]

        App().task_helper.run(load, callback=(on_load,))

    def activate_child(self):
        """
            Activated typeahead row
        """
        try:
            if App().player.is_party:
                App().lookup_action("party").change_state(
                    GLib.Variant("b", False))
            for child in self.filtered:
                style_context = child.get_style_context()
                if style_context.has_class("typeahead"):
                    if hasattr(child, "album"):
                        App().player.play_album(child.album)
                    else:
                        track = child.track
                        App().player.add_album(track.album)
                        App().player.load(track.album.get_track(track.id))
                style_context.remove_class("typeahead")
        except Exception as e:
            Logger.error("ArtistView::activate_child: %s" % e)

    def jump_to_current(self):
        """
            Jump to current album
        """
        widget = None
        for child in self._box.get_children():
            if child.album.id == App().player.current_track.album.id:
                widget = child
                break
        if widget is not None:
            y = widget.get_current_ordinate(self._box)
            self._scrolled.get_vadjustment().set_value(y)

    @property
    def args(self):
        """
            Get default args for __class__, populate() plus sidebar_id and
            scrolled position
            @return ({}, int, int)
        """
        if self._view_type & ViewType.SCROLLED:
            position = self._scrolled.get_vadjustment().get_value()
        else:
            position = 0
        view_type = self._view_type & ~self.view_sizing_mask
        return ({"genre_ids": self._genre_ids,
                 "artist_ids": self._artist_ids,
                 "view_type": view_type},
                self._sidebar_id, position)

#######################
# PROTECTED           #
#######################
    def _on_value_changed(self, adj):
        """
            Update scroll value and check for lazy queue
            @param adj as Gtk.Adjustment
        """
        ArtistAlbumsView._on_value_changed(self, adj)
        title_style_context = self._title_label.get_style_context()
        if adj.get_value() == adj.get_lower() and self.__show_artwork:
            self._artwork.show()
            self._banner.collapse(False)
            title_style_context.remove_class("text-x-large")
            title_style_context.add_class("text-xx-large")
        else:
            self._banner.collapse(True)
            self._artwork.hide()
            title_style_context.remove_class("text-xx-large")
            title_style_context.add_class("text-x-large")
        if self._view_type & ViewType.SCROLLED:
            self._scrolled.get_vscrollbar().set_margin_top(self._banner.height)

    def _on_label_realize(self, eventbox):
        """
            Change cursor on label
            @param eventbox as Gtk.EventBox
        """
        try:
            if len(self._artist_ids) == 1:
                eventbox.get_window().set_cursor(
                    Gdk.Cursor(Gdk.CursorType.HAND2))
        except:
            Logger.warning(_("You are using a broken cursor theme!"))

    def _on_artwork_box_realize(self, eventbox):
        """
            Change cursor on image
            @param eventbox as Gtk.EventBox
        """
        try:
            eventbox.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
        except:
            Logger.warning(_("You are using a broken cursor theme!"))

    def _on_image_button_release(self, eventbox, event):
        """
            Show artist artwork manager
            @param eventbox as Gtk.EventBox
            @param event as Gdk.Event
        """
        if self._artist_ids:
            pop = ArtworkPopover(self._artist_ids[0])
            pop.set_relative_to(eventbox)
            pop.show()

    def _on_jump_button_clicked(self, button):
        """
            Scroll to album
            @parma button as Gtk.Button
        """
        self.jump_to_current()

    def _on_current_changed(self, player):
        """
            Set playing button status
            @param player as Player
        """
        ArtistAlbumsView._on_current_changed(self, player)
        self.__update_jump_button()

    def _on_populated(self, widget, idle_id):
        """
            Set jump button state
            @param widget as AlbumDetailedWidget
            @param idle_id as int
        """
        self.__update_jump_button()
        ArtistAlbumsView._on_populated(self, widget, idle_id)

    def _on_map(self, widget):
        """
            Connect signals and set active ids
            @param widget as Gtk.Widget
        """
        def on_populated(selection_list, ids):
            selection_list.disconnect_by_func(on_populated)
            selection_list.select_ids(ids, False)

        ArtistAlbumsView._on_map(self, widget)
        self.__on_album_changed(App().player)
        self.__art_signal_id = App().art.connect(
                                           "artist-artwork-changed",
                                           self.__on_artist_artwork_changed)
        self.__party_signal_id = App().player.connect(
                                                "party-changed",
                                                self.__on_album_changed)
        self.__added_signal_id = App().player.connect(
                                                "album-added",
                                                self.__on_album_changed)
        self.__removed_signal_id = App().player.connect(
                                                  "album-removed",
                                                  self.__on_album_changed)
        if self._sidebar_id == Type.ARTISTS_LIST:
            App().window.container.list_view.connect("populated",
                                                     on_populated,
                                                     self._artist_ids)

    def _on_unmap(self, widget):
        """
            Disconnect signals
            @param widget as Gtk.Widget
        """
        ArtistAlbumsView._on_unmap(self, widget)
        if self.__art_signal_id is not None:
            App().art.disconnect(self.__art_signal_id)
            self.__art_signal_id = None
        if self.__party_signal_id is not None:
            App().player.disconnect(self.__party_signal_id)
            self.__party_signal_id = None
        if self.__added_signal_id is not None:
            App().player.disconnect(self.__added_signal_id)
            self.__added_signal_id = None
        if self.__removed_signal_id is not None:
            App().player.disconnect(self.__removed_signal_id)
            self.__removed_signal_id = None

    def _on_adaptive_changed(self, window, status):
        """
            Update banner style
            @param window as Window
            @param status as bool
        """
        if status:
            App().window.container.show_view(
                self._genre_ids, self._artist_ids, True)
            # Destroy after any animation
            GLib.idle_add(self.destroy, priority=GLib.PRIORITY_LOW)
        if self.__show_artwork:
            self._box.set_margin_top(self._banner.height + MARGIN)
        else:
            self._box.set_margin_top(self._banner.height)

#######################
# PRIVATE             #
#######################
    def __set_artwork(self):
        """
            Set artist artwork
        """
        if self.__show_artwork:
            self._artwork.set_margin_start(MARGIN)
            artist = App().artists.get_name(self._artist_ids[0])
            self._box.set_margin_top(self._banner.height + MARGIN)
            App().art_helper.set_artist_artwork(
                                        artist,
                                        ArtSize.BANNER,
                                        ArtSize.BANNER,
                                        self.get_scale_factor(),
                                        ArtBehaviour.ROUNDED |
                                        ArtBehaviour.CROP_SQUARE |
                                        ArtBehaviour.CACHE,
                                        self.__on_artist_artwork)
        else:
            self._title_label.set_margin_start(MARGIN)
            self._banner.collapse(True)
            self._box.set_margin_top(self._banner.height)

    def __update_jump_button(self):
        """
            Update jump button status
        """
        found = False
        for child in self.children:
            if child.album.id == App().player.current_track.album.id:
                found = True
                break
        if found:
            self._jump_button.set_sensitive(True)
        else:
            self._jump_button.set_sensitive(False)

    def __on_album_changed(self, player, album_id=None):
        """
            Update icon
            @param player as Player
            @param album_id as int
        """
        albums = App().albums.get_ids(self._artist_ids, self._genre_ids)
        album_ids = App().player.album_ids
        self._update_icon(len(set(albums) & set(album_ids)) != len(albums))

    def __on_artist_artwork_changed(self, art, prefix):
        """
            Update artwork if needed
            @param art as Art
            @param prefix as str
        """
        artist = App().artists.get_name(self._artist_ids[0])
        if prefix == artist:
            self._artwork.clear()
            self.__set_artwork()

    def __on_artist_artwork(self, surface):
        """
            Set artist artwork
            @param surface as cairo.Surface
        """
        if surface is None:
            self._artwork.get_style_context().add_class("artwork-icon")
            self._artwork.set_size_request(ArtSize.BANNER,
                                           ArtSize.BANNER)
            self._artwork.set_from_icon_name(
                                              "avatar-default-symbolic",
                                              Gtk.IconSize.DIALOG)
        else:
            self._artwork.get_style_context().remove_class("artwork-icon")
            self._artwork.set_from_surface(surface)
        self._artwork.show()
