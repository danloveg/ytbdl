#pylint: disable=consider-using-f-string
from pathlib import Path
from subprocess import CalledProcessError
import shlex
import sys

from yt_dlp import main as yt_dlp_main

class SysExitSignal(Exception):
    ''' Signals a sys.exit() call
    '''
    def __init__(self, exit_code, *args, **kwargs):
        self.exit_code = exit_code
        super().__init__(*args, **kwargs)


def download_audio_embedded(album_dir: Path, extra_args: list, urls: list, logger):
    ''' Downloads one or more songs using yt-dlp into the album_dir. If the
    album_dir does not exist, yt-dlp will create it.

    To trigger yt-dlp, its main() function is called. Because the main()
    function may exit with sys.exit(), it is necessary to patch the sys.exit
    function temporarily while yt-dlp does its thing, so as not to exit from
    the ytbdl application.

    Args:
        album_dir (Path): The directory to download files into
        extra_args (list): A list of arguments to pass to yt-dlp
        urls (list): A list of URLs to download music from.
        logger: A logging object
    '''
    if extra_args:
        logger.info(
            msg='Using extra arguments for yt-dlp: {0}'.format(
            ' '.join(extra_args)
        ))
    else:
        logger.debug('No extra arguments for yt-dlp found')

    # Arguments used instead of sys.argv
    override_argv = [
        '--extract-audio',
        '--output',
        str(album_dir / '%(title)s.%(ext)s'),
        *extra_args,
        '--',
        *urls
    ]

    logger.debug(msg=(
        'Using the following yt-dlp args in place of sys.argv: {0}'.format(
        ' '.join(override_argv)
    )))

    # Patch sys.exit() so yt-dlp can't hijack the current process and exit too
    # early
    unpatched_exit = getattr(sys, 'exit')
    try:
        def patched_exit(*args, **_):
            exit_code = args[0]
            raise SysExitSignal(exit_code, 'yt-dlp exited with code {0}'.format(
                exit_code
            ))
        setattr(sys, 'exit', patched_exit)

        # Run yt-dlp's main() function
        yt_dlp_main(argv=override_argv)

    except SysExitSignal as exc:
        if exc.exit_code != 0:
            raise CalledProcessError(
                exc.exit_code, ['yt-dlp', *override_argv]
            ) from exc

    finally:
        sys.exit = unpatched_exit


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
