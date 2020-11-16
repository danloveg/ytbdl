import shutil
import subprocess

from pathlib import Path
from textwrap import dedent
from argparse import RawTextHelpFormatter

from dlalbum import config, get_loaded_config_sources, config_exists, get_main_config_path
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
                                       create: Create a new, empty configuration file
                                       dump: Show the contents of the configuration file
                                       '''))

    def start_execution(self, arg_parser, **kwargs):
        config_action = kwargs.get('action')
        try:
            if config_action == 'create':
                if not config_exists():
                    self.create_new_config()
                else:
                    print('Configuration file already exists here:')
                    self.print_config_sources()

            elif config_action == 'edit':
                if not config_exists():
                    print('Create a config before continuing with:')
                    print('dlalbum config create')
                elif 'editor' in config:
                    editor = config['editor'].get(str)
                    config_file = Path(get_loaded_config_sources()[0])
                    config_file.resolve()
                    subprocess.call([editor, str(config_file)])
                else:
                    print('To edit your configuration like this, you must first specify which '
                          'editor to use for editing. You need to add a line in your config file '
                          'similar to the following text, substituting "notepad" for the editor '
                          'you want to use:')
                    print('\neditor: notepad')
                    print('\nYou can find your config file here:')
                    self.print_config_sources()

            elif config_action == 'path':
                if not config_exists():
                    print('Create a config before continuing with:')
                    print('dlalbum config create')
                else:
                    self.print_config_sources()

            elif config_action == 'dump':
                if not config_exists():
                    print('Create a config before continuing with:')
                    print('dlalbum config create')
                else:
                    with open(get_loaded_config_sources()[0], 'r') as config_file:
                        for line in config_file.readlines():
                            print(line.replace('\n', ''))
            else:
                arg_parser.error(f'Invalid config action: "{config_action}"')

        except subprocess.CalledProcessError as exc:
            self.print_exc(exc)
            print('Try adding the selected editor to your PATH before continuing, or just provide the '
                  'full path to the editor\'s executable')
        except Exception as exc:
            self.print_exc(exc)

    def print_config_sources(self):
        for source in get_loaded_config_sources():
            print(source.replace('\\\\', '/'))

    def create_new_config(self):
        new_config_file = get_main_config_path()
        default_config = Path(__file__).parent.parent / 'default_config.yaml'

        if not default_config.exists():
            print('The default_config.yaml file does not exist.')
        else:
            shutil.copy(default_config, new_config_file)
            print(f'Created a new configuration file at {new_config_file}.')
