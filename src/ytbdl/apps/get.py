#pylint: disable=consider-using-f-string
import re
import shlex
import sys
from subprocess import CalledProcessError, run
from pathlib import Path

import confuse

from ytbdl import config_exists, config
from ytbdl.beets import beet_import, create_temp_config
from ytbdl.exceptions import ConfigurationError
from ytbdl.apps.base import BaseApp


def ytdl_options(value: str) -> list:
    ''' Convert a string into a set of command line arguments for yt-dlp

    Args:
        value (str): Input string received

    Returns:
        (list): A valid list of command line arguments for yt-dlp
    '''
    if not value:
        return []

    args = shlex.split(value)
    for arg in ('-x', '--extract-audio'):
        if arg in args:
            raise ValueError(
                f'The {arg} yt-dlp option is already specified for you, you do '
                'not need to add it'
            )
    for arg in ('-o', '--output'):
        if arg in args:
            raise ValueError(
                f'The {arg} yt-dlp option is already in use, you may not '
                'specify a custom output format'
            )
    return args

class DownloadApp(BaseApp):
    ''' App to download and tag audio files downloaded from the internet.
    '''

    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        dl_parser = sub_parser.add_parser(name='get', description=(
            'download one or more audio files with yt-dlp before tagging them '
            'as an album with beets. beets\' behaviour can be changed by '
            'modifying the ytbdl config file, which is itself a beets config '
            'file. the config file also has a ytdl_args option that can be '
            'used to control yt-dlp\'s behaviour (or use --ytdl-args)'
        ))
        dl_parser.add_argument('-v', '--verbose', action='store_true', help=(
            'log verbose (debug) information'
        ))
        dl_parser.add_argument('-y', '--ytdl-args', default=[],
            type=ytdl_options, help=(
            'command line arguments to pass to yt-dlp. For example: '
            '"--format bestaudio[ext=m4a]". you may also specify yt-dlp '
            'options in the ytdl_args setting in the config file. you may '
            'not use -x/--extract-audio or -o/--output as these are already in '
            'use. --ytdl-args are always combined with any existing args in '
            'the ytdl_args config option'
        ))
        dl_parser.add_argument('artist', help=(
            'the artist who created the album'
        ))
        dl_parser.add_argument('album', help=(
            'the name of the album to download'
        ))
        dl_parser.add_argument('urls', nargs='+', help=(
            'one or more URLs to download audio from'
        ))

    INVALID_FILENAME_CHARS = re.compile(r'[^\w\-_\. ]')
    DEFAULT_YTDL_ARGS = ['--extract-audio', '--output', "%(title)s.%(ext)s"]

    def __init__(self):
        self.verbose = False
        self.logger = None
        self.temp_config = None

    def configure_logging(self):
        level = 'DEBUG' if self.verbose else 'INFO'
        self.logger = self.get_logger('ytbdl', level)

    def start_execution(self, arg_parser, **kwargs):
        self.verbose = kwargs.get('verbose')
        self.configure_logging()
        if not config_exists():
            self.logger.info('Create a config before continuing with:')
            self.logger.info('ytbdl config create')
            return

        artist_name = kwargs.get('artist')
        album_name = kwargs.get('album')
        urls = kwargs.get('urls')

        # Combine console and configuration ytdl args
        extra_args = kwargs.get('ytdl_args', [])
        try:
            for config_arg in config['ytdl_args'].get(list):
                if config_arg not in extra_args:
                    extra_args.append(config_arg)
        except confuse.exceptions.NotFoundError:
            self.logger.debug('ytdl_args option was not found in config file')
        except confuse.exceptions.ConfigTypeError:
            self.logger.error('ytdl_args config option is not a list!')
            self.logger.warning('Aborting')
            sys.exit(1)

        try:
            self.logger.info(msg='Downloading "{0}" by {1}'.format(
                album_name, artist_name
            ))
            album_dir = self.create_album_dir(artist_name, album_name)
            self.download_music(album_dir, extra_args, urls)
            self.logger.info(msg='Autotagging album downloaded to {0}'.format(
                str(album_dir)
            ))
            self.autotag_album(album_dir)
        except KeyboardInterrupt:
            self.logger.info('User interrupted program.')
            self.logger.info('Aborting.')
            sys.exit(2)
        except FileExistsError as exc:
            self.logger.error(msg='FileExistsError: {0}'.format(str(exc)))
            self.logger.warning('Aborting')
            sys.exit(1)
        except (CalledProcessError, ConfigurationError) as exc:
            self.logger.error(msg='{0} encountered:'.format(
                exc.__class__.__name__
            ))
            self.logger.error(msg=str(exc))
            self.logger.warning('Aborting')
            sys.exit(1)
        finally:
            self.logger.debug('Cleaning up')
            self.cleanup()

    def create_album_dir(self, artist: str, album: str) -> Path:
        ''' Create the artist and album folders for the music to be moved into.
        If the album folder already exists and is not empty, an exception is
        raised as this may indicate that the album has already been downloaded.

        The directory structure is created under the current directory in this
        manner:

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
            self.logger.debug(msg='Creating artist folder "{0}"'.format(
                artist_folder
            ))
            artist_folder.mkdir()
        album_folder = artist_folder / self.clean_path_name(album)
        if album_folder.exists() and list(album_folder.glob('*')):
            raise FileExistsError(
                'The album folder "{0}" already exists and is not empty'.format(
                    str(album_folder)
                )
            )
        if not album_folder.exists():
            self.logger.debug(msg='Creating album folder "{0}"'.format(
                album_folder
            ))
            album_folder.mkdir()
        return album_folder

    def download_music(self, album_dir: Path, extra_args: list, urls: list):
        ''' Downloads one or more songs using yt-dlp in a subprocess into the
        album_dir.

        Embedding yt-dlp is not well documented. Calling yt-dlp, a Python
        program, from within Python makes the most sense, but there is no easy
        way to map from the command line options to a dict. Embedding yt-dlp
        only seems to make sense if the argument list is static, which it is
        not, here.

        Args:
            album_dir (Path): The directory to download files into
            urls (list): A list of URLs to download music from.
        '''
        if extra_args:
            self.logger.info(msg='Using extra arguments for yt-dlp: {0}'.format(
                ' '.join(extra_args)))
        else:
            self.logger.debug('No extra arguments for yt-dlp found')
        command = ['yt-dlp', *self.DEFAULT_YTDL_ARGS, *extra_args, '--', *urls]
        self.logger.debug(msg='Opening subprocess: {0}'.format(
            ' '.join(command)
        ))
        result = run(
            args=command,
            check=True,
            shell=False,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd=str(album_dir))
        result.check_returncode()
        self.logger.debug('yt-dlp exited with return code 0')

    def autotag_album(self, album_dir: Path):
        ''' Autotag the downloaded music with beets. The configuration for beets
        is combined with ytbdl's configuration file.

        Args:
            album_dir (Path): The directory the album was downloaded to
        '''
        import_dir = str(album_dir.parent.parent.resolve()).replace('\\', '/')
        self.temp_config = create_temp_config(import_dir)
        self.logger.debug('Created a temporary in-memory beets config')
        beet_import(album_dir, self.temp_config)

    def clean_path_name(self, name):
        ''' Replace any invalid file name characters with an underline

        Args:
            name (str): The file name

        Returns:
            (str): A sanitized filename
        '''
        return self.INVALID_FILENAME_CHARS.sub('_', name)

    def cleanup(self):
        ''' Remove the temporary config from memory
        '''
        if self.temp_config is not None:
            self.logger.debug(msg=(
                'Releasing {} bytes held by temporary config'.format(
                self.temp_config.tell()
            )))
            self.temp_config.close()
