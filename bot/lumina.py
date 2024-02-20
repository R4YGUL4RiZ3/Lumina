import os
import random
import json
from typing import *

import discord
from discord.ext import commands
from openai import OpenAI

from .chat import Chat
from .utils import *

class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.chat = Chat(self, load_instructions("./bot/instructions.txt"))

        self.bot_active = False

        self._cache_dir = "./cache"

    async def on_ready(self):
        guild = self.guilds[0]
        self._guild_metadata = {
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "creation_date": str(guild.created_at),
        }

        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        with open("./cache/guild_metadata.json", 'w') as f:
            json.dump(self._guild_metadata, f, indent=6)
        
        print(f"\nInstructions: {load_instructions("./bot/instructions.txt")}")

        print(f"{self.user} is now up and running!")

    async def on_message(self, message: discord.Message):
        # Debugging
        print(f"\n{message.author}: {message.content} ({message.channel})")
        if len(message.mentions) > 0:
            print(f"\nMentions: {message.mentions}")

        if message.author == self.user:
            return
        
        if (self.user in message.mentions) or (message.guild is None):
            try:
                self.bot_active = True
                await self.chat.init_thread()
                await message.channel.send("```You have now entered a converation session with Lumina. Type `!quit` to quit.```\n")
            except Exception as e:
                print(e)
                await message.channel.send("```Something went wrong```")

        if self.bot_active:
            try:
                async with message.channel.typing():
                    await self.chat.add_message(message)
                    await self.chat.respond(message)
            except Exception as e:
                print(e)
                await message.channel.send("```Something went wrong```")

        await self._handle_commands(message)
        await self.process_commands(message)

    async def _handle_commands(self, message):
        if message.content.startswith('!'):
            if not self.bot_active and message.content[1:] == "roll":
                print("rolling...")
                random_number = str(random.randint(1, 6))
                await message.channel.send(random_number)

            if self.bot_active and message.content[1:] == "quit":
                self.bot_active = False
                self.chat.cleanup()
                await message.channel.send("\n```You have successfully exit the conversation.```")
