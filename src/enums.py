import discord
import logging

from enum import Enum

# ==== SETUP ====
global client
global main_logger
main_logger = logging.getLogger(name='main_logger')

class GuildPinAddResult(Enum):
    SUCCESS = 1
    INVALID_PIN_PROVIDED = 2
    DUPLICATE_MESSAGE_FOUND = 3

class GuildPinRemoveResult(Enum):
    SUCCESS = 1
    INVALID_PIN_PROVIDED = 2
    PIN_NOT_FOUND = 3
