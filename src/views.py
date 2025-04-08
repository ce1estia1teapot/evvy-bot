import discord
import logging

from discord import Interaction, InputTextStyle, Message, SelectOption, User, ComponentType, ApplicationContext, ButtonStyle
from discord.ui import Modal, InputText, Select, View, Button
from typing import List, Callable

#region ==== GLOBALS ====
global main_logger
main_logger = logging.getLogger(name='main_logger')

#region ==== CLASSES ====
class AuthorSelect(Select):
        external_callback : Callable

        def __init__(self, external_callback : Callable = None, select_type = ComponentType.user_select, *, custom_id = None, placeholder = "Select users to filter by", min_values = 0, max_values = 1, options = None, channel_types = None, disabled = False, row = None):
            super().__init__(select_type, custom_id=custom_id, placeholder=placeholder, min_values=min_values, max_values=max_values, options=options, channel_types=channel_types, disabled=disabled, row=row)
            self.external_callback = external_callback
        
        async def callback(self, interaction : Interaction):
            await self.external_callback(interaction)

class SubmitButton(Button):
    external_callback : Callable

    def __init__(self, p_external_callback : Callable = None, *, style = ButtonStyle.primary, label = None, disabled = False, custom_id = None, url = None, emoji = None, sku_id = None, row = None):
        super().__init__(style=style, label="Submit", disabled=disabled, custom_id=custom_id, url=url, emoji=emoji, sku_id=sku_id, row=row)

        if p_external_callback:
            self.external_callback = p_external_callback
        else:
            main_logger.error("Submit button not provided an external callback")
    
    async def callback(self, interaction : Interaction):
        self.style = ButtonStyle.green

        await self.external_callback(interaction)
        

class PinListView(View):
    external_callback : Callable
    ctx : ApplicationContext

    parent_interaction : Interaction

    tags_select : Select
    tags_select_options : List[SelectOption]
    tags_select_values : List[str]
    
    authors_select : Select
    authors_select_values : List[User]

    submit_button : SubmitButton

    def __init__(self, ctx : ApplicationContext, p_collection_tags : List[str] = None, p_external_callback : Callable = None):
        super().__init__()

        # Set initial values
        self.ctx = ctx
        self.parent_interaction = None

        self.tags_select_options = []
        self.tags_select_values = []

        self.authors_select_values = []

        if (not p_collection_tags):
            main_logger.debug(f'"None" provided for list of tags from collection.')
        if (len(p_collection_tags) == 0):
            main_logger.debug(f'PinListView received empty list of Pin tags: {p_collection_tags}')
        if p_external_callback:
            self.external_callback = p_external_callback

        # De-duplicate and Sort tags
        main_logger.debug(f'Received collection of {len(p_collection_tags)} tags')
        sorted_tags = []
        for tag in p_collection_tags:
            if not (tag in sorted_tags):
                sorted_tags.append(tag)

        sorted_tags : List[str] = sorted(sorted_tags)
        sorted_tags.insert(0, "None")
        main_logger.debug(f'Retrieved, de-duped, and sorted {len(sorted_tags)} tags (including None tag): {sorted_tags}')

        # Create SelectOptions from tags
        self.tags_select_options = []
        for tag in sorted_tags:
            temp_option : SelectOption = SelectOption(label=tag, value=tag)
            self.tags_select_options.append(temp_option)
        main_logger.debug(f'Created {len(self.tags_select_options)} SelectOptions for TagSelect dropdown: {[option.value for option in self.tags_select_options]}')

        # Create componens and add to view
        self.tags_select = Select(select_type=discord.ComponentType.string_select, placeholder="Select tags to filter by", options=self.tags_select_options, min_values=0, max_values=len(self.tags_select_options))
        self.authors_select = AuthorSelect(external_callback=self.author_select_callback, min_values=0, max_values=4)
        self.submit_button = SubmitButton(p_external_callback=self.submission_callback)

        self.add_item(self.tags_select)
        self.add_item(self.authors_select)
        self.add_item(self.submit_button)
    
    async def tag_select_callback(self, interaction : Interaction):
        selected_tags = self.tags_select.values
        self.tags_select_values = selected_tags

        main_logger.debug("PinListView tag selection was submitted.")
        await interaction.response.send_message(f"Tags selected: {selected_tags}", ephemeral=True)
        return
    
    async def author_select_callback(self, interaction : Interaction):
        selected_authors = self.authors_select.values
        self.authors_select_values = selected_authors

        main_logger.debug("PinListView author selection was submitted.")
        await interaction.response.send_message(f"Users selected: {[user.global_name for user in selected_authors]}", ephemeral=True)
        return

    async def submission_callback(self, interaction : Interaction = None):
        
        if interaction:
            main_logger.debug("PinListView submitted...")

            # Call external callback
            await self.external_callback(self, interaction)
        else:
            main_logger.error("No interaction provided to PinListView submission callback")
        return
        

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