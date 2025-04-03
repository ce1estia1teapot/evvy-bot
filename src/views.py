import discord
import logging

from discord import Interaction, InputTextStyle, Message
from discord.ui import Modal, InputText
from typing import List, Callable

#region ==== GLOBALS ====
global main_logger
main_logger = logging.getLogger(name='main_logger')

#region ==== CLASSES ====
class PinListModal(Modal):
    submission_callback : Callable

    key_word_input : InputText
    tags_input : InputText

    def __init__(self, p_submission_callback : Callable = None):
        super().__init__(title="List Options")

        if p_submission_callback:
            self.submission_callback = p_submission_callback

        self.key_word_input = InputText(label="Key Words (Optional)", placeholder="Keywords to search for...", required=False, style=InputTextStyle.singleline)
        self.tags_input = InputText(label="Tags", placeholder="Tags to include lethalcompany, repo, theforest, etc...", required=False, style=InputTextStyle.short)

        self.add_item(self.key_word_input)
        self.add_item(self.tags_input)

    async def callback(self, interaction : Interaction):
        """
        call the external function when the modal is submitted
        """
        self.submission_callback(self, interaction)

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