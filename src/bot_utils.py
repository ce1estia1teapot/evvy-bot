import datetime
import difflib
import discord
import json
import logging
import os
import yaml
import difflib

from configparser import ConfigParser
from datetime import datetime as DateTime
from difflib import SequenceMatcher
from discord import Client, Guild, Intents, TextChannel
from typing import Dict, List, Self

from enums import GuildPinAddResult, GuildPinRemoveResult

# ==== SETUP ====
global client
global main_logger
global guild_pins_directory

main_logger = logging.getLogger(name='main_logger')
guild_pins_directory = os.getcwd() + "/data/guild_pin_collections"

#region ==== CLASSES ====
class GuildPin():
    """
    A class representing a single pinned message in a particular guild
    """
    guild_id : int   
    channel_id : int
    message_id : int

    pin_creation_time : DateTime
    title : str
    tags : List[str]
    description : str
    
    target_author_global_name : discord.User
    target_creation_time : DateTime
    target_message_contents : str    

    def __init__(self, p_title : str = None, p_tags : List[str] = None, p_description : str = None, 
                 guild_id : int = None, pin_creation_time : DateTime = None, target_author_global_name : str = None, 
                 target_creation_time : DateTime = None, message_id : str = None, target_message_contents : str = None,
                 channel_id : int = None):
        """
        Constructs a GuildPin from provided discord messages
        """
        main_logger.debug('ENTERING GUILDPIN CONSTRUCTOR')

        self.guild_id = None
        self.channel_id = None
        self.message_id = None

        self.pin_creation_time = None
        self.title = None
        self.tags = []
        self.description = None
        
        self.target_author_global_name = None
        self.target_creation_time = None
        self.target_message_contents  = 'None'

        # Check for basic info
        if (p_title) and (isinstance(p_title, str)) and (p_title != ""):
            self.title = p_title
        else:
            self.title = DateTime.now()

        if (p_description) and (isinstance(p_description, str)):
            self.description = p_description
        else:
            self.description = ""
        
        if (p_tags) and (isinstance(p_tags, List)):
            for tag in p_tags:
                if (tag) and (isinstance(tag, str)):
                    self.tags.append(tag.lower())
        if (guild_id) and (isinstance(guild_id, int)):
            self.guild_id = guild_id
        if (pin_creation_time) and (isinstance(pin_creation_time, DateTime)):
            self.pin_creation_time = pin_creation_time
        
        if (target_author_global_name) and (isinstance(target_author_global_name, str)):
            self.target_author_global_name = target_author_global_name
        if (target_creation_time) and (isinstance(target_creation_time, DateTime)):
            self.target_creation_time = target_creation_time
        if (channel_id) and (isinstance(channel_id, int)):
            self.channel_id = channel_id
        if (message_id) and (isinstance(message_id, int)):
            self.message_id = message_id
        if (target_message_contents) and (isinstance(target_message_contents, str)):
            self.target_message_contents = target_message_contents
    
    def __json__(self) -> Dict:
        final_dict : Dict = {
            "guild_id" : self.guild_id,
            "channel_id" : self.channel_id,
            "message_id" : self.message_id,

            "pin_creation_time" : self.pin_creation_time.isoformat(),
            "title" : self.title,
            "tags" : self.tags,
            "description" : self.description,

            "target_author_global_name" : self.target_author_global_name,
            "target_creation_time" : self.target_creation_time.isoformat(),
            "target_message_contents" : self.target_message_contents,

            "__Guild_Pin__" : True
        }
        return final_dict

    @classmethod
    def _from_json(cls, data : Dict):
        main_logger.debug("_from_json_ called on GuildPin class")
        if not "__Guild_Pin__" in data:
            main_logger.debug("Failed to find class flag '__Guild_Pin__' in data. Returning None")
            return None

        final_object = cls(p_title = data["title"], 
                   p_tags = data["tags"], 
                   p_description = data["description"], 
                   guild_id = data["guild_id"], 
                   channel_id = data["channel_id"],
                   message_id = data["message_id"], 
                   pin_creation_time = DateTime.fromisoformat(data["pin_creation_time"]),  
                   target_author_global_name = data["target_author_global_name"], 
                   target_creation_time = DateTime.fromisoformat(data["target_creation_time"]), 
                   target_message_contents = data["target_message_contents"]
                )
        return final_object

    @classmethod
    def create_pin_from_message(cls, p_title : str = None, p_tags : List[str] = None, p_description : str = None, 
                                 p_target_message : discord.Message = None):
        """
        Alternate constructor that creates a GuildPin with only the basic fields filled plus the message ID's
        """
        guild_id = None
        channel_id = None
        pin_creation_time = None

        target_author_global_name = None
        target_creation_time = None
        target_message_id = None
        target_message_contents = None

        # Check for target Message
        if p_target_message:
            main_logger.debug('Received target message... parsing info')
            guild_id = int(p_target_message.guild.id)
            channel_id = int(p_target_message.channel.id)
            pin_creation_time = p_target_message.created_at

            target_author_global_name = p_target_message.author.global_name
            target_creation_time = p_target_message.created_at
            target_message_id = p_target_message.id
            target_message_contents = p_target_message.content
            
            return cls(p_title=p_title, p_tags=p_tags, p_description=p_description, 
                            guild_id=guild_id, channel_id=channel_id, pin_creation_time=pin_creation_time,
                            target_author_global_name=target_author_global_name,
                            target_creation_time=target_creation_time,
                            message_id=target_message_id, 
                            target_message_contents=target_message_contents
                        )
        else:
            main_logger.debug('target_message was None. No info to parse')
        
    def get_display_string(self):
        target_date_string : str = f'{self.target_creation_time.month}/{self.target_creation_time.day}/{self.target_creation_time.year}'        
        
        final_string : str = {f' **{self.title}** \n Author: {self.target_author_global_name} \n -# Message Creation Time: {target_date_string} \n -# {self.tags} \n {self.description} \n `{self.target_message_contents}`'}
        return final_string
    
    def get_keyword_score(self, p_keywords : List[str] = None) -> int:
        """
        Searches the pin's title, tags, description, and target message contents.

        Returns the number of occurances of the keyword throughout the pin. 
        """
        similarity_threshold : float = 0.8

        if (not p_keywords) or (not isinstance(p_keywords, List)):
            return 0

        final_score : int = 0
        all_words : List[str] = full_string.split(" ")

        full_string = self.title + " " + self.description + " "  + " "  + self.target_message_contents
        for tag in self.tags:
            full_string = full_string + " " + tag

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
    tag_match_threshold = 0.7

    ## The guild ID this set of pins belongs to
    guild_id : int
    guild_pins : List[GuildPin]

    def __init__(self, p_guild_id : int = None, p_guild_pins : List[GuildPin] = None):
        self.guild_id = p_guild_id

        if p_guild_pins:
            self.guild_pins = p_guild_pins
        else:
            self.guild_pins = []
    
    def __json__(self) -> Dict:
        final_dict : Dict = {
            "guild_id" : self.guild_id,
            "guild_pins" : [pin.__json__() for pin in self.guild_pins if hasattr(pin, "__json__")],

            "__Guild_Pin_Collection__" : True
        }
        return final_dict
    
    @classmethod
    def _from_json(cls, data : Dict):
        main_logger.debug("_from_json_ called on GuildPinCollection class")

        # If there is data but flag isn't found, return
        if (len(data) > 0) and (not "__Guild_Pin_Collection__" in data):
            main_logger.debug("Failed to find class flag '__Guild_Pin_Collection_' in data. Returning None")
            return None

        # If there is no data, create a blank one
        if (len(data) == 0):
            return_collection = cls()
        else:
            # Otherwise, populate with data
            guild_id : str = int(data["guild_id"])
            guild_pins : List[GuildPin] = [GuildPin._from_json(pin) for pin in data["guild_pins"]]

        return cls(guild_id, guild_pins)

    def add_pin(self, p_pin : GuildPin) -> GuildPinAddResult:
        """
        Adds a pin to the GuildPinCollection
        Returns: bool representing whether the GuildPin was successfully added to the GuildPinCollection

        1. Checks whether the pin is in the collection
        2. Checks whether the target message_id is found in any pins of the collection
        """
        if (p_pin) and (isinstance(p_pin, GuildPin)):
            main_logger.debug("Valid GuildPin received. Performing checks to add to collection...")
            message_id_search : List[str] = [(x.message_id == p_pin.message_id) for x in self.guild_pins if x.message_id]

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
    
    def get_refined_collection(self, p_tags : List[str] = None, p_author_names : List[str] = None) -> List[GuildPin]:
        """
        Returns a filtered list of GuildPins from the collection that are filtered by Tags and sorted by keywords
        """
        
        final_collection : List[GuildPin] = self.guild_pins
        tag_similarity_threshold : float = 0.8

        # Filter Pins by tags
        if (p_tags) and len(p_tags) > 0:
            def compare_pin_tags(pin : GuildPin):
                for self_tag in pin.tags:
                    for tag in p_tags:
                        tag = tag.lower()
                        matcher = difflib.SequenceMatcher(None, self_tag, tag)
                        
                        if matcher.ratio() < tag_similarity_threshold:
                            final_collection.remove(pin)
                            return
            for pin in self.guild_pins:
                compare_pin_tags(pin)
            main_logger.debug(f'Filtered to ({len(final_collection)}/{len(self.guild_pins)}) pins based on tags')
        else:
            main_logger.debug("No GuildPin tag(s) selected for filtering")
        
        if p_author_names:
            # Filter pins by author
            final_collection = [pin for pin in final_collection if pin.target_author_global_name in p_author_names]
            main_logger.debug(f'Filtered to ({len(final_collection)}/{len(self.guild_pins)}) pins based on author')
        else:
            main_logger.debug("No GuildPin author(s) selected for filtering")

        return final_collection

    def get_collection_tags(self) -> List[str]:
        final_tags : List[str] = []

        for pin in self.guild_pins:
            for sample_tag in pin.tags:
                if len(final_tags) == 0:
                    final_tags.append(sample_tag)
                    continue

                for return_tag in final_tags:
                    matcher : SequenceMatcher = SequenceMatcher(a=sample_tag, b=return_tag)

                    if matcher.ratio() <= self.tag_match_threshold:
                        final_tags.append(sample_tag)
        return final_tags
    
    @classmethod
    def retrieve_guild_pin_collection_from_file(cls, p_guild_id : int = None) -> Self:
        """
        Retrieves guild pins from file if one exists. If not, creates one and hands it back
        
        Assumes filenames of the format [guild_id].json
        """
        # abs_target_file_path : str = f'{guild_pins_directory}\\{p_guild_id}.json'
        file_name : str = f'{p_guild_id}.json'
        abs_target_file_path : str = os.path.join(guild_pins_directory, file_name)

        # Guard clauses
        if (not p_guild_id):
            main_logger.debug("No guild ID provided")
            return None    
        if not os.path.isdir(guild_pins_directory):
            os.mkdir(guild_pins_directory)
        if not os.path.isfile(abs_target_file_path):
            main_logger.debug(f'No GuildPinCollection file found for GuildID {p_guild_id}. Creating an empty one.')

            with open(abs_target_file_path, 'wt') as file:
                pass
        
        try:
            with open(abs_target_file_path, 'rt') as file:
                # TODO: Implement retrieval of GuildPinCollection file contents
                contents = json.load(file)
                pin_collection : GuildPinCollection = GuildPinCollection._from_json(contents)
        
                # If collection wasn't found on disk
                if not pin_collection:
                    main_logger.debug("Pin collection was None after load. Creating an empty one with the provided GuildID")
                    pin_collection = GuildPinCollection(p_guild_id=p_guild_id, p_guild_pins=[])
                else:
                    main_logger.debug(f'Valid pin collection retrieved. Returning: {pin_collection}')

                main_logger.debug(f'Returning GuildPinCollection: {pin_collection}')
                return pin_collection
        except json.decoder.JSONDecodeError as e:
            pin_collection = GuildPinCollection(p_guild_id=p_guild_id)

            main_logger.error(f'Found a file for GuildID {p_guild_id}, but failed to decode JSON file. Returning empty GuildPinCollection')
            return pin_collection
        except IOError as e:
            pin_collection = GuildPinCollection(p_guild_id=p_guild_id)

            main_logger.error(f'Failed to read target file: {abs_target_file_path} \n {e}')
            return pin_collection
    

    def save_guild_pin_collection_to_file(self):
        """
        Saves the provided collection to the pin collection file associated with the provided guild id. Overwrites existing file if one is found
        
        Assumes filenames of the format [guild_id].json
        """

        if not self:
            main_logger.error("pin collection not provided. Returning None")
            return None
        if not self.guild_id:
            main_logger.error("pin collection has no associated GuildID - cannot save. Returning None")
            return None
        
        guild_id : int = self.guild_id
        # target_file_name : str = f'{guild_pins_directory}\\{guild_id}.json'
        file_name : str = f'{guild_id}.json'
        abs_target_file_path : str = os.path.join(guild_pins_directory, file_name)

        if os.path.isfile(abs_target_file_path):
            main_logger.debug(f'Found target file. Removing before saving to enable overwrite...')
            os.remove(abs_target_file_path)

        try:
            with open(abs_target_file_path, 'wt') as file:
                json.dump(obj=self, fp=file, cls=GuildPinCollectionJSONEncoder)
        except IOError as e:
            main_logger.error(f'Failed to read target file: {abs_target_file_path}\n {e}')
        
        main_logger.info(f'Saved {len(self.guild_pins)} pins to file for Guild: {guild_id}')

    
class GuildPinJSONEncoder(json.JSONEncoder):
    def default(self, obj : GuildPin):
        if isinstance(obj, GuildPin) and (hasattr(obj, "__json__")):
            return obj.__json__()
        return super().default(obj)

class GuildPinCollectionJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GuildPinCollection):
            return obj.__json__()
        return super().default(obj)

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

#region ==== APPENDIX ====
# class EvvyClient(Client):
#     token : str
#     guilds_joined : List[Guild]
    
#     # Constructor
#     def __init__(self, p_intents : Intents, p_token : str=None):
#         super().__init__(intents=p_intents)
#         self.token = p_token
#         self.guilds_joined = [self.fetch_guilds()]

#     async def on_ready(self):
#         """
#         Callback for when the client receives the 'ready' event. Should:
#             1. Write to debugger indicating successful login
#             2. Sync bot commands with tree, output status message when done
#             3. List currently connected guilds
#         """
#         #  Report Log in
#         logMessage : str = f'Logged in as: {self.user}\n'
#         main_logger.info(logMessage)

#         # List Connected guilds
#         main_logger.info('===== Connected to Guilds: =====')
#         for guild in self.guilds:
#             info_string : str = f' {guild.name} ({len(guild.members)} members)'
#             main_logger.info(info_string)
        
#         # Sync Commands
#         main_logger.info('Initiating command tree sync...')
#         try:
#             synced = await self.sync_commands()
#             synced_commands = [c.name for c in synced]
#             main_logger.info(f'Synced {len(synced)} commands: {synced_commands}')
#         except Exception as e:
#             main_logger.exception(f'Encountered an error when syncing app commands: \n{e}')

#     async def on_guild_join(self, p_guild: Guild):
#         """
#         Callback that triggers when the bot joins a guild. Should:
#             1. Write to debugger that a guild was successfully joined indicating the number of members in it
#             2. Post a message in each text channel advertising that the bot has joined
#         """

#         print(f' *** Joined {p_guild.name} *** ({len(p_guild.members)} members)')

#         textChannels = []
#         for channel in p_guild.channels:
#             if type(channel) is TextChannel:
#                 textChannels.append(channel)        
#         if len(textChannels > 0):
#             channel = textChannels[0]
#             await channel.send(content='Bot Online!')

#     async def on_guild_remove(self, p_guild: Guild):
#         """
#         Callback that triggers when the bot is removed from a guild
#         """
        
#         print(f' *** Removed From Guild: {p_guild.name} ***')

#     # Slash command: /hello
#     @discord.slash_command(name="hello", description="Say hello to the bot!")
#     async def hello(self, ctx: discord.ApplicationContext):
#         await ctx.respond(f"Hello, {ctx.author.mention}!")