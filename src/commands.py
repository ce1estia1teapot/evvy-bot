import discord
import logging

from discord import ApplicationContext, SlashCommandGroup, Option, Message, User, Interaction
from discord.ui import Modal
from discord.ext.commands import Bot

from bot_utils import GuildPin, GuildPinCollection
from typing import List, Callable
from views import PinListModal, PinCreateModal

#region ==== GLOBALS ====
global main_logger
main_logger = logging.getLogger(name='main_logger')


#region ==== TEST COMMANDS ====
test_group : SlashCommandGroup = SlashCommandGroup('test')

@test_group.command(name="sub1", description="First subcommand")
async def subcommand1(ctx : ApplicationContext):
    await ctx.respond("You called /test sub1!")

@test_group.command(name="sub2", description="Second subcommand")
async def subcommand2(ctx : ApplicationContext):
    await ctx.respond("You called /test sub2!")

#endregion

#region ==== UTILITY FUNCTIONS ====

#endregion

#region ==== CALLBACK FUNCTIONS ====
def callback_pin_list_modal(p_pin_list_modal : PinListModal, p_interaction : Interaction, p_originating_message : Message, p_target_message : Message):
    if not p_pin_list_modal:
        main_logger.info('Didnt receive a modal argument')
    if not isinstance(p_pin_list_modal, PinListModal):
        main_logger.debug(f'Provided Modal is of the wrong type: {p_pin_list_modal}')
    
    # 1. Extract keywords, tags, and guild info

    # 2. Retrieve guild pin collection from records

    # 3. Refine pin collection with keywords and tags

def callback_pin_create_modal(p_pin_create_modal : PinCreateModal, p_interaction : Interaction):
    """
    Function to be provided as a callback when creating a PinCreateModal
    """
    if (not p_pin_create_modal):
        main_logger.error("Modal not provided. Exiting")
        return
    if (not p_interaction):
        main_logger.error("Interaction not provided. Exiting process")
        return

    originating_message : Message = p_pin_create_modal.originating_message
    target_message : Message = p_pin_create_modal.target_message

    title : str = p_pin_create_modal.title_input.value
    tags : List[str] = p_pin_create_modal.tags_input.value.replace(' ', '').split(',')
    description : str = p_pin_create_modal.description_input.value

    new_guild_pin : GuildPin = GuildPin.create_pin_from_messages(p_title=title, p_tags=tags, p_description=description, p_target_message=target_message, p_originating_message=originating_message)
    

#endregion
    


#region ==== PIN COMMANDS ====
pin_group : SlashCommandGroup = SlashCommandGroup(name='pin', description='Command group for handling the creation of pins in a server')

@pin_group.command(name='create', description='Create a pin for the server. Reply to the message you want to pin with this command')
async def create(ctx : ApplicationContext):
    """
    Uses the replied-to message (target message) and the originating message to create a GuildPin and add to corresponding GuildPinCollection
    """

    # Retrieve initiating message
    originating_message : Message = ctx.interaction.message
    if not originating_message:
        main_logger.error("Couldnt retrieve the message that initiated the interaction")
        await ctx.respond("I couldn't find the message that initiated the interaction. Unable to create pin")
        return
    
    # Retrieve the target message from the initiating message
    target_message : Message
    is_replied_to : bool = True if not (originating_message.reference is None) else False
    if is_replied_to:
        target_message = originating_message.reference.resolved
        main_logger.debug(f'Found target_message from originating_message. Continuing...')
    else:
        main_logger.debug("Couldnt find replied message")
        ctx.respond('It doesnt appear that your message replies to anything. Unable to create pin.')
        return
    
    # Respond with the pin creation modal
    modal : PinCreateModal = PinCreateModal(p_callback=callback_pin_create_modal, p_originating_message=originating_message, p_target_message=target_message)
    ctx.send_modal(modal)

@pin_group.command(name="list", description="List all pins for the server stored by the bot")
async def list(ctx : ApplicationContext) -> None:
    """
    A function which lists all pins for the guild in which the command was invoked. Responds with a modal allowing the user to choose options for display
    """

    modal : PinListModal = PinListModal(p_submission_callback=callback_pin_list_modal)
    await ctx.send_modal(modal)
#endregion

    

#endregion
