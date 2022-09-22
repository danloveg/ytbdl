from pathlib import Path
from subprocess import CalledProcessError
import shlex

from yt_dlp import main as yt_dlp_main


def download_audio(album_dir: Path, extra_args: list, urls: list, logger):
    ''' Downloads one or more songs using yt-dlp into the album_dir. If the
    album_dir does not exist, yt-dlp will create it.

    To trigger yt-dlp, its main() function is called. Because the main()
    function may exit with sys.exit(), it is necessary to catch SystemExit so as
    not to exit from the ytbdl application.

    Args:
        album_dir (Path): The directory to download files into
        extra_args (list): A list of arguments to pass to yt-dlp
        urls (list): A list of URLs to download music from.
        logger: A logging object
    '''
    if extra_args:
        logger.info('Using extra arguments for yt-dlp: %s', ' '.join(extra_args))
    else:
        logger.debug('No extra arguments for yt-dlp found')

    # Arguments used instead of sys.argv
    argv = [
        '--extract-audio',
        '--output',
        str(album_dir / r'%(title)s.%(ext)s'),
        *extra_args,
        '--',
        *urls
    ]

    logger.debug('Using the following yt-dlp args in place of sys.argv: %s', ' '.join(argv))

    try:
        yt_dlp_main(argv=argv)

    # Don't allow yt-dlp to hijack this process and exit too early
    except SystemExit as exc:
        if exc.code != 0:
            raise CalledProcessError(
                exc.code, ['yt-dlp', *argv]
            ) from exc


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
