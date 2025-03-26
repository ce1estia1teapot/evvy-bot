import configparser
import datetime
import discord
import logging.config
import os
import yaml

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import app_commands, User, Member, Guild, TextChannel, Message, Intents, ScheduledEvent
from discord import Interaction, InteractionType
from discord.ext import commands
from typing import Dict, List, Union

from bot_utils import retrieve_bot_token, setup_logging

# ==== GLOBALS ====
global main_logger
global evvy_client

#region ==== CLASSES ====
class GuildEvent:
    event : ScheduledEvent


class EvvyClient(discord.Client):
    token : str
    guilds_joined : List[Guild]
    
    # Constructor
    def __init__(self, p_intents : Intents, p_token : str=None):
        super().__init__(intents=p_intents)
        self.tree = app_commands.CommandTree(self)

        self.token = p_token
        self.guilds_joined = [self.fetch_guilds()]

    #region ==== EVENT CALLBACKS ====
    async def setup_hook(self):
        # Sync Commands
        main_logger.info('Initiating command tree sync...')
        try:
            synced = await self.tree.sync()
            synced_commands = [c.name for c in synced]
            main_logger.info(f'Synced {len(synced)} commands: {synced_commands}')
        except Exception as e:
            main_logger.exception(f'Encountered an error when syncing app commands: \n{e}')

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
    async def echo(self, interaction : discord.Interaction, message : str):
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

    @app_commands.command(name='sample_events_menu', description='Responds with a select menu populated with ScheduledEvents from the server')
    async def events_menu(self, interaction: discord.Interaction):
        guild = interaction.guild
        events = await guild.fetch_scheduled_events()
        
        if not events:
            await interaction.response.send_message("No scheduled events found.")
            return

        options = [
            discord.SelectOption(label=event.name, value=str(event.id), description=event.description or "No description")
            for event in events
        ]

        class EventSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Select an event", options=options)

            async def callback(self, select_interaction: discord.Interaction):
                selected_event = discord.utils.get(events, id=int(self.values[0]))
                if selected_event:
                    await select_interaction.response.send_message(f'You selected: {selected_event.name}')

        class EventView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(EventSelect())

        await interaction.response.send_message("Select an event from the menu:", view=EventView())


    #endregion

    #region ==== CLASS METHODS ====
    @classmethod
    def bind_commands_to_client(cls, p_client : discord.Client) -> discord.Client:
        p_client.tree.add_command(EvvyClient.echo)
        p_client.tree.add_command(EvvyClient.button_example)
        p_client.tree.add_command(EvvyClient.events_menu)

        return p_client
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
    bound_evvy_client = EvvyClient.bind_commands_to_client(evvy_client)
    bound_evvy_client.run(bot_token)
#endregion