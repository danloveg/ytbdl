"""If the album and artist are empty, try to extract the album and artist from
the directories the file is in. Looks above the file for the album, and above
the album for the artist name.
"""

from pathlib import Path

from beets.plugins import BeetsPlugin
from beets.util import displayable_path

import tagsfrompath as frompath


class FromDirectoryNamePlugin(BeetsPlugin):
    def __init__(self):
        super(FromDirectoryNamePlugin, self).__init__()
        self.register_listener('import_task_start', update_album_artist_with_dirnames)


def update_album_artist_with_dirnames(task, session):
    items = task.items if task.is_album else [task.item]

    for item in items:
        if item.album and item.artist:
            continue

        file_path = Path(displayable_path(item.path))

        if not item.album:
            item.album = frompath.get_album_name(file_path)
        if not item.artist:
            item.artist = frompath.get_artist_name(file_path)
