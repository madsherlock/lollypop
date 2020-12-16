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

import itertools
from time import time
from random import shuffle

from lollypop.sqlcursor import SqlCursor
from lollypop.objects_track import Track
from lollypop.define import App, Type, OrderBy, StorageType
from lollypop.logger import Logger
from lollypop.utils import remove_static, make_subrequest


class DiscsDatabase:
    """
        Discs database helper
    """

    def __init__(self, db):
        """
            Init albums database object
            @param db as Database
        """
        self.__db = db
        
    def add(self, name, album_id, number, year, timestamp):
        """
            @param name as str
            @param album_id as int
            @param number as int
            @param year as int
            @param timestamp as int
        """
        with SqlCursor(self.__db, True) as sql:
            result = sql.execute("INSERT INTO discs\
                                  (name, album_id, number,\
                                   year, timestamp)\
                                  VALUES (?, ?, ?, ?, ?)",
                                 (name, album_id, number, year, timestamp))
            return result.lastrowid

    def get_number(self, disc_id):
        """
            Get disc number
            @param disc_id as int
            @return int
        """
        with SqlCursor(self.__db) as sql:
            result = sql.execute("SELECT number FROM discs\
                                  WHERE rowid=?",
                                  (disc_id,))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def get_album_id(self, disc_id):
        """
            Get album id
            @param disc_id as int
            @return int
        """
        with SqlCursor(self.__db) as sql:
            result = sql.execute("SELECT album_id FROM discs\
                                  WHERE rowid=?",
                                  (disc_id,))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def get_year(self, disc_id):
        """
            Get year
            @param disc_id as int
            @return int
        """
        with SqlCursor(self.__db) as sql:
            result = sql.execute("SELECT year FROM discs\
                                  WHERE rowid=?",
                                  (disc_id,))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def get_timestamp(self, disc_id):
        """
            Get timestamp
            @param disc_id as int
            @return int
        """
        with SqlCursor(self.__db) as sql:
            result = sql.execute("SELECT timestamp FROM discs\
                                  WHERE rowid=?",
                                  (disc_id,))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def get_id(self, disc_id, number):
        """
            Get disc id
            @param disc_id as int
            @param number as int
            @return int
        """
        with SqlCursor(self.__db) as sql:
            result = sql.execute("SELECT rowid FROM discs\
                                  WHERE rowid=? AND number=?",
                                  (disc_id, number))
            v = result.fetchone()
            if v is not None:
                return v[0]
            return None

    def set_year(self, disc_id, year):
        """
            Set year
            @param disc_id as int
            @param year as int
            @warning: commit needed
        """
        with SqlCursor(self.__db, False) as sql:
            sql.execute("UPDATE discs SET year=? WHERE rowid=?",
                        (year, disc_id))

    def set_timestamp(self, disc_id, timestamp):
        """
            Set timestamp
            @param disc_id as int
            @param timestamp as int
            @warning: commit needed
        """
        with SqlCursor(self.__db, False) as sql:
            sql.execute("UPDATE discs SET timestamp=? WHERE rowid=?",
                        (timestamp, disc_id))

    def get_tracks(self, disc_id):
        """
            Get tracks
            @param disc_id as int
            @return []
        """
        with SqlCursor(self.__db, False) as sql:
            result = sql.execute("SELECT track_id FROM tracks\
                                  WHERE rowid=?", (disc_id,))
            tracks = []
            for track_id in list(itertools.chain(*result)):
                tracks.append(Track(track_id))
            return tracks

#######################
# PRIVATE             #
#######################
