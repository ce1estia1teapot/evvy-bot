import discord
import logging

from discord import Interaction, InputTextStyle, Message, SelectOption, User, ComponentType, ApplicationContext
from discord.ui import Modal, InputText, Select, View
from typing import List, Callable

#region ==== GLOBALS ====
global main_logger
main_logger = logging.getLogger(name='main_logger')

#region ==== CLASSES ====
class AuthorSelect(Select):
        external_callback : Callable

        def __init__(self, external_callback : Callable = None, select_type = ComponentType.user_select, *, custom_id = None, placeholder = "Select users to filter by", min_values = 1, max_values = 1, options = None, channel_types = None, disabled = False, row = None):
            super().__init__(select_type, custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, channel_types=channel_types, disabled=disabled, row=row)
            self.external_callback = external_callback
        
        async def callback(self, interaction : Interaction):
            self.external_callback(self, interaction, self.values)

class PinListView(View):
    external_callback : Callable
    ctx : ApplicationContext

    tags_select : Select
    is_tags_select_submitted : bool
    tags_select_options : List[SelectOption]
    
    authors_select : Select
    is_authors_select_submitted : bool
    author_select_values : List[User]

    def __init__(self, ctx : ApplicationContext, p_collection_tags : List[str] = None, p_external_callback : Callable = None):
        super().__init__()
        self.ctx = ctx

        self.tags_select_options = []
        self.is_tags_select_submitted = False

        self.author_select_values = []
        self.is_authors_select_submitted = False

        if (not p_collection_tags):
            main_logger.debug(f'"None" provided for list of tags from collection.')
        if (len(p_collection_tags) == 0):
            main_logger.debug(f'PinListView received empty list of Pin tags: {p_collection_tags}')
        if p_external_callback:
            self.external_callback = p_external_callback

        # Sort tags
        sorted_tags : List[str] = sorted(p_collection_tags)
        sorted_tags.insert(0, "None")

        # Create SelectOptions from tags
        self.tags_select_options = []
        for tag in sorted_tags:
            temp_option : SelectOption = SelectOption(label=tag, value=tag)
            self.tags_select_options.append(temp_option)

        self.tags_select = Select(select_type=discord.ComponentType.string_select, placeholder="Select tags to filter by", options=self.tags_select_options)
        self.authors_select = AuthorSelect(external_callback=self.handle_author_select_callback)

        self.add_item(self.tags_select)
        self.add_item(self.authors_select)
    
    async def handle_tag_select_callback(self):
        self.is_tags_select_submitted = True

        if (self.is_tags_select_submitted) and (self.is_authors_select_submitted):
            self.submission_callback
    
    async def handle_author_select_callback(self):
        self.is_authors_select_submitted = True
        
        if (self.is_tags_select_submitted) and (self.is_authors_select_submitted):
            self.submission_callback

    def submission_callback(self):
        # Call external callback
        self.external_callback(self)
        

class PinCreateModal(Modal):
    submit_callback : Callable

    target_message : Message
    
    title_input : InputText
    tags_input : InputText
    description_input : InputText

    def __init__(self, p_callback : Callable = None, p_target_message : Message = None):
        super().__init__(title="Pin Creation (Optional Info)")
        if p_callback:
            self.submit_callback = p_callback
        if p_target_message and isinstance(p_target_message, Message):
            self.target_message = p_target_message

        self.title_input = InputText(label="Title (defaults to empty)", placeholder="Title you want the pin to have", required=False, style=InputTextStyle.singleline)
        self.tags_input = InputText(label="Tags (optional, defaults to empty)", placeholder="Comma separated list of tags: lethalcompany, repo, theforest, etc...", required=False, style=InputTextStyle.short)
        self.description_input = InputText(label="Description (Optional)", placeholder="This is a really funny clip where someone in it goes hehehehe", required=False, style=InputTextStyle.paragraph)

        self.add_item(self.title_input)
        self.add_item(self.tags_input)
        self.add_item(self.description_input)

    async def callback(self, interaction : Interaction):
        """
        Activated when modal is submitted. Used to invoke exte2rnal callback specified in constructor
        """
        await self.submit_callback(self, interaction)

#endregion