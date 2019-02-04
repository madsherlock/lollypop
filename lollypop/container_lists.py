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

from lollypop.loader import Loader
from lollypop.logger import Logger
from lollypop.selectionlist import SelectionList
from lollypop.define import App, Type, SelectionListMask


class ListsContainer:
    """
        Selections lists management for main view
    """

    def __init__(self):
        """
            Init container
        """
        self._list_one = SelectionList(SelectionListMask.ARTISTS |
                                       SelectionListMask.COMPILATIONS)
        self._list_one.connect("item-selected", self.__on_list_one_selected)
        self._list_one.connect("populated", self.__on_list_one_populated)
        self._list_one.connect("pass-focus", self.__on_pass_focus)

    def update_list_one(self, update=False):
        """
            Update list one
            @param update as bool
        """
        if self._list_one.get_visible():
            self.__update_list_artists(update)

    def show_artists_albums(self, artist_ids):
        """
            Show albums from artists
            @param artist id as int
        """
        self._list_one.select_ids(artist_ids)

    @property
    def list_one(self):
        """
            Get first SelectionList
            @return SelectionList
        """
        return self._list_one

##############
# PROTECTED  #
##############
    def _reload_list_view(self):
        """
            Reload list view
        """
        state_one_ids = App().settings.get_value("state-one-ids")
        if state_one_ids:
            self._list_one.select_ids(state_one_ids)
        else:
            self._list_one.select_first()

############
# PRIVATE  #
############
    def __update_list_artists(self, update):
        """
            Setup list for artists
            @param update as bool, if True, just update entries
        """
        def load():
            artists = App().artists.get([Type.ALL])
            compilations = App().albums.get_compilation_ids([Type.ALL])
            return (artists, compilations)

        def setup(artists, compilations):
            items = self._list_one.get_headers(self._list_one.mask)
            items += artists
            if update:
                self._list_one.update_values(items)
            else:
                self._list_one.populate(items)
        loader = Loader(target=load, view=self._list_one,
                        on_finished=lambda r: setup(*r))
        loader.start()

    def __on_list_one_selected(self, selection_list):
        """
            Update view based on selected object
            @param list as SelectionList
        """
        Logger.debug("Container::__on_list_one_selected()")
        self._stack.destroy_non_visible_children()
        if App().window.is_adaptive:
            App().window.emit("can-go-back-changed", True)
        else:
            App().window.emit("show-can-go-back", False)
            App().window.emit("can-go-back-changed", False)
        view = None
        selected_ids = self._list_one.selected_ids
        if not selected_ids:
            return
        # Update view
        if selected_ids[0] == Type.PLAYLISTS:
            view = self._get_view_playlists()
        elif selected_ids[0] == Type.CURRENT:
            view = self._get_view_current()
        elif selected_ids[0] == Type.SEARCH:
            view = self._get_view_search()
        elif Type.DEVICES - 999 < selected_ids[0] < Type.DEVICES:
            view = self._get_view_device(selected_ids[0])
        elif selected_ids[0] in [Type.POPULARS,
                                 Type.LOVED,
                                 Type.RECENTS,
                                 Type.NEVER,
                                 Type.RANDOMS]:
            view = self._get_view_albums(selected_ids, [])
        elif selected_ids[0] == Type.RADIOS:
            view = self._get_view_radios()
        elif selected_ids[0] == Type.YEARS:
            view = self._get_view_albums_decades()
        elif selected_ids[0] == Type.ARTISTS:
            view = self._get_view_artists_rounded(False)
            App().window.emit("show-can-go-back", True)
        elif selection_list.mask & SelectionListMask.ARTISTS:
            if selected_ids[0] == Type.ALL:
                view = self._get_view_albums(selected_ids, [])
            elif selected_ids[0] == Type.COMPILATIONS:
                view = self._get_view_albums([], selected_ids)
            else:
                view = self._get_view_artists([], selected_ids)
        elif not App().window.is_adaptive:
            view = self._get_view_albums(selected_ids, [])
        if view is not None:
            if view not in self._stack.get_children():
                self._stack.add(view)
            self._stack.set_visible_child(view)

    def __on_list_one_populated(self, selection_list):
        """
            Add device to list one
            @param selection_list as SelectionList
        """
        for dev in self.devices.values():
            self._list_one.add_value((dev.id, dev.name, dev.name))

    def __on_pass_focus(self, selection_list):
        """
            Pass focus to other list
            @param selection_list as SelectionList
        """
        self._list_one.grab_focus()
