import configparser
import datetime
import discord
import logging.config
import os
import yaml

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import Client, Intents, Guild, ScheduledEvent, TextChannel
from discord.ext import commands
from typing import Dict, List, Union

from bot_utils import retrieve_bot_token, setup_logging
from commands import test_group, pin_group

# ==== GLOBALS ====
global main_logger
global evvy_client
global nissi_naturals_id

#region ==== CLASSES ====
class EvvyBot(discord.Bot):
    guild_ids_to_sync : List[str]

    def __init__(self, p_guild_ids : List[str] = None, p_intents : discord.Intents = discord.Intents.default(), description=None, *args, **options):
        super().__init__(intents=p_intents)

        self.guild_ids_to_sync = p_guild_ids

    #region ==== EVENT CALLBACKS ====
    async def on_ready(self):
        """
        Callback for when the client receives the 'ready' event. Should:
            1. Write to debugger indicating successful login
            2. Sync bot commands with tree, output status message when done
            3. List currently connected guilds
        """
        #  Report Log in
        logMessage : str = f'Logged in as: {self.user}\n'
        main_logger.info(logMessage)

        # List Connected guilds
        main_logger.info('===== Connected to Guilds: =====')
        for guild in self.guilds:
            info_string : str = f' {guild.name} ({len(guild.members)} members)'
            main_logger.info(info_string)
        
        # Sync Commands
        main_logger.info('Initiating command tree sync...')
        try:
            synced = await self.sync_commands(guild_ids=self.guild_ids_to_sync)
        except Exception as e:
            main_logger.exception(f'Encountered an error when syncing app commands: \n{e}')

    async def on_guild_join(self, p_guild: Guild):
        """
        Callback that triggers when the bot joins a guild. Should:
            1. Write to debugger that a guild was successfully joined indicating the number of members in it
            2. Post a message in each text channel advertising that the bot has joined
        """

        print(f' *** Joined {p_guild.name} *** ({len(p_guild.members)} members)')

        textChannels = []
        for channel in p_guild.channels:
            if type(channel) is TextChannel:
                textChannels.append(channel)        
        if len(textChannels > 0):
            channel = textChannels[0]
            await channel.send(content='Bot Online!')

    async def on_guild_remove(self, p_guild: Guild):
        """
        Callback that triggers when the bot is removed from a guild
        """
        
        print(f' *** Removed From Guild: {p_guild.name} ***')
    #endregion
#endregion

#region ==== RUN THE BOT ====
if __name__ == "__main__":
    # 1. Setup Logging
    main_logger = logging.getLogger(name='main_logger')
    setup_logging()

    # 2. Grab bot token out of secrets file
    secrets_filepath : str = 'config\\secrets.cfg'
    bot_token : str = retrieve_bot_token(secrets_filepath)

    # 3. Load bot configuration
    # config_path : str = 'config\\bot_config.ini'
    # bot_config : ConfigParser = ConfigParser()
    # bot_config.read(config_path)

    # 4. Create intents, create client, bind commands, run client
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    nissi_naturals_id : str = '599028360471117861'

    nissi_bot: discord.Bot = EvvyBot(p_guild_ids=[nissi_naturals_id], p_intents=intents)
    nissi_bot.add_application_command(test_group)
    nissi_bot.add_application_command(pin_group)
    nissi_bot.run(bot_token)
#endregion