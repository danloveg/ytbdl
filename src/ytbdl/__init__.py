import os

import confuse

config = confuse.LazyConfig('ytbdl', None)

def get_loaded_config_sources():
    ''' Get existing configuration files

    Returns:
        (list): A list of (string) paths to configuration files that exist on
            the file system. Returns an empty list if no configuration files
            exist
    '''
    config.resolve()
    return [s.filename for s in config.sources if os.path.exists(s.filename)]

def get_main_config_path():
    ''' Get the main configuration file path

    Returns:
        (str): A path to the configuration file. This path may or may not exist
    '''
    return os.path.join(config.config_dir(), 'config.yaml')

def config_exists():
    ''' Determine if one or more configuration files exist.

    Returns:
        (bool): True if a config file exists, False otherwise
    '''
    return any(get_loaded_config_sources())
