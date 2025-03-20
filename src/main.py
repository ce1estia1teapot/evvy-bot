import configparser
import datetime
import discord
import logging.config
import os
import discord.ext.commands
import yaml

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import app_commands, User, Member, Guild, TextChannel, Message, Intents
from discord import Interaction, InteractionType
from discord.ext.commands import Bot
from typing import Dict, List, Union

from bot_utils import retrieve_bot_token

# ==== FUNCTIONS ====


# ==== GLOBALS ====
global main_logger
global evvy_bot

# ==== Setup ====
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

evvy_bot = Bot(command_prefix='!', intents=intents)

# ==== EVENTS ====
@evvy_bot.event
async def on_ready():
        """
        'ready' event. Should:
            1. Write to debugger indicating successful login
            2. Sync bot commands with tree, output status message when done
            3. List currently connected guilds
        """
        #  Log in
        logMessage : str = f'Logged in as: {evvy_bot.user}\n'
        main_logger.info(logMessage)

        # Sync Commands
        synced = await evvy_bot.tree.sync()
        main_logger.info(f'Synced {len(synced)} commands')

        # List Connected guilds
        main_logger.info('===== Connected to Guilds: =====')
        for guild in evvy_bot.guilds:
            info_string : str = f' {guild.name} ({len(guild.members)} members)'
            main_logger.info(info_string)

@evvy_bot.event
async def on_guild_join(self, p_guild: Guild):
    """
    'on guild join' event. Should:
        1. Write to debugger that a guild was successfully joined indicating the number of members in it
        2. Post a message in each text channel advertising that the bot has joined
    """

    print(f' *** Joined {p_guild.name} *** ({len(p_guild.members)} members)')

    textChannels = []
    for channel in p_guild.channels:
        if type(channel) is TextChannel:
            textChannels.append(channel)
    for channel in textChannels:
        # if len(textChannels) > 0:
        #     channel = textChannels[0]
        await channel.send(content='Bot Online!')

@evvy_bot.event
async def on_guild_remove(self, p_guild: Guild):
    print(f' *** Removed From Guild: {p_guild.name} ***')

# ==== COMMANDS ====
@evvy_bot.tree.command(name='echo', description='Repeats your message.')
@app_commands.describe(message='The message to repeat')
async def echo(p_interaction : discord.Interaction, message : str):
    """
    echo command: Just echoes back a message sent by a user
    """
    
    await p_interaction.response.send_message(f'{author}: {message}')

# ==== UTILITY FUNCTIONS ====
def get_logger() -> logging.Logger:
    return main_logger


# ==== RUN THE BOT ====
evvy_bot.run(bot_token)