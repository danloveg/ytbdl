import confuse
from pathlib import Path

config = confuse.LazyConfig('dlalbum', None)

def get_loaded_config_sources():
    config.resolve()
    config_files = []
    for source in config.sources:
        if source.filename:
            config_files.append(source.filename)
    return config_files

def get_main_config_path():
    return Path(config.config_dir()) / 'config.yaml'

def config_exists():
    return bool(get_loaded_config_sources())
