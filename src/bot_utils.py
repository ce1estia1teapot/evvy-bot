import os
import logging
import yaml

from configparser import ConfigParser
from typing import Dict

# ==== SETUP ====
global main_logger
main_logger = logging.getLogger(name='main_logger')

# ==== FUNCTIONS ====
def retrieve_bot_token(p_secrets_path : str) -> str:
    if os.path.isfile(p_secrets_path):
        secrets_parser : ConfigParser = ConfigParser()
        secrets_parser.read(p_secrets_path)

        try:
            token : str = secrets_parser['SECRETS']['token']
            return token
        except Exception as e:
            main_logger.exception(f'Trouble accessing token in secrets loader: {secrets_parser}')

    else:
        main_logger.error(f'Couldnt find secrets file: {p_secrets_path}')
