import discord
import logging
import os
import yaml

from configparser import ConfigParser
from discord import Client
from typing import Dict

# ==== SETUP ====
global client
global main_logger
main_logger = logging.getLogger(name='main_logger')

#region ==== FUNCTIONS ====
def setup_logging() -> None:
    # Create Logs directory if it doesn't exist
    if not os.path.isdir('logs\\'):
        os.mkdir('logs')

    with open(file='config\\logging_config.yaml', mode='r') as file:
        try:
            # Setting up using config...
            config: Dict = yaml.safe_load(file)
            logging.config.dictConfig(config)

        except Exception as e:
            main_logger.exception(f'Unable to configure logging: {e}')
        main_logger.debug('Logging initialized')

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
#endregion

#region ==== COMMANDS ====



#endregion