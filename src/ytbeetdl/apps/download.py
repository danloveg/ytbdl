import re
import sys
from subprocess import CalledProcessError, run
from pathlib import Path


from ytbeetdl import config_exists
from ytbeetdl.configtools import get_extra_youtube_dl_args, get_beets_config
from ytbeetdl.beets import overwrite_beets_config, restore_backup_beets_config, beet_import
from ytbeetdl.exceptions import ConfigurationError
from ytbeetdl.apps.base import BaseApp


class DownloadApp(BaseApp):
    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        dl_parser = sub_parser.add_parser(name='get')
        dl_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Log verbose information')
        dl_parser.add_argument('--artist', action='store', required=True,
                               help='The artist who created the album to download')
        dl_parser.add_argument('--album', action='store', required=True,
                               help='The name of the album to download')
        dl_parser.add_argument('urls', nargs='+',
                               help='One or more URLs to download audio from')

    INVALID_FILENAME_CHARS = re.compile(r'[^\w\-_\. ]')

    def __init__(self):
        self.backup_beets_config = None
        self.verbose = False
        self.logger = None

    def configure_logging(self):
        level = 'DEBUG' if self.verbose else 'INFO'
        self.logger = self.get_logger('ytbeetdl', level)

    def start_execution(self, arg_parser, **kwargs):
        self.verbose = kwargs.get('verbose')
        self.configure_logging()
        if not config_exists():
            self.logger.info('Create a config before continuing with:')
            self.logger.info('ytbeetdl config create')
            return

        artist_name = kwargs.get('artist')
        album_name = kwargs.get('album')
        urls = kwargs.get('urls')

        try:
            self.logger.info(msg='Downloading "{0}" by {1}'.format(album_name, artist_name))
            album_dir = self.create_album_dir(artist_name, album_name)
            self.download_music(album_dir, urls)
            self.logger.info('Autotagging album')
            self.autotag_album(album_dir)
        except (CalledProcessError, ConfigurationError) as exc:
            self.logger.error(msg=str(exc))
            self.logger.warning('Aborting')
            sys.exit(1)
        finally:
            self.cleanup()

    def create_album_dir(self, artist: str, album: str) -> Path:
        ''' Create the artist and album folders for the music to be moved into. If the album folder
        already exists and is not empty, an exception is raised as this may indicate that the album
        has already been downloaded.

        The directory structure is created under the current directory in this manner:

        .. code-block::

            . (current directory)
                |_ Artist
                    |_ Album

        Args:
            artist (str): The name of the artist whose music is being downloaded
            album (str): The name of album by the artist

        Returns:
            (Path): A path to the album folder
        '''
        root = Path('.')
        artist_folder = root / self.clean_path_name(artist)
        if not artist_folder.exists():
            self.logger.debug(msg='Creating artist folder "{0}"'.format(artist_folder))
            artist_folder.mkdir()
        album_folder = artist_folder / self.clean_path_name(album)
        if album_folder.exists() and list(album_folder.glob('*')):
            raise FileExistsError('The album folder already exists and is not empty')
        if not album_folder.exists():
            self.logger.debug(msg='Creating album folder "{0}"'.format(album_folder))
            album_folder.mkdir()
        return album_folder

    def download_music(self, album_dir: Path, urls: list):
        ''' Downloads one or more songs using youtube-dl in a subprocess into the album_dir. Adds
        any extra args to the youtube-dl call (before the URLs) that may be in
        :code:`config['youtube-dl']['options']`.

        Embedding youtube-dl is not well documented. Calling youtube-dl, a Python program, from
        within Python makes the most sense, but there is no easy way to map from the command line
        options users know to a python dict youtube-dl uses. Embedding youtube-dl only seems to make
        sense if the argument list is static.

        Args:
            album_dir (Path): The directory to download files into
            urls (list): A list of URLs to download music from.
        '''
        default_args = ['--extract-audio', '--output', "%(title)s.%(ext)s"]
        extra_args = get_extra_youtube_dl_args()
        if extra_args:
            self.logger.info(msg='Using extra arguments for youtube-dl: {0}'.format(
                ' '.join(extra_args)))
        else:
            self.logger.debug('No extra arguments for youtube-dl found')
        command = ['youtube-dl', *default_args, *extra_args, *urls]
        self.logger.debug(msg='Opening subprocess: {0}'.format(' '.join(command)))
        result = run(
            args=command,
            check=True,
            shell=False,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd=str(album_dir))
        result.check_returncode()
        self.logger.debug('youtube-dl exited with return code 0')

    def autotag_album(self, album_dir: Path):
        ''' Autotag the downloaded music with beets. The configuration for beets is overwritten with
        the beets config from ytbeetdl's configuration file.

        Embedding beets is even less documented than youtube-dl, so it is called in a subprocess the
        same as youtube-dl is. The same way that

        Args:
            album_dir (Path): The directory the album was downloaded to
        '''
        self.logger.info('Backing up your beets config')
        self.logger.info('Writing custom beets config')
        import_dir = str(album_dir.parent.parent.resolve()).replace('\\', '/')
        raw_config = get_beets_config(import_dir)
        self.backup_beets_config = overwrite_beets_config(raw_config)
        self.logger.debug(msg='Backup copy stored at "{0}"'.format(self.backup_beets_config))
        self.logger.info('Starting beets import session')
        beet_import(album_dir)

    def clean_path_name(self, name):
        return self.INVALID_FILENAME_CHARS.sub('_', name)

    def cleanup(self):
        if self.backup_beets_config is not None:
            self.logger.info(msg='Restoring backup beets config copy')
            restore_backup_beets_config(self.backup_beets_config)
            self.logger.debug(msg='Backup copy restored from "{0}"'.format(
                self.backup_beets_config))
