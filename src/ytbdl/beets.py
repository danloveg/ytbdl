#pylint: disable=consider-using-f-string
from argparse import Namespace as ArgparseNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
import os

from beets import config as beetsconfig
from beets.ui import _setup as setup_beets
from beets.ui.commands import import_files

from ytbdl import beetsplug
from ytbdl import config, config_exists, get_main_config_path
from ytbdl.exceptions import ConfigurationError


# Keys and their required content in the config file
REQUIRED_VARIABLES = (
    ('directory', r'{import_dir}'),
    ('pluginpath', r'{beetsplug_dir}'),
)

# Plugins required in plugins: list in the config file
REQUIRED_PLUGINS = (
    'fromdirname',
    'fromyoutubetitle',
)


def beet_import(album_dir: Path, logger):
    ''' Emulates the behaviour of calling Beets' import function from a shell,
    in an embedded fashion. This bypasses a lot of the overhead required in
    creating a new subprocess as well as for other set up. Since the default
    beets config and library are used, no custom processing is required to set
    those up.

    Behind the scenes, beets will open a
    :code:`beets.ui.commands.TerminalImportSession` so that users can enter
    input via stdin. That function will emit the cli_exit event in case the user
    has activated any plugins that rely on this event. All of this functionality
    is emulated here.

    Args:
        album_dir (Path): A path to an album directory where some music exists
        logger: A logging object
    '''
    import_dir = str(Path(album_dir).parent.parent.resolve()).replace('\\', '/')
    beetsplug_dir = str(Path(beetsplug.__file__).parent.resolve()).replace('\\', '/')

    config_content = get_custom_config_contents(
        import_dir=import_dir,
        beetsplug_dir=beetsplug_dir
    )

    with TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, 'config.yaml')

        with open(temp_file_path, 'w', encoding='utf-8') as temp_config:
            temp_config.write(config_content)

        logger.debug(msg=('Created a temporary beets config at: {0}'.format(
            temp_file_path
        )))

        setup_options = ArgparseNamespace(
            directory=None,
            config=temp_file_path,
            plugins=None,
            library=None,
        )

        _, plugins, library = setup_beets(setup_options)

        # Start the import
        paths = [str(album_dir).encode('utf-8')]
        import_files(library, paths, None)

        # Clean up
        plugins.send('cli_exit', lib=library)
        library._close()
        beetsconfig.clear()


def get_custom_config_contents(**template_args) -> str:
    ''' Get the content of the custom beets configuration specified in ytbdl's
    config, and verify that the options with "DO NOT REMOVE" were not removed by
    the user.

    Args:
        **template_args: Supplied arguments to fill ytbdl's string template

    Returns:
        (str): ytbdl's config, with filled template arguments
    '''
    if not config_exists():
        raise ConfigurationError('Could not find a config file')

    for required_key, required_content in REQUIRED_VARIABLES:
        if required_key not in config:
            raise ConfigurationError(
                'The "{0}" key is missing from the configuration file. Add it '
                'back, and set it to: "{1}" (keep the quotes)'.format(
                    required_key, required_content
                )
            )
        found_content = config[required_key].as_str()
        if found_content != required_content:
            raise ConfigurationError(
                'The "{0}" key in the configuration file must be set to '
                '"{1}," but found "{2}"'.format(
                    required_key, required_content, found_content
                )
            )

    plugin_list = config['plugins'].get(list)
    for required_plugin in REQUIRED_PLUGINS:
        if required_plugin not in plugin_list:
            raise ConfigurationError(
                'The "{0}" plugin is missing from the plugins list in the '
                'configuration file. Add it back before continuing'.format(
                    required_plugin
                )
            )

    raw_beets_template = ''
    with open(get_main_config_path(), 'r', encoding='utf-8') as file_pointer:
        raw_beets_template = file_pointer.read()

    return raw_beets_template.format(**template_args)
