import shutil
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import yaml

from beets import config as beetsconfig
from beets.ui import _setup
from beets.ui.commands import import_func
from confuse.yaml_util import load_yaml, Loader
from confuse.sources import ConfigSource

from ytbeetdl import beetsplug
from ytbeetdl import config, config_exists, get_main_config_path
from ytbeetdl.exceptions import ConfigurationError


def set_file_monkeypatch(filename):
    if isinstance(filename, BytesIO):
        file_path = None
        bytes_io = filename
        yaml_data = yaml.load(bytes_io, Loader=Loader)
    else:
        file_path = str(Path(filename).resolve())
        yaml_data = load_yaml(file_path, loader=Loader)
    beetsconfig.set(ConfigSource(yaml_data, file_path))


def beet_import(album_dir: Path, custom_config: BytesIO):
    ''' Emulates the behaviour of calling Beets' import function from a shell, in an embedded
    fashion. This bypasses a lot of the overhead required in creating a new subprocess as well as
    for other set up. Since the default beets config and library are used, no custom processing is
    required to set those up.

    Behind the scenes, beets opens a :code:`beets.ui.commands.TerminalImportSession` so that users
    can enter input via stdin. This function will emit the cli_exit event in case the user has
    activated any plugins that rely on this event.

    Args:
        album_dir (Path): A path to the directory where the music was downloaded
        config_file (BytesIO): A stream containing a custom beets configuration
    '''
    # Patch the config to change the set_file function
    setattr(beetsconfig, 'set_file', set_file_monkeypatch)
    # Create fake namespaces that would normally be created by parsing command line args
    setup_options = SimpleNamespace(directory=None, config=custom_config, plugins=None, library=None)
    import_options = SimpleNamespace(copy=None, library=None)
    # Start the import
    _, plugins, library = _setup(setup_options)
    import_func(library, import_options, [str(album_dir)])
    # Clean up
    plugins.send('cli_exit', lib=library)
    library._close()
    beetsconfig.clear()


def create_temp_config(import_dir: str) -> BytesIO:
    ''' Create an in-memory beets config file from the user's ytbeetdl config. '''
    if not config_exists():
        raise ConfigurationError('Could not find a config file')

    # Verify that the options with "DO NOT REMOVE" were not removed
    if 'directory' not in config:
        raise ConfigurationError('The directory key is missing from the configuration')
    if config['directory'].as_str() != r'{import_dir}':
        raise ConfigurationError(r'directory must be set as "{import_dir}" in the '
                                 f"configuration, but found {config['directory'].as_str()}")
    if 'pluginpath' not in config:
        raise ConfigurationError('The pluginpath key is missing from the configuration')
    if config['pluginpath'].as_str() != r'{beetsplug_dir}':
        raise ConfigurationError(r'pluginpath must be set as "{beetsplug_dir}" in the '
                                 f"configuration, but found {config['pluginpath'].as_str()}")
    if 'plugins' not in config:
        raise ConfigurationError('The plugins key is missing from the configuration')
    if 'fromdirname' not in config['plugins'].get(list):
        raise ConfigurationError('fromdirname plugin is missing from plugins list in the '
                                 'configuration')
    if 'fromyoutubetitle' not in config['plugins'].get(list):
        raise ConfigurationError('fromyoutubetitle plugin is missing from plugins list in the '
                                 'configuration')

    raw_beets_template = open(get_main_config_path(), 'r', encoding='utf-8').read()
    raw_beets_config = raw_beets_template.format(
        beetsplug_dir=str(get_beetsplug_dir()),
        import_dir=str(import_dir),
    )
    return BytesIO(raw_beets_config.encode('utf-8'))


def get_beetsplug_dir() -> Path:
    return str(Path(beetsplug.__file__).parent.resolve()).replace('\\', '/')
