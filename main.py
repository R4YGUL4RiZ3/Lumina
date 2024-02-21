import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from bot import LuminaBot
# from bot.lumina import LuminaCog

def main():
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = True

    lumina = LuminaBot(command_prefix='!', intents=intents)
    # lumina.add_cog(LuminaCog)
    
    lumina.run(TOKEN)


if __name__ == "__main__":
    main()
