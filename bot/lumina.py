import os
from dotenv import load_dotenv
import random
from typing import *

import discord
from discord.ext import commands
from openai import OpenAI

from utils import *

class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(
            name="Lumina",
            instructions=load_instructions("./bot/instructions.txt"),
            model="gpt-3.5-turbo-0613",
            tools=[{"type": "code_interpreter"}]
        )
        print(load_instructions("./bot/instructions.txt"))
        self.bot_active = False

    async def on_ready(self):
        print(f"{self.user} is now online!")

    async def on_message(self, message: discord.Message):
        # Debugging
        print(f"\n{message.author}: {message.content} ({message.channel})")
        if len(message.mentions) > 0:
            print(f"\nMentions: {message.mentions}")

        if message.author == self.user:
            return
        
        if (self.user in message.mentions) or (message.guild is None):
            await self._init_thread()
            await message.channel.send("```You have now entered a converation session with Lumina. Type `!quit` to quit.```")

        if self.bot_active:
            async with message.channel.typing():
                await self._add_message(message)
                await self._respond(message)

        await self._handle_commands(message)
        await self.process_commands(message)

    async def _init_thread(self):
        self.bot_active = True
        self._thread = self.client.beta.threads.create()

    async def _add_message(self, message: discord.Message):
        self._oapi_msg = self.client.beta.threads.messages.create(
            thread_id=self._thread.id,
            role="user",
            content=message.content
        )
        
        self._run = self.client.beta.threads.runs.create(
            thread_id=self._thread.id,
            assistant_id=self.assistant.id
        )
    
    async def _respond(self, message: discord.Message):
        while self._run.status != "completed":
            current_run = self.client.beta.threads.runs.retrieve(
                thread_id=self._thread.id,
                run_id=self._run.id
            )
            print(f"Thread run current status: {current_run.status}")
            
            if current_run.status == "completed":
                break
            
        response = self.client.beta.threads.messages.list(thread_id=self._thread.id)

        await message.channel.send(response.data[0].content[0].text.value)
        print(f"\nLUMINA: {response.data[0].content[0].text.value}")

    async def _handle_commands(self, message):
        if not self.bot_active and message.content.startswith('!'):
            if message.content[1:] == "roll":
                print("rolling...")
                random_number = str(random.randint(1, 6))
                await message.channel.send(random_number)
            if self.bot.active and message.content[1:] == "quit":
                self.bot_active = False
                del self._thread, self._run, self._oapi_msg
                await message.channel.send("```You have successfully exit the conversation.```")
                print(self.bot_active)

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = True

    lumina = LuminaBot(command_prefix=commands.when_mentioned_or('/'), intents=intents)
    
    lumina.run(TOKEN)
