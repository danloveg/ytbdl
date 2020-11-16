from abc import ABC, abstractmethod

from colorama import Fore, Style

class BaseApp(ABC):
    @staticmethod
    @abstractmethod
    def add_sub_parser_arguments(sub_parser):
        pass

    @abstractmethod
    def start_execution(self, arg_parser, **kwargs):
        pass

    def error_text(self, text):
        return f'{Fore.RED}{text}{Style.RESET_ALL}'
