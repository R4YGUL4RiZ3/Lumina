import os
from dotenv import load_dotenv
import random
import discord
from discord.ext import commands
from openai import OpenAI

class LuminaBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.create(
            name="Lumina",
            description="",
            model="gpt-4-turbo-preview",
            tools=[{"type": "code_interpreter"}]
        )

    async def on_ready(self):
        print(f"{self.user} has connected to Discord!")

    async def on_message(self, message: discord.Message):
        print(message.content)
        if message.author == self.user:
            return
        
        if self.user in message.mentions:
            print(f"Mentions: {message.mentions}")

            thread = await self._create_thread(message.content)
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant.id
            )

            await message.channel.send(f"{message.author.mention}\n" + ...)

        if message.content.startswith('!'):
            if message.content[1:] == "roll":
                print("rolling...")
                random_number = str(random.randint(1, 6))
                await message.channel.send(random_number)

        await self.process_commands(message)

    async def _create_thread(self, message: str):
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ]
        )
        return thread

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True

    lumina = LuminaBot(command_prefix=commands.when_mentioned_or('/'), intents=intents)
    
    lumina.run(TOKEN)
