import configparser
import os

from configparser import ConfigParser
from typing import List, Dict

class BotConfigLoader:
    config_path : str
    secrets_path : str

    _config_parser : ConfigParser
    _secrets_parser : ConfigParser

    def __init__(self, p_config_path : str, p_secrets_path : str):
        self._config_parser = ConfigParser()
        self._secrets_parser = ConfigParser()

        if os.path.isfile(p_secrets_path):
            raise NotImplemented()
            self._secrets_parser.read_dict
            print()
            
        if os.path.isfile(p_config_path):
            raise NotImplemented()


    def load_config():
        
        if not os.path.isfile:
            raise NotImplemented()

if __name__ == "__main__":

    loader : BotConfigLoader = BotConfigLoader
