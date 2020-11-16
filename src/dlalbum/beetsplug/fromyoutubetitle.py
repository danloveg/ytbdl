""" fromyoutubetitle Beets Plugin """

from pathlib import Path
import re

from beets.plugins import BeetsPlugin
from beets.util import displayable_path

import tagsfrompath as frompath


class FromYoutubeTitlePlugin(BeetsPlugin):
    """ Sets the title of each item to the filename, removing most of the common
    junk associated with YouTube titles like "(Official Audio)" and the name of
    the album or artist.
    Assumes the music is in an Artist/Album/Song folder structure, and that the
    song file names are the names of the YouTube videos they were extracted
    from.
    """
    def __init__(self):
        super(FromYoutubeTitlePlugin, self).__init__()
        self.register_listener('import_task_start', set_titles_no_junk)


YOUTUBE_TITLE_JUNK = [
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?(?:Explicit|Clean|Parental\sAdvisory).*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?(?:HQ|HD|CDQ).*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Audio.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Album.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Song.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Video.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Lyric.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Visualizer.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?iTunes.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Official.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Original.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Version.*?[\)\]\}])'),
    re.compile(r'(?i)(?P<junk>[\(\[\{].*?Prod(?:uced)?\sBy.*?[\)\]\}])'),
]


EXTRA_STRIP_PATTERNS = [
    re.compile(r'^\s*[-_\|]\s*(?P<title>.+)$'),
    re.compile(r'^(?P<title>.+)\s*[-_\|]\s*$')
]


def set_titles_no_junk(task, session):
    items = task.items if task.is_album else [task.item]

    for item in items:
        if item.title:
            continue
        item_file_path = Path(displayable_path(item.path))
        youtube_title = frompath.get_title(item_file_path)
        album_name = frompath.get_album_name(item_file_path)
        artist_name = frompath.get_artist_name(item_file_path)
        artist_album_junk = [
            '(?i)(?P<junk>\\({0}\\))'.format(re.escape(album_name)),
            '(?i)(?P<junk>\\(?{0}\\)?)'.format(re.escape(artist_name))
        ]
        item.title = remove_junk(youtube_title, artist_album_junk, YOUTUBE_TITLE_JUNK)


def remove_junk(title: str, *junk_patterns):
    new_title = title

    for pattern_list in junk_patterns:
        for pattern in pattern_list:
            match_obj = None
            if isinstance(pattern, re.Pattern):
                match_obj = pattern.search(new_title)
            elif isinstance(pattern, str):
                match_obj = re.search(pattern, title)
            if match_obj is not None:
                new_title = new_title.replace(match_obj.group('junk'), '')

    return extra_strip(new_title)


def extra_strip(string: str):
    stripped_string = string
    for pattern in EXTRA_STRIP_PATTERNS:
        match_obj = pattern.match(stripped_string)
        if match_obj is None:
            continue
        stripped_string = match_obj.group('title')
    return stripped_string.strip()
