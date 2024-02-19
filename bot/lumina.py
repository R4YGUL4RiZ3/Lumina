import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        print(message.mentions)
        if self.user in message.mentions:
            await message.channel.send(f"Hello, {message.author.name}!")

        await self.process_commands(message)

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()

    lumina = LuminaBot(command_prefix='!', intents=intents)
    lumina.run(TOKEN)
