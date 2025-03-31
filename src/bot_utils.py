import datetime
import discord
import logging
import os
import yaml
import difflib

from configparser import ConfigParser
from datetime import datetime as DateTime
from discord import Client, Guild, Intents, TextChannel
from typing import Dict, List

from enums import GuildPinAddResult, GuildPinRemoveResult

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
    title : str
    tags : List[str]
    description : str
    
    target_author_global_name : discord.User
    target_creation_time : DateTime
    target_message_id : str
    target_message_contents : str    

    originating_author_global_name : discord.User
    originating_message_id : str
    originating_message_contents : str

    def __init__(self, p_title : str = None, p_tags : List[str] = None, p_description : str = None, 
                 guild_id : str = None, pin_creation_time : DateTime = None, originating_author_global_name : str = None, 
                 originating_message_id : str = None, originating_message_contents : str = None, target_author_global_name : str = None, 
                 target_creation_time : DateTime = None, target_message_id : str = None, target_message_contents : str = None):
        """
        Constructs a GuildPin from provided discord messages
        """
        main_logger.debug('ENTERING GUILDPIN CONSTRUCTOR')

        # Check for basic info
        if (p_title) and (isinstance(p_title, str)) and (p_title != ""):
            self.title = p_title
        else:
            self.title = DateTime.now()

        if (p_description) and (isinstance(p_description, str)):
            self.title = p_title
        else:
            self.description = ""
        
        if (p_tags) and (isinstance(p_tags, List)):
            for tag in p_tags:
                if (tag) and (isinstance(tag, str)):
                    self.tags.append(tag.lower())
        if (guild_id) and (isinstance(guild_id, str)):
            self.guild_id = guild_id
        if (pin_creation_time) and (isinstance(pin_creation_time, DateTime)):
            self.pin_creation_time = pin_creation_time
        
        if (originating_author_global_name) and (isinstance(originating_author_global_name, str)):
            self.originating_author_global_name = originating_author_global_name
        if (originating_message_id) and (isinstance(originating_message_id, str)):
            self.originating_message_id = originating_message_id
        if (originating_message_contents) and (isinstance(originating_message_contents, str)):
            self.originating_message_contents = originating_message_contents
        
        if (target_author_global_name) and (isinstance(target_author_global_name, str)):
            self.target_author_global_name = target_author_global_name
        if (target_creation_time) and (isinstance(target_creation_time, DateTime)):
            self.target_creation_time = target_creation_time
        if (target_message_id) and (isinstance(target_message_id, str)):
            self.target_message_id = target_message_id
        if (target_message_contents) and (isinstance(target_message_contents, str)):
            self.target_message_contents = target_message_contents
    
    @classmethod
    def create_pin_from_messages(cls, p_title : str = None, p_tags : List[str] = None, p_description : str = None, 
                                 p_target_message : discord.Message = None, p_originating_message : discord.Message = None):
        """
        Alternate constructor that creates a GuildPin with only the basic fields filled plus the message ID's
        """
        guild_id = None
        pin_creation_time = None

        originating_author_global_name = None
        originating_message_id = None
        originating_message_contents = None

        target_author_global_name = None
        target_creation_time = None
        target_message_id = None
        target_message_contents = None
        
        # Check for originating message
        if p_originating_message:
            main_logger.debug('Received originating message... parsing info')

            guild_id = p_originating_message.guild.id
            pin_creation_time = p_originating_message.created_at

            originating_author_global_name = p_originating_message.author.global_name
            originating_message_id = p_originating_message.id
            originating_message_contents = p_originating_message.content
        else:
            main_logger.debug('originating_message was None. No info to parse')

        # Check for target Message
        if p_target_message:
            main_logger.debug('Received target message... parsing info')

            target_author_global_name = p_target_message.author.global_name
            target_creation_time = p_target_message.created_at
            target_message_id = p_target_message.id
            target_message_contents = p_target_message.content
        else:
            main_logger.debug('target_message was None. No info to parse')
        
        return cls.__init__(p_title=p_title, p_tags=p_tags, p_description=p_description, 
                            guild_id=guild_id, pin_creation_time=pin_creation_time,
                            originating_author_global_name=originating_author_global_name,
                            originating_message_id=originating_message_id, originating_message_contents=originating_message_contents,
                            target_author_global_name=target_author_global_name,
                            target_creation_time=target_creation_time,
                            target_message_id=target_message_id, target_message_contents=target_message_contents)
    
    def get_keyword_score(self, p_keywords : List[str] = None) -> int:
        """
        Searches the pin's title, tags, description, originating message contents, and target message contents.

        Returns the number of occurances of the keyword throughout the pin. 
        """
        similarity_threshold : float = 0.8

        if (not p_keywords) or (not isinstance(p_keywords, List)):
            return 0

        final_score : int = 0
        all_words : List[str] = full_string.split(" ")

        full_string = self.title + " " + self.description + " "  + self.originating_message_contents + " "  + self.target_message_contents
        for tag in self.tags:
            full_string = full_string + " " = tag

        for keyword in p_keywords:
            keyword = keyword.lower()

            # Searching the body of the pin and tags
            for word in all_words:
                matcher = difflib.SequenceMatcher(None, keyword, word)
                if matcher.ratio() > similarity_threshold:
                    main_logger.debug(f'Word match during keyword search. Keyword: {keyword}   Match: {word}')
                    final_score += 1

        # Log final score and return
        main_logger.info(f'Calculated GuildPin keyword score: {final_score}')        
        return final_score


class GuildPinCollection():
    """
    A class representing a collection of GuildPins for a particular guild
    """
    ## The guild ID this set of pins belongs to
    guild_id : str
    guild_pins : List[GuildPin]

    def __init__(self):
        self.guild_id = None
        self.guild_pins = []

    def add(self, p_pin : GuildPin) -> GuildPinAddResult:
        """
        Adds a pin to the GuildPinCollection
        Returns: bool representing whether the GuildPin was successfully added to the GuildPinCollection

        1. Checks whether the pin is in the collection
        2. Checks whether the target message_id is found in any pins of the collection
        """
        if (p_pin) and (isinstance(p_pin, GuildPin)):
            main_logger.debug("Valid GuildPin received. Performing checks to add to collection...")
            message_id_search : List[str] = [(x.target_message_id == p_pin.target_message_id) for x in self.guild_pins if x.target_message_id]

            is_pin_in_collection = p_pin in self.guild_pins
            is_target_message_id_in_collection = any(message_id_search)

            if not(is_pin_in_collection or is_target_message_id_in_collection):
                main_logger.info("GuildPin checks passed, adding to collection...")
                self.guild_pins.append(p_pin)
                return GuildPinAddResult.SUCCESS
            else:
                main_logger.info("Pin failed checks: Duplicate found.")
                return GuildPinAddResult.DUPLICATE_MESSAGE_FOUND
        else:
            main_logger.debug("Invalid GuildPin received")
            return GuildPinAddResult.INVALID_PIN_PROVIDED
    
    def remove(self, p_pin : GuildPin) -> GuildPinRemoveResult:
        """
        Removes a pin from the GuildPinCollection

        Returns: bool representing whether the GuildPin was successfully added to the GuildPinCollection
        """
        if (p_pin) and (isinstance(p_pin, GuildPin)):
            if p_pin in self.guild_pins:
                try:
                    self.guild_pins.remove(p_pin)
                    return GuildPinRemoveResult.SUCCESS
                except ValueError as e:
                    main_logger.error(f'Failed to find p_pin in self.guild_pins: {e}')
                finally:
                    return GuildPinRemoveResult.PIN_NOT_FOUND
            else:
                return GuildPinRemoveResult.PIN_NOT_FOUND
        else:
            GuildPinRemoveResult.INVALID_PIN_PROVIDED
    
    def get_refined_collection(self, p_keywords : List[str] = None, p_tags : List[str] = None) -> List[GuildPin]:
        """
        Returns a filtered list of GuildPins from the collection that are filtered by Tags and sorted by keywords
        """
        main_logger.debug("Refining collection based on tags and keywords....")

        final_collection : List[GuildPin] = []
        tag_similarity_threshold : float = 0.8

        # Filter Pins by tags
        def compare_pin_tags(pin : GuildPin):
            for self_tag in pin.tags:
                for tag in p_tags:
                    tag = tag.lower()
                    matcher = difflib.SequenceMatcher(None, self_tag, tag)
                    
                    if matcher.ratio() > tag_similarity_threshold:
                        final_collection.append(pin)
                        return
        for pin in self.guild_pins:
            compare_pin_tags(pin)        
        main_logger.debug(f'Filtered to ({len(final_collection)}/{len(self.guild_pins)}) pins based on tags')

        # Sort remaining Pins by keyword score
        sorted_pins = sorted(final_collection, key=lambda pin : pin.get_keyword_score(p_keywords), reverse=True)

        return sorted_pins


class EvvyClient(Client):
    token : str
    guilds_joined : List[Guild]
    
    # Constructor
    def __init__(self, p_intents : Intents, p_token : str=None):
        super().__init__(intents=p_intents)
        self.token = p_token
        self.guilds_joined = [self.fetch_guilds()]

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

    # Slash command: /hello
    @discord.slash_command(name="hello", description="Say hello to the bot!")
    async def hello(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Hello, {ctx.author.mention}!")
