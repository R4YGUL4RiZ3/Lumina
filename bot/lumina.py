import os
import sys
import random
import json
from typing import *

import discord
from discord.ext import commands

from .client import Client
from .utils import *

class LuminaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context):
        if not self.bot.bot_active:
            print("rolling...")
            random_number = str(random.randint(1, 6))
            await ctx.send(random_number)

    @commands.command()
    async def quit(self, ctx: commands.Context):
        if self.bot.bot_active:
            self.bot.bot_active = False
            self.bot.client.cleanup()
            await ctx.send("\n```You have successfully exit the conversation.```")

    @commands.command()
    async def join_voice(self, ctx: commands.Context):
        channel = ctx.author.voice.channel
        if channel:
            await channel.connect()
        else:
            await ctx.send("You are not in a voice channel! Join one to get me to join.")
        
    @commands.command()
    async def leave_voice(self, ctx: commands.Context):
        voice = discord.utils.get(self.voice_clients, guild=self.guilds[0])
        
        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.channel.send("> Lumina Left the voice channel")
        else:
            await ctx.channel.send("I'm not in a voice channel!")
    
class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.client = Client(load_instructions("./bot/instructions.txt"))

        self.bot_active = False

        self._cache_dir = "./cache"

    async def setup_hook(self):
        await self.add_cog(LuminaCog(self))

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
                await self.client.init_thread()
                await message.channel.send("```You have now entered a converation session with Lumina. Type `!quit` to quit.```\n")
            except Exception as e:
                print(e, file=sys.stderr)
                await message.channel.send("```Something went wrong```")

        if self.bot_active:
            try:
                async with message.channel.typing():
                    await self.client.add_message(f"<{message.author.display_name}> " + message.content)
                    response = await self.client.respond()
                    await message.channel.send(response)
                    print(f"\nLUMINA: {response}")
            except Exception as e:
                print(e, file=sys.stderr)
                await message.channel.send("```Something went wrong```")

        await self.process_commands(message)

    async def _play(self):
        voice_client = discord.utils.get(self.voice_clients, guild=self.guilds[0])
        if not voice_client:
            return
        src = discord.FFmpegPCMAudio(os.path.join(self._cache_dir, "_current_audio.opus"))
        voice_client.play(src, after=lambda e: print(f"Player error: {e}") if e else None)
