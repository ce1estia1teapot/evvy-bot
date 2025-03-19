import discord
import logging.config

from modules.bot_config_loader.main import BotConfigLoader

# Client Definition
class FjunnyClient(discord.Client):
    settings : BotConfigLoader

    def __init__(self, p_config_path : str, p_secrets_path : str, intents, **options):
        super().__init__(intents=intents, **options)

        self.settings = BotConfigLoader(p_config_path, p_secrets_path)

    async def on_ready(self):
        datetimeString = utils.get_current_datetime_string()
        logMessage: str = f'{datetimeString} Logged in as: {self}\n'

        print(logMessage)

        # List Connected guilds
        print(f'{utils.get_current_datetime_string()} ===== Connected to Guilds: =====')
        for guild in self.guilds:
            print(f'{utils.get_current_datetime_string()} {guild.name} ({len(guild.members)} members)')

        print('\n')

    async def on_guild_join(self, p_guild: Guild):
        print(f'{utils.get_current_datetime_string()} *** Joined {p_guild.name} *** ({len(p_guild.members)} members)')

        textChannels = []
        for channel in p_guild.channels:
            if type(channel) is TextChannel:
                textChannels.append(channel)
        for channel in textChannels:
            # if len(textChannels) > 0:
            #     channel = textChannels[0]
            await channel.send(content='Bot Online!')

    async def on_guild_remove(self, p_guild: Guild):
        print(f'{utils.get_current_datetime_string()} *** Removed From Guild: {p_guild.name} ***')

    async def on_message(self, p_message: Message):
        pass

    async def on_typing(self, p_channel: TextChannel, p_user: [User, Member], p_when: DateTime):
        pass


def main():
    pass


if __name__ == "__main__":
    
    
        
    main()