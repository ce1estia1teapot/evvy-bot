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
        raise NotImplementedError()

class PinCreateModal(Modal):
    target_message : Message

    title_input : InputText
    tags_input : InputText
    description_input : InputText

    def __init__(self, p_target_message : Message = None):
        super().__init__(title="Pin Creation (Optional Info)")
        if p_target_message:
            self.target_message = p_target_message

        self.title_input = InputText(label="Title (defaults to empty)", placeholder="Title you want the pin to have", required=False, style=InputTextStyle.singleline)
        self.tags_input = InputText(label="Tags (optional, defaults to empty)", placeholder="Comma separated list of tags: lethalcompany, repo, theforest, etc...", required=False, style=InputTextStyle.short)
        self.description_input = InputText(label="Description (Optional)", placeholder="This is a really funny clip where someone in it goes hehehehe", required=False, style=InputTextStyle.paragraph)

        self.add_item(self.title_input)
        self.add_item(self.tags_input)
        self.add_item(self.description_input)

    async def on_submit(self, interaction: Interaction):        
        await interaction.response.send_message("Sorry I don't know what to do with that yet")
        raise NotImplementedError()
        # await interaction.response.send_message(f"You entered: {self.input.value}", ephemeral=True)


#endregion