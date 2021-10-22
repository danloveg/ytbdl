import re
import shlex
import sys
from subprocess import CalledProcessError, run
from pathlib import Path

from ytbeetdl import config_exists
from ytbeetdl.beets import beet_import, create_temp_config
from ytbeetdl.exceptions import ConfigurationError
from ytbeetdl.apps.base import BaseApp


class DownloadApp(BaseApp):
    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        dl_parser = sub_parser.add_parser(name='get',
            description=('Get an album from YouTube with youtube-dl before auto-tagging it with '
                         'beets'))
        dl_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Log verbose information')
        dl_parser.add_argument('--ytdl-options', type=str,
                               help=('command line options to pass to youtube-dl. For example, '
                                     '"-f bestaudio[ext=m4a]"'))
        dl_parser.add_argument('--artist', action='store', required=True,
                               help='The artist who created the album to download')
        dl_parser.add_argument('--album', action='store', required=True,
                               help='The name of the album to download')
        dl_parser.add_argument('urls', nargs='+',
                               help='One or more URLs to download audio from')

    INVALID_FILENAME_CHARS = re.compile(r'[^\w\-_\. ]')
    DEFAULT_YTDL_ARGS = ['--extract-audio', '--output', "%(title)s.%(ext)s"]

    def __init__(self):
        self.verbose = False
        self.logger = None
        self.temp_config = None

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
            extra_args = self.parse_ytdl_options(kwargs.get('ytdl_options'))
        except ValueError as exc:
            arg_parser.error(str(exc))

        try:
            self.logger.info(msg='Downloading "{0}" by {1}'.format(album_name, artist_name))
            album_dir = self.create_album_dir(artist_name, album_name)
            self.download_music(album_dir, extra_args, urls)
            self.logger.info(msg='Autotagging album downloaded to {0}'.format(str(album_dir)))
            self.autotag_album(album_dir)
        except KeyboardInterrupt:
            self.logger.info('User interrupted program.')
            self.logger.info('Aborting.')
            sys.exit(0)
        except FileExistsError as exc:
            self.logger.error(msg='FileExistsError: {0}'.format(str(exc)))
            self.logger.warning('Aborting')
            sys.exit(1)
        except (CalledProcessError, ConfigurationError) as exc:
            self.logger.error(msg='{0} encountered:'.format(exc.__class__.__name__))
            self.logger.error(msg=str(exc))
            self.logger.warning('Aborting')
            sys.exit(1)
        finally:
            self.logger.debug('Cleaning up')
            self.cleanup()

    def parse_ytdl_options(self, raw_options: str) -> list:
        ''' Parse the list of youtube-dl options the user specified into a list of command line
        options. Raises a ValueError if the user supplied an --output or -o option.

        Args:
            raw_options (str): A string of command line args

        Returns:
            (list): A list of command line options parsed from the raw_options
        '''
        if not raw_options:
            return []

        extra_args = shlex.split(raw_options)

        if '--extract-audio' in extra_args:
            self.logger.warning(('The --extract-audio option is already specified for you, you do '
                                 'not need to add it'))
            while '--extract-audio' in extra_args:
                extra_args.remove('--extract-audio')
        if '-x' in extra_args:
            self.logger.warning(('The -x option is already specified for you as --extract-audio, '
                                 'you do not need to add it'))
            while '-x' in extra_args:
                extra_args.remove('-x')

        for not_allowed in ('--output', '-o'):
            if not_allowed in extra_args:
                raise ValueError((f'You cannot pass "{not_allowed}" in --ytdl-options, the output '
                                  'option is already in use'))
        return extra_args

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

    def download_music(self, album_dir: Path, extra_args: list, urls: list):
        ''' Downloads one or more songs using youtube-dl in a subprocess into the album_dir.

        Embedding youtube-dl is not well documented. Calling youtube-dl, a Python program, from
        within Python makes the most sense, but there is no easy way to map from the command line
        options to a dict. Embedding youtube-dl only seems to make sense if the argument list is
        static, which it is not, here.

        Args:
            album_dir (Path): The directory to download files into
            urls (list): A list of URLs to download music from.
        '''
        if extra_args:
            self.logger.info(msg='Using extra arguments for youtube-dl: {0}'.format(
                ' '.join(extra_args)))
        else:
            self.logger.debug('No extra arguments for youtube-dl found')
        command = ['youtube-dl', *self.DEFAULT_YTDL_ARGS, *extra_args, '--', *urls]
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
        ''' Autotag the downloaded music with beets. The configuration for beets is combined with a
        temporary in-memory file, which is copied from ytbeetdl's configuration.

        Args:
            album_dir (Path): The directory the album was downloaded to
        '''
        import_dir = str(album_dir.parent.parent.resolve()).replace('\\', '/')
        self.temp_config = create_temp_config(import_dir)
        self.logger.debug('Created a temporary in-memory beets config')
        beet_import(album_dir, self.temp_config)

    def clean_path_name(self, name):
        return self.INVALID_FILENAME_CHARS.sub('_', name)

    def cleanup(self):
        if self.temp_config is not None:
            self.logger.debug('Releasing {} bytes held by temporary config'.format(
                self.temp_config.tell()))
            self.temp_config.close()
