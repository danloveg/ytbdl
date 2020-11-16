from abc import ABC, abstractmethod

class BaseApp(ABC):
    @staticmethod
    @abstractmethod
    def add_sub_parser_arguments(sub_parser):
        pass

    @abstractmethod
    def start_execution(self, arg_parser, **kwargs):
        pass
