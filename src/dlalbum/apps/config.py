from textwrap import dedent
from argparse import RawTextHelpFormatter

from dlalbum.apps.base import BaseApp

class ConfigApp(BaseApp):
    @staticmethod
    def add_sub_parser_arguments(sub_parser):
        config_parser = sub_parser.add_parser(name='config',
                                              formatter_class=RawTextHelpFormatter)
        config_parser.add_argument('action',
                                   choices=['path', 'edit', 'create', 'dump'],
                                   type=str,
                                   help=dedent('''\
                                       path: Show the path to the configuration file
                                       edit: Edit the configuration file. Requires editor to be set
                                       edit: Create a new, empty configuration file
                                       dump: Show the contents of the configuration file
                                       '''))

    def start_execution(self, arg_parser, **kwargs):
        print('This is the config app')
