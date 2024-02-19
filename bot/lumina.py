import os
from dotenv import load_dotenv
import random
import discord
from discord.ext import commands

class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        # self.add_cog(Commands(self))

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        
        if self.user in message.mentions:
            print(f"User {message.author} tagged {self.user}.")
            await message.channel.send(f"Hello, {message.author.name}!")

        # if message.content.startswith('!'):
        #     if message.content[1:] == "roll":
        #         print("rolling...")
        #         random_number = str(random.randint(1, 6))
        #         await message.channel.send(random_number)

        await self.process_commands(message)

    @commands.command()
    async def roll(self, ctx: commands.Context):
        print("rolling...")
        random_number = str(random.randint(1, 6))
        await ctx.channel.send(random_number)

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True

    lumina = LuminaBot(command_prefix=commands.when_mentioned_or('/'), intents=intents)
    
    lumina.run(TOKEN)
