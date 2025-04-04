import discord
import logging

from discord import ApplicationContext, SlashCommandGroup, Option, Message, User, Interaction
from discord.ui import Modal, View
from discord.abc import GuildChannel
from discord.ext.commands import Bot

from bot_utils import GuildPin, GuildPinCollection, retrieve_guild_pin_collection_from_file, save_guild_pin_collection_to_file
from typing import List, Callable
from views import PinListView, PinCreateModal

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
async def callback_pin_list_view(p_pin_list_view : PinListView = None):
    """
    Called when the PinListView is submitted
    """

    # Extract info
    selected_tags : List[str] = p_pin_list_view.tags_select.values
    selected_authors : List[User] = p_pin_list_view.authors_select.values
    ctx : ApplicationContext = p_pin_list_view.ctx
    guild_id : int = int(ctx.guild.id)

    # Retrieve pin collection
    pin_collection : GuildPinCollection = retrieve_guild_pin_collection_from_file(guild_id)

    # Refine with submitted values
    refined_pins : List[GuildPin] = pin_collection.get_refined_collection(p_tags=selected_tags, p_author_names=selected_authors)

    # Display refined pin collection?
    final_string : str = ''
    for pin in refined_pins:
        final_string = f'{final_string} \n {pin.get_display_string()}'
    
    ctx.respond(final_string)


async def callback_pin_create_modal(p_pin_create_modal : PinCreateModal, p_interaction : Interaction):
    """
    Function to be provided as a callback when creating a PinCreateModal
    """
    if (not p_pin_create_modal):
        main_logger.error("Modal not provided. Exiting")
        return
    if (not p_interaction):
        main_logger.error("Interaction not provided. Exiting process")
        return

    target_message : Message = p_pin_create_modal.target_message

    guild_id : int = int(target_message.guild.id)

    title : str = p_pin_create_modal.title_input.value
    tags : List[str] = p_pin_create_modal.tags_input.value.replace(' ', '').split(',')
    description : str = p_pin_create_modal.description_input.value

    # Create pin from new info
    new_guild_pin : GuildPin = GuildPin.create_pin_from_message(p_title=title, p_tags=tags, p_description=description, p_target_message=target_message)
    main_logger.info(f'Created a new GuildPin from the modal data and target message: {new_guild_pin}')

    # Attempt to retrieve pin collection and add new pin
    pin_collection : GuildPinCollection = retrieve_guild_pin_collection_from_file(p_guild_id=guild_id)
    main_logger.info(f'Retrieved GuildPinCollection from file: {pin_collection}')

    pin_collection.add_pin(new_guild_pin)

    # Save updated pin collection to disk
    main_logger.debug("Initiating GuildPinCollection file save...")
    save_guild_pin_collection_to_file(pin_collection)

    # Respond with success message
    main_logger.debug("Responding with final success message...")
    await p_interaction.respond(f'Saved pin #{len(pin_collection.guild_pins)}')
#endregion
    


#region ==== PIN COMMANDS ====
pin_group : SlashCommandGroup = SlashCommandGroup(name='pin', description='Command group for handling the creation of pins in a server')

@pin_group.command(name='create', description='Create a pin for the server. Provide the link to the message you want to save.')
async def create(ctx : ApplicationContext, message_link : str = Option(str, "Link to target message")):
    """
    Uses the replied-to message (target message) to create a GuildPin and add to corresponding GuildPinCollection
    """
    main_logger.info("Entered the /pin create event handler")

    guild_id : int
    channel_id : int
    message_id : int
    channel : GuildChannel
    target_message : Message
    
    # Retrieve the target message from the link provided in the initiating message. Split on slashes, then choose the last element. It will always be the message ID
    split_message_link : List[str] = message_link.split('/')
    try:
        guild_id = int(split_message_link[-3])
        channel_id = int(split_message_link[-2])
        message_id = int(split_message_link[-1])

        target_channel = await ctx.guild.fetch_channel(channel_id)
        target_message = await target_channel.fetch_message(message_id)
    except discord.NotFound:
        main_logger.error(f'Failed to find the target message.  Guild: {guild_id}  Channel: {channel_id}  Message: {message_id}')
        await ctx.respond("Message not found! Make sure the ID is correct.", ephemeral=True)
        return
    except discord.Forbidden:
        main_logger.error(f'Insufficient bot permissions to read message history.  Guild: {guild_id}  Channel: {channel_id}  Message: {message_id}')
        await ctx.respond("I don't have permission to read message history!", ephemeral=True)
        return
    except discord.HTTPException:
        main_logger.error(f'Failed to fetch message. HTTPException.   Guild: {guild_id}  Channel: {channel_id}  Message: {message_id}')
        await ctx.respond("Failed to fetch the message. Please try again.", ephemeral=True)
        return

    
    # Respond with the pin creation modal
    modal : PinCreateModal = PinCreateModal(p_callback=callback_pin_create_modal, p_target_message=target_message)
    await ctx.send_modal(modal)

@pin_group.command(name="list", description="List all pins for the server stored by the bot")
async def list(ctx : ApplicationContext) -> None:
    """
    A function which lists all pins for the guild in which the command was invoked. Responds with a modal allowing the user to choose options for display
    """
    main_logger.info("Entered the /pin list event handler")

    # Retrieve collection for the guild
    pin_collection : GuildPinCollection = retrieve_guild_pin_collection_from_file(ctx.guild_id)

    # If succcessful, get the tags for that guild and hand to modal constructor
    tags : List[str] = pin_collection.get_collection_tags()

    view : PinListView = PinListView(ctx=ctx, p_collection_tags=tags, p_external_callback=callback_pin_list_view)
    await ctx.send("Select the options you want to filter by", view=view)
#endregion

    

#endregion
