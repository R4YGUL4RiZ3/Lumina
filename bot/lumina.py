import os
import sys
import datetime
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

    @commands.command(name="roll", help="Rolls a random number between 1 and 6")
    async def roll(self, ctx: commands.Context):
        if not self.bot.bot_active:
            print("rolling...")
            random_number = str(random.randint(1, 6))
            await ctx.send(random_number)

    @commands.command(name="quit", help="Quit current chat session")
    async def quit(self, ctx: commands.Context):
        if self.bot.bot_active:
            self.bot.bot_active = False
            self.bot.client.cleanup()
            await ctx.send("\n```You have successfully exit the conversation.```")

    @commands.command(name="stop", help="Forcefully make Lumina stop")
    async def stop(self, ctx: commands.Context):
        self.bot.client.cancel_run()
        await ctx.send("> Successfully made Lumina stop")

    @commands.command(name="join_voice", help="Joins current voice chat")
    async def join_voice(self, ctx: commands.Context):
        channel = ctx.author.voice.channel
        if channel:
            await channel.connect()
        else:
            await ctx.send("You are not in a voice channel! Join one to get me to join.")
        
    @commands.command(name="leave_voice", help="Leaves current voice chat")
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
        self._cache_dir = "./cache"

        self.client = Client()
        
        self.bot_active = False

    async def setup_hook(self):
        await self.add_cog(LuminaCog(self))
        
    async def on_ready(self):
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

        history = await self._fetch_chat_history()
        with open(os.path.join(self._cache_dir, "history.json"), 'w') as f:
            json.dump(history, f, indent=4)
            
        guild_metadata = await self._fetch_guid_metadata()
        with open(os.path.join(self._cache_dir, "guild_metadata.json"), 'w') as f:
            json.dump(guild_metadata, f, indent=4)

        self.client.setup(
            model="gpt-3.5-turbo-0125",
            instructions=load_instructions("./bot/instructions.txt"),
            files=[
                await self.client.create_file(os.path.join(self._cache_dir, "guild_metadata.json")),
                await self.client.create_file(os.path.join(self._cache_dir, "history.json"))
            ]
        )

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
                await message.channel.send("> Something went wrong. Please report issue to @PyIDK")
                raise e

        if self.bot_active:
            if (len(message.mentions) > 0 and (self.user in message.mentions)) or len(message.mentions) == 0:
                try:
                    async with message.channel.typing():
                        await self.client.add_message(f"<{message.author.display_name}> " + message.content)
                        response = await self.client.respond()
                        await message.channel.send(response)
                        print(f"\nLUMINA: {response}")
                except Exception as e:
                    await message.channel.send("> Something went wrong. Please report issue to @PyIDK")
                    raise e

        await self.process_commands(message)

    async def _fetch_guid_metadata(self) -> Dict[str, Union[str, int]]:
        guild = self.guilds[0]
        guild_metadata = {
            "file_metadata": {
                "name": "guild_metadata.json"
            },
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "members": [str(member) for member in guild.members],
            "creation_date": str(guild.created_at),
        }
        return guild_metadata

    async def _fetch_chat_history(self) -> Dict[str, Dict[str, str]]:
        guild = self.guilds[0]
        history = {"_file_metadata": {"name": "history.json"}}
        for channel in guild.text_channels:
            history_current_channel = []
            async for msg in channel.history(limit=100):
                current_msg = {
                    "author": f"{msg.author.name} ({msg.author.display_name})",
                    "time": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "content": msg.content
                }
                history_current_channel.append(current_msg)
            history[channel.name] = history_current_channel
        return history

    async def _play(self):
        voice_client = discord.utils.get(self.voice_clients, guild=self.guilds[0])
        if not voice_client:
            return
        src = discord.FFmpegPCMAudio(os.path.join(self._cache_dir, "_current_audio.opus"))
        voice_client.play(src, after=lambda e: print(f"Player error: {e}") if e else None)
