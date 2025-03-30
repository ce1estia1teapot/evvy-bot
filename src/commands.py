import discord
import logging

from discord import ApplicationContext, SlashCommandGroup, Option, Message, User
from discord.ui import Modal
from discord.ext.commands import Bot

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

#region ==== PIN COMMANDS ====
pin_group : SlashCommandGroup = SlashCommandGroup(name='pin', description='Command group for handling the creation of pins in a server')

@pin_group.command(name='create', description='Create a pin for the server. Reply to the message you want to pin with this command')
async def create(ctx : ApplicationContext, target_message_id : str = Option(description='The message ID of the message you want to pin')):

    if (not target_message_id) or (target_message_id == ''):
        ctx.respond('You didnt provide a message id for me to find')

    # 1. Retrieve target message. If successful, move on. If not, send error message.
    target_message : Message
    try:
        target_message = await ctx.fetch_message(target_message_id)
    except discord.NotFound as e:
        await ctx.respond(f'I couldn\'t find the message you referred to. Message ID: {target_message_id}')
    except discord.Forbidden as e:
        await ctx.respond(f'I dont have the permissions required to get that message. Message ID: {target_message_id}')
    except discord.HTTPException as e:
        await ctx.respond(f'Retrieving the message failed. Message ID: {target_message_id}')
    
    if target_message:
        main_logger.info(f'Retrieved target message: {target_message.id}')
        
        main_logger.info(f'Responding with Pin creation Modal...')
        modal : PinCreateModal = PinCreateModal()
        await ctx.send_modal(modal)
    else:
        return
    
    # 2. Respond with the pin creation modal
    raise NotImplementedError()

@pin_group.command(name="list", description="List all pins for the server stored by the bot")
async def list(ctx : ApplicationContext) -> None:
    """
    A function which lists all pins for the guild in which the command was invoked. Responds with a modal allowing the user to choose options for display
    """

    modal : PinListModal = PinListModal()
    await ctx.send_modal(modal)
#endregion

#region ==== UTILITY FUNCTIONS ====
def handle_pin_list_modal_submit(p_pin_list_modal : PinListModal = None):
    if not p_pin_list_modal:
        main_logger.info('Didnt receive a modal argument')
    if not isinstance(p_pin_list_modal, PinListModal):
        main_logger.debug(f'Provided Modal is of the wrong type: {p_pin_list_modal}')

    

#endregion
