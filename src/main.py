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

from bot_utils import retrieve_bot_token, setup_logging

# ==== GLOBALS ====
global main_logger
global evvy_client

#region ==== CLASSES ====
class EvvyClient(discord.Client):
    token : str

    # Constructor
    def __init__(self, p_intents : Intents, p_token : str=None):
        super().__init__(intents=p_intents)
        self.tree = app_commands.CommandTree(self)

        self.token = p_token

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

        # Sync Commands
        synced = await self.tree.sync()
        main_logger.info(f'Synced {len(synced)} commands')

        # List Connected guilds
        main_logger.info('===== Connected to Guilds: =====')
        for guild in self.guilds:
            info_string : str = f' {guild.name} ({len(guild.members)} members)'
            main_logger.info(info_string)

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
    # Slash command: /echo
    @app_commands.command(name='echo', description='Repeats your message.')
    @app_commands.describe(message='The message to repeat')
    async def echo(interaction : discord.Interaction, message : str):
        """
        echo command: Just echoes back a message sent by a user
        """
        author = interaction.user.global_name

        await interaction.response.send_message(f'{author} said: {message}')
    
    # Slash command: /button_example
    @app_commands.command(name="button_example", description="Sends a message with an interactive button.")
    async def button_example(self, interaction: discord.Interaction):
        class ButtonView(discord.ui.View):
            @discord.ui.button(label="Click Me", style=discord.ButtonStyle.primary)
            async def button_callback(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                await button_interaction.response.send_message("You clicked the button!")
        
        await interaction.response.send_message("Here is an interactive button!", view=ButtonView())
    #endregion

    #region ==== CLASS METHODS ====
    @classmethod
    def bind_commands_to_client(cls, p_client) -> None:
        p_client.tree.add_command(EvvyClient.echo)
        p_client.tree.add_command(EvvyClient.button_example)
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
    config_path : str = 'config\\bot_config.ini'
    bot_config : ConfigParser = ConfigParser()
    bot_config.read(config_path)

    # 4. Create intents, create client, bind commands, run client
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    evvy_client : EvvyClient = EvvyClient(p_intents=intents, p_token=bot_token)
    EvvyClient.bind_commands_to_client(evvy_client)
    evvy_client.run(bot_token)
#endregion