#pylint: disable=consider-using-f-string
from subprocess import run
from pathlib import Path
import shlex
import sys


# yt-dlp arguments used regardless of invocation
DEFAULT_YTDL_ARGS = (
    '--extract-audio',
    '--output',
    "%(title)s.%(ext)s"
)


def download_audio(album_dir: Path, extra_args: list, urls: list, logger):
    ''' Downloads one or more songs using yt-dlp in a subprocess into the
    album_dir.

    Embedding yt-dlp is not well documented. Calling yt-dlp, a Python program,
    from within Python makes the most sense, but there is no easy
    way to map from the command line options to a dict. Embedding yt-dlp
    only seems to make sense if the argument list is static, which it is
    not, here.

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
    command = ['yt-dlp', *DEFAULT_YTDL_ARGS, *extra_args, '--', *urls]
    logger.debug(msg='Opening subprocess: {0}'.format(
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
    logger.debug('yt-dlp exited with return code 0')


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
