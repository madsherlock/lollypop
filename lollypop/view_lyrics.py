# Copyright (c) 2014-2020 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
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

from gi.repository import Gtk, GLib, Pango

from gettext import gettext as _

from lollypop.view import View
from lollypop.define import App, ViewType, AdaptiveSize
from lollypop.define import StorageType
from lollypop.logger import Logger
from lollypop.objects_track import Track
from lollypop.helper_lyrics import LyricsHelper
from lollypop.helper_signals import SignalsHelper, signals_map
from lollypop.widgets_banner_lyrics import LyricsBannerWidget


class LyricsLabel(Gtk.Stack):
    """
        Lyrics label with effect on change
    """

    def __init__(self):
        """
            Init label
        """
        Gtk.Stack.__init__(self)
        self.__label1 = Gtk.Label.new()
        self.__label1.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.__label1.set_line_wrap(True)
        self.__label1.set_justify(Gtk.Justification.CENTER)
        self.__label2 = Gtk.Label.new()
        self.__label2.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.__label2.set_line_wrap(True)
        self.__label2.set_justify(Gtk.Justification.CENTER)
        self.__label1.show()
        self.__label2.show()
        self.add(self.__label1)
        self.add(self.__label2)
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.set_transition_duration(200)

    def set_text(self, text):
        """
            Set label text
            @param text as str
        """
        self.next()
        self.get_visible_child().set_text(text)

    def set_markup(self, markup):
        """
            Set label markup
            @param markup as str
        """
        self.next()
        self.get_visible_child().set_markup(markup)

    def next(self):
        """
            Show next label
        """
        for child in self.get_children():
            if child != self.get_visible_child():
                self.set_visible_child(child)
                break


class LyricsView(View, SignalsHelper):
    """
        Show lyrics for track
    """

    __FILTERS = ["[explicit]", "(explicit)"]

    # TODO add https://www.musixmatch.com support
    @signals_map
    def __init__(self):
        """
            Init view
        """
        View.__init__(self, StorageType.COLLECTION,
                      ViewType.SCROLLED | ViewType.OVERLAY)
        self.__lyrics_timeout_id = None
        self.__downloads_running = 0
        self.__lyrics_text = ""
        self._empty_message = _("No track playing")
        self._empty_icon_name = "view-dual-symbolic"
        self.__lyrics_label = LyricsLabel()
        self.__lyrics_label.show()
        self.__lyrics_label.set_property("halign", Gtk.Align.CENTER)
        self.__banner = LyricsBannerWidget(self.view_type)
        self.__banner.show()
        self.__banner.connect("translate", self.__on_translate)
        self.add_widget(self.__lyrics_label, self.__banner)
        self.__lyrics_helper = LyricsHelper()
        self.__update_lyrics_style()
        return [
                (App().window, "adaptive-size-changed",
                 "_on_adaptive_size_changed"),
                (App().player, "current-changed", "_on_current_changed")
        ]

    def populate(self, track):
        """
            Set lyrics
            @param track as Track
        """
        self.__banner.translate_button.set_sensitive(False)
        self.__lyrics_label.set_text("")
        if track.id is None:
            return
        self.__lyrics_label.set_text(_("Loading…"))
        lyrics = ""
        if isinstance(track, Track):
            self.__lyrics_helper.load(track)
            # First check synced lyrics
            if self.__lyrics_helper.available:
                if self.__lyrics_timeout_id is None:
                    self.__lyrics_timeout_id = GLib.timeout_add(
                        500, self.__show_sync_lyrics)
                return
            else:
                if self.__lyrics_timeout_id is not None:
                    GLib.source_remove(self.__lyrics_timeout_id)
                    self.__lyrics_timeout_id = None
                if track.storage_type & StorageType.COLLECTION:
                    from lollypop.tagreader import TagReader, Discoverer
                    tagreader = TagReader()
                    discoverer = Discoverer()
                    try:
                        info = discoverer.get_info(track.uri)
                    except:
                        info = None
                    if info is not None:
                        tags = info.get_tags()
                        lyrics = tagreader.get_lyrics(tags)
        if lyrics:
            self.__lyrics_label.set_text(lyrics)
            self.__lyrics_text = lyrics
        else:
            self.__lyrics_helper.get_lyrics_from_web(track,
                                                     self.__on_lyrics,
                                                     False,
                                                     track)

    @property
    def args(self):
        return None

##############
# PROTECTED  #
##############
    def __on_translate(self, banner, active):
        """
            Translate lyrics
            @param banner as LyricsBannerWidget
            @param active as bool
        """
        if active:
            App().task_helper.run(self.__get_blob, self.__lyrics_text,
                                  callback=(self.__lyrics_label.set_text,))
        else:
            self.__lyrics_label.set_text(self.__lyrics_text)

    def _on_unmap(self, widget):
        """
            Connect player signal
            @param widget as Gtk.Widget
        """
        self.__lyrics_helper.cancel()
        View._on_unmap(self, widget)
        if self.__lyrics_timeout_id is not None:
            GLib.source_remove(self.__lyrics_timeout_id)
            self.__lyrics_timeout_id = None

    def _on_current_changed(self, player):
        """
            Update lyrics
            @param player as Player
        """
        self.populate(App().player.current_track)

    def _on_adaptive_size_changed(self, window, adaptive_size):
        """
            Update internal sizing
            @param window as Window
            @param adaptive_size as AdaptiveSize
        """
        self.__update_lyrics_style()

############
# PRIVATE  #
############
    def __show_sync_lyrics(self):
        """
            Show sync lyrics for track
        """
        timestamp = App().player.position
        (previous, current, next) =\
            self.__lyrics_helper.get_lyrics_for_timestamp(timestamp)
        lyrics = ""
        for line in previous:
            if line:
                escaped = GLib.markup_escape_text(line)
                lyrics += "<span alpha='20000'>%s</span>" % escaped + "\n"
        for line in current:
            escaped = GLib.markup_escape_text(line)
            lyrics += "<span>%s</span>" % escaped + "\n"
        for line in next:
            if line:
                escaped = GLib.markup_escape_text(line)
                lyrics += "<span alpha='20000'>%s</span>" % escaped + "\n"
        self.__lyrics_label.set_markup(lyrics)
        return True

    def __get_blob(self, text):
        """
            Translate text with current user locale
            @param text as str
        """
        try:
            locales = GLib.get_language_names()
            user_code = locales[0].split(".")[0]
            try:
                from textblob.blob import TextBlob
            except:
                return _("You need to install python3-textblob module")
            blob = TextBlob(text)
            return str(blob.translate(to=user_code))
        except Exception as e:
            Logger.error("LyricsView::__get_blob(): %s", e)
            return _("Can't translate this lyrics")

    def __update_lyrics_style(self):
        """
            Update lyrics style based on current view width
        """
        context = self.get_style_context()
        for cls in context.list_classes():
            context.remove_class(cls)
        context.add_class("lyrics")
        adaptive_size = App().window.adaptive_size
        if adaptive_size & (AdaptiveSize.BIG | AdaptiveSize.LARGE):
            if self.__lyrics_helper.available:
                context.add_class("text-xx-large")
            else:
                context.add_class("text-x-large")
        elif adaptive_size & AdaptiveSize.NORMAL:
            if self.__lyrics_helper.available:
                context.add_class("text-x-large")
            else:
                context.add_class("text-large")
        elif adaptive_size & AdaptiveSize.MEDIUM:
            if self.__lyrics_helper.available:
                context.add_class("text-large")
            else:
                context.add_class("text-medium")
        elif self.__lyrics_helper.available:
            context.add_class("text-medium")

    def __on_lyrics(self, lyrics, filtered, track):
        """
            Set lyrics
            @param lyrics as str/None
            @param filtered as bool
            @param track as Track
        """
        if lyrics is None:
            self.__lyrics_label.set_text(
                    _("Network not available"))
        elif lyrics == "":
            if filtered:
                self.__lyrics_label.set_text(_("No lyrics found ") + "😓")
            else:
                name = track.name.lower()
                for _filter in self.__FILTERS:
                    name = name.replace(_filter, "")
                track.set_name(name)
                self.__lyrics_helper.get_lyrics_from_web(track,
                                                         self.__on_lyrics,
                                                         True,
                                                         track)
        else:
            self.__lyrics_label.set_text(lyrics)
            self.__lyrics_text = lyrics
            self.__banner.translate_button.set_sensitive(True)
