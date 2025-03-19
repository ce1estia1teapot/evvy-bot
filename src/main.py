import configparser
import datetime
import discord
import logging.config
import os
import discord.ext.commands
import yaml

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import User, Member, Guild, TextChannel, Message, Intents
from typing import Dict, List, Union

import discord.ext

# ==== GLOBALS ====
global main_logger

# ==== CLASSES ====

class EvvyClient(discord.Client):
    async def on_ready(self):
        logMessage : str = f'Logged in as: {self}\n'

        main_logger.info(logMessage)

        # List Connected guilds
        main_logger.info('===== Connected to Guilds: =====')
        for guild in self.guilds:
            info_string : str = f' {guild.name} ({len(guild.members)} members)'
            main_logger.info(info_string)

    async def on_guild_join(self, p_guild: Guild):
        print(f' *** Joined {p_guild.name} *** ({len(p_guild.members)} members)')

        textChannels = []
        for channel in p_guild.channels:
            if type(channel) is TextChannel:
                textChannels.append(channel)
        for channel in textChannels:
            # if len(textChannels) > 0:
            #     channel = textChannels[0]
            await channel.send(content='Bot Online!')

    async def on_guild_remove(self, p_guild: Guild):
        print(f' *** Removed From Guild: {p_guild.name} ***')


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


def main():
    global main_logger

    # 1. Setup Logging
    main_logger = logging.getLogger(name='main_logger')
    setup_logging()

    # 2. Grab bot token out of secrets file
    secrets_filepath : str = 'config\\secrets.cfg'
    bot_token : str = retrieve_bot_token(secrets_filepath)

    # 3. Load bot configuration
    config_path : str = 'config\\bot_config.ini'
    bot_config : ConfigParser = ConfigParser()
    bot_config.read(config_path)

    # 4. Create Bot Client and run
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    evvy_client : EvvyClient = EvvyClient(intents=intents)
    
    evvy_client.run(bot_token)

if __name__ == "__main__":
    main()