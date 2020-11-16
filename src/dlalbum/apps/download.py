from dlalbum.apps.base import BaseApp
from dlalbum import config_exists

class DownloadApp(BaseApp):
    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        dl_parser = sub_parser.add_parser(name='get')
        dl_parser.add_argument('artist', help='The artist who created the album to download')
        dl_parser.add_argument('album', help='The name of the album to download')
        dl_parser.add_argument('urls', nargs='+',
                               help='One or more URLs to download audio from')

    def start_execution(self, arg_parser, **kwargs):
        if not config_exists():
            print('Create a config before continuing with:')
            print('dlalbum config create')
            return

        artist_name = kwargs.get('artist')
        album_name = kwargs.get('album')
        urls = kwargs.get('urls')

        print('Downloading "{0}" by {1}'.format(album_name, artist_name))
