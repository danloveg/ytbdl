import shutil
from pathlib import Path
from types import SimpleNamespace

from beets import config as beetsconfig
from beets.ui import _setup
from beets.ui.commands import import_func

from dlalbum import beetsplug


def get_beetsplug_dir() -> Path:
    return str(Path(beetsplug.__file__).parent.resolve()).replace('\\', '/')

def get_beets_config_path() -> Path:
    config_path = Path(beetsconfig.user_config_path())
    if not config_path.exists():
        config_path.touch()
    return config_path.resolve()

def overwrite_beets_config(new_contents: str) -> Path:
    beets_config_path = get_beets_config_path()
    backup_path = (beets_config_path.parent / (beets_config_path.name + '.bkp')).resolve()
    shutil.move(beets_config_path, backup_path)
    with open(beets_config_path, 'w') as write_handle:
        write_handle.write(new_contents)
    return backup_path

def restore_backup_beets_config(backup_path: Path):
    if not backup_path.exists():
        raise FileNotFoundError(f'Backup beets config file "{backup_path}" does not exist')
    shutil.move(backup_path, get_beets_config_path())

def beet_import(album_dir: Path):
    ''' Emulates the behaviour of calling Beets' import function from a shell, in an embedded
    fashion. This bypasses a lot of the overhead required in creating a new subprocess as well as
    for other set up. Since the default beets config and library are used, no custom processing is
    required to set those up.

    Behind the scenes, beets opens a :code:`beets.ui.commands.TerminalImportSession` so that users
    can enter input via stdin. This function will emit the cli_exit event in case the user has
    activated any plugins that rely on this event.

    Args:
        album_dir (Path): A path to the directory where the music was downloaded
    '''
    # Create fake namespaces that would normally be created by parsing command line args
    setup_options = SimpleNamespace(directory=None, config=None, plugins=None, library=None)
    import_options = SimpleNamespace(copy=None, library=None)

    _, plugins, library = _setup(setup_options)
    import_func(library, import_options, [str(album_dir)])
    plugins.send('cli_exit', lib=library)
    library._close()
