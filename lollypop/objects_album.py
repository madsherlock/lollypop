# Copyright (c) 2014-2020 Cedric Bellegarde <cedric.bellegarde@adishatz.org>
# Copyright (c) 2015 Jean-Philippe Braun <eon@patapon.info>
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

from hashlib import md5

from lollypop.define import App, StorageType, ScanUpdate
from lollypop.objects_track import Track
from lollypop.objects_disc import Disc
from lollypop.objects import Base
from lollypop.utils import emit_signal
from lollypop.collection_item import CollectionItem
from lollypop.logger import Logger


class Album(Base):
    """
        Represent an album
    """
    DEFAULTS = {"name": "",
                "artists": [],
                "artist_ids": [],
                "year": None,
                "timestamp": 0,
                "uri": "",
                "popularity": 0,
                "rate": 0,
                "mtime": 1,
                "synced": 0,
                "loved": False,
                "storage_type": 0,
                "mb_album_id": None,
                "lp_album_id": None}

    def __init__(self, album_id=None, genre_ids=[], artist_ids=[],
                 skipped=True):
        """
            Init album
            @param album_id as int
            @param genre_ids as [int]
            @param artist_ids as [int]
            @param skipped as bool
        """
        Base.__init__(self, App().albums)
        self.id = album_id
        self.genre_ids = genre_ids
        self.__tracks = None
        self.__skipped = skipped
        self.__tracks_storage_type = self.storage_type
        # Use artist ids from db else
        if artist_ids:
            artists = []
            for artist_id in set(artist_ids) | set(self.artist_ids):
                artists.append(App().artists.get_name(artist_id))
            self.artists = artists
            self.artist_ids = artist_ids

    def __del__(self):
        """
            Remove ref cycles
        """
        self.__tracks = None

    # Used by pickle
    def __getstate__(self):
        self.db = None
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.db = App().albums

    def set_track_ids(self, track_ids):
        """
            Set album track ids
            @param track_ids as [int]
        """
        self.__tracks = []
        self.append_track_ids(track_ids)

    def append_track_id(self, track_id):
        """
            Append track_id to album
            @param track_id as int
        """
        if self.__tracks is None:
            self.__tracks = []
        self.__tracks.append(Track(track_id, self))

    def append_track_ids(self, track_ids):
        """
            Append track ids to album
            @param track_ids as [int]
        """
        if self.__tracks is None:
            self.__tracks = []
        for track_id in track_ids:
            self.__tracks.append(Track(track_id, self))

    def remove_track_id(self, track_id):
        """
            Remove track_id from album
            @param track_id as int
        """
        for track in self.__tracks:
            if track.id == track_id:
                self.__tracks.remove(_track)

    def set_loved(self, loved):
        """
            Mark album as loved
            @param loved as bool
        """
        if self.id >= 0:
            self.db.set_loved(self.id, loved)
            self.loved = loved

    def set_uri(self, uri):
        """
            Set album uri
            @param uri as str
        """
        if self.id >= 0:
            self.db.set_uri(self.id, uri)
        self.uri = uri

    def get_track(self, track_id):
        """
            Get track
            @param track_id as int
            @return Track
        """
        for track in self.tracks:
            if track.id == track_id:
                return track
        return Track()

    def save(self, save):
        """
            Save album to collection.
            @param save as bool
        """
        # Save tracks
        for track_id in self.track_ids:
            if save:
                App().tracks.set_storage_type(track_id, StorageType.SAVED)
            else:
                App().tracks.set_storage_type(track_id, StorageType.EPHEMERAL)
        # Save album
        self.__save(save)

    def save_track(self, save, track):
        """
            Save track to collection
            @param save as bool
            @param track as Track
        """
        if save:
            App().tracks.set_storage_type(track.id, StorageType.SAVED)
        else:
            App().tracks.set_storage_type(track.id, StorageType.EPHEMERAL)
        # Save album
        self.__save(save)

    def load_tracks(self, cancellable):
        """
            Load album tracks from Spotify,
            do not call this for Storage.COLLECTION
            @param cancellable as Gio.Cancellable
            @return status as bool
        """
        try:
            if self.storage_type & (StorageType.COLLECTION |
                                    StorageType.EXTERNAL):
                return False
            elif self.synced != 0 and self.synced != len(self.tracks):
                from lollypop.search import Search
                Search().load_tracks(self, cancellable)
        except Exception as e:
            Logger.warning("Album::load_tracks(): %s" % e)
        return True

    def set_synced(self, mask):
        """
            Set synced mask
            @param mask as int
        """
        self.db.set_synced(self.id, mask)
        self.synced = mask

    def clone(self, skipped):
        """
            Clone album
            @param skipped as bool
            @return album
        """
        return Album(self.id, self.genre_ids, self.artist_ids, skipped)

    def set_storage_type(self, storage_type):
        """
            Set storage type
            @param storage_type as StorageType
        """
        self.__tracks_storage_type = storage_type

    def set_skipped(self):
        """
            Set album as skipped, not allowing skipped tracks
        """
        self.__skipped = True

    @property
    def collection_item(self):
        """
            Get collection item related to album
            @return CollectionItem
        """
        item = CollectionItem(album_id=self.id,
                              album_name=self.name,
                              artist_ids=self.artist_ids,
                              lp_album_id=self.lp_album_id)
        return item

    @property
    def is_web(self):
        """
            True if track is a web track
            @return bool
        """
        return not self.storage_type & (StorageType.COLLECTION |
                                        StorageType.EXTERNAL)

    @property
    def tracks_count(self):
        """
            Get tracks count
            @return int
        """
        if self._tracks:
            return len(self._tracks)
        else:
            return self.db.get_tracks_count(
                self.id,
                self.genre_ids,
                self.artist_ids)

    @property
    def track_ids(self):
        """
            Get album track ids
            @return [int]
        """
        return [track.id for track in self.tracks]

    @property
    def track_uris(self):
        """
            Get album track uris
            @return [str]
        """
        return [track.uri for track in self.tracks]

    @property
    def tracks(self):
        """
            Get album tracks
            @return [Track]
        """
        if self.id is None:
            return []
        if self.__tracks is not None:
            return self._tracks
        for disc in self.discs:
            tracks += disc.tracks
        # Already cached by another thread
        if not self._tracks:
            self._tracks = tracks
        return tracks

    @property
    def duration(self):
        """
            Get album duration and handle caching
            @return int
        """
        if self._tracks:
            track_ids = [track.lp_track_id for track in self.tracks]
            track_str = "%s" % sorted(track_ids)
            track_hash = md5(track_str.encode("utf-8")).hexdigest()
            album_hash = "%s-%s" % (self.lp_album_id, track_hash)
        else:
            album_hash = "%s-%s-%s" % (self.lp_album_id,
                                       self.genre_ids,
                                       self.artist_ids)
        duration = App().cache.get_duration(album_hash)
        if duration is None:
            if self._tracks:
                duration = 0
                for track in self._tracks:
                    duration += track.duration
            else:
                duration = self.db.get_duration(self.id,
                                                self.genre_ids,
                                                self.artist_ids)
            App().cache.set_duration(self.id, album_hash, duration)
        return duration

#######################
# PRIVATE             #
#######################
    def __save(self, save):
        """
            Save album to collection.
            @param save as bool
        """
        # Save album by updating storage type
        if save:
            self.db.set_storage_type(self.id, StorageType.SAVED)
        else:
            self.db.set_storage_type(self.id, StorageType.EPHEMERAL)
        self.reset("mtime")
        if save:
            item = CollectionItem(artist_ids=self.artist_ids,
                                  album_id=self.id)
            emit_signal(App().scanner, "updated", item,
                        ScanUpdate.ADDED)
        else:
            removed_artist_ids = []
            for artist_id in self.artist_ids:
                if not App().artists.get_name(artist_id):
                    removed_artist_ids.append(artist_id)
            item = CollectionItem(artist_ids=removed_artist_ids,
                                  album_id=self.id)
            emit_signal(App().scanner, "updated", item,
                        ScanUpdate.REMOVED)
