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
from lollypop.objects import Base
from lollypop.utils import emit_signal
from lollypop.collection_item import CollectionItem
from lollypop.logger import Logger


class Disc(Base):
    """
        Represent an album disc
    """
    DEFAULTS = {"name": "",
                "number": [],
                "album_id": [],
                "year": None,
                "timestamp": 0,
                "tracks": []}

    def __init__(self, disc_id=None):
        """
            Init Disc
            @param disc_id as int
        """
        self.db = App().discs
        self.id = disc_id

    def __del__(self):
        """
            Remove ref cycles
        """
        self.__album = None

    # Used by pickle
    def __getstate__(self):
        self.db = None
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.db = App().discs
