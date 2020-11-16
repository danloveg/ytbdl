from .base import BaseApp

class DownloadApp(BaseApp):
    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        dl_parser = sub_parser.add_parser(name='download')
        dl_parser.add_argument('-u', '--urls', nargs='+',
                               help='One or more URLs to download audio from')
        dl_parser.add_argument('artist', help='The artist who created the album to download')
        dl_parser.add_argument('album', help='The name of the album to download')

    def start_execution(self, arg_parser, **kwargs):
        print('This is the download app')
