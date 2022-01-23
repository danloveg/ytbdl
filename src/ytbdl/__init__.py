import os

import confuse

config = confuse.LazyConfig('ytbdl', None)

def get_loaded_config_sources():
    config.resolve()
    config_files = []
    for source in config.sources:
        if source.filename and os.path.exists(source.filename):
            config_files.append(source.filename)
    return config_files

def get_main_config_path():
    return os.path.join(config.config_dir(), 'config.yaml')

def config_exists():
    return bool(get_loaded_config_sources())
