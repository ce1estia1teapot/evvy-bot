import discord
import logging

from discord import ApplicationContext, SlashCommandGroup, Option, Message, User
from discord.ext.commands import Bot

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

@pin_group.command(name='create', description='Create a pin for the server')
async def create(ctx : ApplicationContext, target_message_id : str = Option(description='The message ID of the message you want to pin')):

    # 1. Retrieve target message. If successful, move on. If not, send error message.
    target_message : Message
    if target_message_id:
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
        else:
            return
    
    # 2. Respond with the pin creation modal
    

#endregion
