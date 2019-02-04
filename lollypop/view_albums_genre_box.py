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

from gi.repository import GLib

from lollypop.view_flowbox import FlowBoxView
from lollypop.widgets_albums_genre import AlbumsGenreWidget
from lollypop.define import App, Type


class AlbumsGenreBoxView(FlowBoxView):
    """
        Show decades in a FlowBox
    """

    def __init__(self, art_size):
        """
            Init decade view
            @param art_size as int
        """
        self._art_size = art_size
        FlowBoxView.__init__(self)
        self._widget_class = AlbumsGenreWidget

#######################
# PROTECTED           #
#######################
    def _add_items(self, item_ids, *args):
        """
            Add albums to the view
            Start lazy loading
            @param item ids as [int]
        """
        widget = FlowBoxView._add_items(self, item_ids, self._art_size)
        if widget is not None:
            widget.connect("overlayed", self.on_overlayed)

    def _on_map(self, widget):
        """
            Set active ids
        """
        if not App().settings.get_value("show-genres"):
            App().window.emit("show-can-go-back", True)
            App().window.emit("can-go-back-changed", True)
        App().settings.set_value("state-one-ids",
                                 GLib.Variant("ai", [Type.GENRES]))
        App().settings.set_value("state-two-ids",
                                 GLib.Variant("ai", []))
