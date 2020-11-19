import shutil
from pathlib import Path

from beets import config as beetsconfig

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
