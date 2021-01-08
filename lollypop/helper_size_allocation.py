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

from gi.repository import GLib


class SizeAllocationHelper:
    """
        Handle widget resizing smoothly
    """

    def __init__(self, use_parent=False):
        """
            Init helper
            @param use_parent as bool: follow parent sizing
        """
        self.__resize_timeout_id = None
        self.__width = self.__height = 0
        # FIXME

    @property
    def width(self):
        """
            Get widget width
            @return int
        """
        return self.__width

    @property
    def height(self):
        """
            Get widget height
            @return int
        """
        return self.__height

#######################
# PROTECTED           #
#######################
    def _handle_width_allocate(self, width):
        """
            @param width as int
            @return True if allocation is valid
        """
        # FIXME Check this, does it change with GTK4?
        if width == 1 or self.__width == width:
            return False
        self.__width = width
        return True

    def _handle_height_allocate(self, height):
        """
            @param height as int
            @return True if allocation is valid
        """
        # FIXME Check this, does it change with GTK4?
        if height == 1 or self.__height == height:
            return False
        self.__height = height
        return True

#######################
# PRIVATE             #
#######################
    def __handle_size_allocate(self, width, height):
        """
            Pass resize to width/height handler
            @param width as int
            @param height as int
        """
        self.__resize_timeout_id = None
        self._handle_width_allocate(width)
        self._handle_height_allocate(height)

    def __on_resize(self, widget, width, height):
        """
            Filter unwanted values
            @param widget as Gtk.Widget
            @param widget as int
            @param height as int
        """
        if self.__resize_timeout_id is not None:
            GLib.source_remove(self.__resize_timeout_id)
        self.__resize_timeout_id = GLib.idle_add(
            self.__handle_size_allocate, width, height)
