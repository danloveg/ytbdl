import logging
from abc import ABC, abstractmethod

class BaseApp(ABC):
    @staticmethod
    @abstractmethod
    def add_sub_parser_arguments(sub_parser):
        pass

    @abstractmethod
    def start_execution(self, arg_parser, **kwargs):
        pass

    def get_logger(self, name, level):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter('[{name}] {levelname}: {message}', style='{')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
