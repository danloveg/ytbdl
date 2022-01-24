#pylint: disable=consider-using-f-string
from pathlib import Path
from subprocess import CalledProcessError
import re
import sys

import confuse

from ytbdl import config_exists, config
from ytbdl.apps.base import BaseApp
from ytbdl.beets import beet_import
from ytbdl.exceptions import ConfigurationError
from ytbdl.yt_dlp import ytdl_options, download_audio


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
        extra_args = kwargs.get('ytdl_args', [])

        try:
            # Construct yt-dlp extra arguments
            if 'ytdl_args' in config:
                for config_arg in config['ytdl_args'].get(list):
                    if config_arg not in extra_args:
                        extra_args.append(config_arg)
            else:
                self.logger.debug('ytdl_args not found in config file')

            album_dir = self.get_album_dir(artist_name, album_name)

            # Download music to directory (yt-dlp will create the directory if
            # it's missing)
            self.logger.info(msg='Downloading "{0}" by {1}'.format(
                album_name, artist_name
            ))
            download_audio(album_dir, extra_args, urls, self.logger)

            # Autotag music in directory
            self.logger.info(msg='Autotagging album downloaded to {0}'.format(
                str(album_dir)
            ))
            beet_import(album_dir, self.logger)

        except confuse.exceptions.ConfigTypeError:
            self.logger.error('ytdl_args config option is not a list!')
            self.logger.warning('Aborting')
            sys.exit(1)
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


    def get_album_dir(self, artist: str, album: str) -> Path:
        ''' Get the path to the artist/album folder. If the album folder already
        exists and is not empty, an exception is raised as this may indicate
        that the album has already been downloaded.

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
            (Path): A path to the album folder relative to the current directory
        '''
        def sanitize_path(name):
            return self.INVALID_FILENAME_CHARS.sub('_', name)

        album_folder = Path('.') / sanitize_path(artist) / sanitize_path(album)
        if album_folder.exists() and list(album_folder.glob('*')):
            raise FileExistsError(
                'The album folder "{0}" already exists and is not empty'.format(
                    str(album_folder)
                )
            )
        return album_folder
