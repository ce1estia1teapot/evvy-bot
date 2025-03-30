import datetime
import discord
import logging
import os
import yaml

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import Client, Guild, Intents, TextChannel
from typing import Dict, List

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


#region ==== CLASSES ====
class GuildPin():
    """
    A class representing a single pinned message in a particular guild
    """
    guild_id : str   
    pin_creation_time : DateTime
    
    target_author : discord.User
    target_creation_time : DateTime
    target_message_id : str

    originating_author : discord.User
    originating_message_id : str

    def __init__(self, p_target_message : discord.Message = None, p_originating_message : discord.Message = None):
        """
        Constructs a GuildPin from provided discord messages
        """
        main_logger.debug('ENTERING GUILDPIN CONSTRUCTOR')

        if p_target_message:
            main_logger.debug('Received target message... parsing info')

            self.target_author = p_target_message.author.global_name
            self.target_creation_time = p_target_message.created_at
            self.target_message_id = p_target_message.id
        else:
            main_logger.debug('target_message was None. No info to parse')
        
        if p_originating_message:
            main_logger.debug('Received originating message... parsing info')

            self.guild_id = p_originating_message.guild.id
            self.pin_creation_time = p_originating_message.created_at

            self.originating_author = p_originating_message.author.global_name
            self.originating_message_id = p_originating_message.id
        else:
            main_logger.debug('originating_message was None. No info to parse')



class GuildPinCollection():
    """
    A class representing a collection of GuildPins for a particular guild
    """
    ## The guild ID this set of pins belongs to
    guild_id : str
    guild_pins : List[GuildPin]

class EvvyClient(Client):
    token : str
    guilds_joined : List[Guild]
    
    # Constructor
    def __init__(self, p_intents : Intents, p_token : str=None):
        super().__init__(intents=p_intents)
        self.token = p_token
        self.guilds_joined = [self.fetch_guilds()]

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
            synced = await self.sync_commands()
            synced_commands = [c.name for c in synced]
            main_logger.info(f'Synced {len(synced)} commands: {synced_commands}')
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
    
    #region ==== COMMANDS ====
    # Slash command: /hello
    @discord.slash_command(name="hello", description="Say hello to the bot!")
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}!")
    #endregion
#endregion