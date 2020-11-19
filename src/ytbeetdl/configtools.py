import yaml
import shlex

from ytbeetdl import config, config_exists
from ytbeetdl.beets import get_beetsplug_dir
from ytbeetdl.exceptions import ConfigurationError

def get_extra_youtube_dl_args() -> list:
    if not config_exists():
        raise ConfigurationError('Could not find a config file')
    extra_args = []
    if 'youtube-dl' in config and 'options' in config['youtube-dl']:
        arg_str = config['youtube-dl']['options'].as_str()
        extra_args = shlex.split(arg_str)
    return extra_args

def get_beets_config(import_dir) -> str:
    if not config_exists():
        raise ConfigurationError('Could not find a config file')
    if 'beets' not in config:
        raise ConfigurationError('beets key is missing in configuration')
    if 'config' not in config['beets']:
        raise ConfigurationError('config key is missing from beets in configuration')

    raw_beets_template = config['beets']['config'].as_str()

    # Load string as YAML to verify configuration
    beets_config = yaml.safe_load(raw_beets_template)
    if 'directory' not in beets_config:
        raise ConfigurationError('The directory key is missing from beets->config in configuration')
    if isinstance(beets_config['directory'], dict):
        raise ConfigurationError(r'beets->config->directory must be set as "{import_dir}" in '
                                 'configuration. Did you forget the double quotes?')
    if beets_config['directory'] != r'{import_dir}':
        raise ConfigurationError(r'beets->config->directory must be set as "{import_dir}" in '
                                 f"configuration, but found {beets_config['directory']}")
    if 'pluginpath' not in beets_config:
        raise ConfigurationError('The pluginpath key is missing from beets->config in '
                                 'configuration')
    if isinstance(beets_config['pluginpath'], dict):
        raise ConfigurationError(r'beets->config->pluginpath must be set as "{beetsplug_dir}" in '
                                 'configuration. Did you forget the double quotes?')
    if beets_config['pluginpath'] != r'{beetsplug_dir}':
        raise ConfigurationError(r'beets->config->pluginpath must be set as "{beetsplug_dir}" in '
                                 f"configuration, but found {beets_config['pluginpath']}")
    if 'plugins' not in beets_config:
        raise ConfigurationError('The plugins key is missing from beets->config in configuration')
    if 'fromdirname' not in beets_config['plugins']:
        raise ConfigurationError('fromdirname plugin is missing from beets->config->plugins in '
                                 'configuration')
    if 'fromyoutubetitle' not in beets_config['plugins']:
        raise ConfigurationError('fromyoutubetitle plugin is missing from beets->config->plugins '
                                 'in configuration')

    raw_beets_config = raw_beets_template.format(
        beetsplug_dir=str(get_beetsplug_dir()),
        import_dir=str(import_dir),
    )
    return raw_beets_config
