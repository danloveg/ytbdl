import argparse

from .apps.config import ConfigApp
from .apps.download import DownloadApp

ACTIVATED_APPS = {
    'config': ConfigApp,
    'download': DownloadApp,
}

def main():
    arg_parser = get_app_arg_parser()
    parsed_namespace = arg_parser.parse_args()
    arguments = vars(parsed_namespace)
    application = ACTIVATED_APPS[arguments['sub-app']]()
    application.start_execution(arg_parser, **arguments)

def get_app_arg_parser():
    app_parser = argparse.ArgumentParser()
    subparser = app_parser.add_subparsers(title='Sub-application Choice')
    subparser.required = True
    subparser.dest = 'sub-app'
    for _, class_ in ACTIVATED_APPS.items():
        class_.add_sub_parser_arguments(subparser)
    return app_parser

if __name__ == '__main__':
    main()
