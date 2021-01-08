# Copyright (c) 2014-2021 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import Gtk, Gdk

from lollypop.define import App, MARGIN_SMALL


class TypeAheadWidget(Gtk.Revealer):
    """
        Type ahead widget
    """

    def __init__(self):
        """
            Init widget
        """
        Gtk.Revealer.__init__(self)
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.show()
        box.set_margin_start(MARGIN_SMALL)
        box.set_margin_end(MARGIN_SMALL)
        box.set_margin_top(MARGIN_SMALL)
        box.set_margin_bottom(MARGIN_SMALL)
        grid = Gtk.Grid.new()
        grid.show()
        grid.set_hexpand(True)
        grid.set_halign(Gtk.Align.CENTER)
        grid.get_style_context().add_class("linked")
        self.__entry = Gtk.Entry.new()
        self.__entry.show()
        self.__entry.connect("activate", self.__on_type_ahead_activate)
        self.__entry.connect("changed", self.__on_type_ahead_changed)
        self.__entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY,
                                             "edit-find-symbolic")
        self.__next_button = Gtk.Button.new_from_icon_name("go-down-symbolic")
        self.__next_button.show()
        self.__prev_button = Gtk.Button.new_from_icon_name("go-up-symbolic")
        self.__prev_button.show()
        self.__close_button = Gtk.Button.new_from_icon_name(
            "window-close-symbolic")
        self.__close_button.show()
        self.__close_button.set_halign(Gtk.Align.END)
        self.__next_button.connect(
            "clicked", lambda x: self.__search_next()
        )
        self.__prev_button.connect(
            "clicked", lambda x: self.__search_prev()
        )
        self.__close_button.connect(
            "clicked", lambda x: self.set_reveal_child(False)
        )
        grid.attach(self.__entry, 0, 0, 1, 1)
        grid.attach(self.__prev_button, 1, 0, 1, 1)
        grid.attach(self.__next_button, 2, 0, 1, 1)
        box.append(grid)
        box.append(self.__close_button)
        self.set_child(box)
        self.__controller = Gtk.EventControllerKey.new()
        self.__entry.add_controller(self.__controller)
        self.__controller.connect("key-pressed", self.__on_key_pressed)
        self.__controller.connect("key-released", self.__on_key_released)

    @property
    def entry(self):
        """
            Get popover entry
            @return Gtk.Entry
        """
        return self.__entry

#######################
# PRIVATE             #
#######################
    def __search_prev(self):
        """
            Search previous item
        """
        view = App().window.container.focused_view
        if view is not None:
            view.search_prev(self.__entry.get_text())

    def __search_next(self):
        """
            Search next item
        """
        view = App().window.container.focused_view
        if view is not None:
            view.search_next(self.__entry.get_text())

    def __on_key_pressed(self, event_controller, keyval, keycode, state):
        """
            Handle keys
            @param event_controller as Gtk.EventController
            @param keyval as int
            @param keycode as int
            @param state as Gdk.ModifierType
        """
        if keyval == Gdk.KEY_Up or keyval == Gdk.KEY_Down:
            return True
        elif keyval == Gdk.KEY_Escape:
            App().window.container.show_filter()

    def __on_key_released(self, event_controller, keyval, keycode, state):
        """
            Handle keys
            @param event_controller as Gtk.EventController
            @param keyval as int
            @param keycode as int
            @param state as Gdk.ModifierType
        """
        if keyval == Gdk.KEY_Up:
            self.__search_prev()
        elif keyval == Gdk.KEY_Down:
            self.__search_next()

    def __on_type_ahead_changed(self, entry):
        """
            Filter current widget
            @param entry as Gtk.entry
        """
        view = App().window.container.focused_view
        if view is not None:
            view.search_for_child(entry.get_text())

    def __on_type_ahead_activate(self, entry):
        """
            Activate row
            @param entry as Gtk.Entry
        """
        view = App().window.container.focused_view
        if view is not None:
            view.activate_child()
