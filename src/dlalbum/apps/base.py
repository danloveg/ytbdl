import re
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

    def get_human_friendly_exception_name(self, exception):
        return re.sub('([A-Z])', r' \1', exception.__class__.__name__).strip()

    def print_exc(self, exception):
        name = self.get_human_friendly_exception_name(exception)
        print(f'{self.error_text(name)}:', exception)
