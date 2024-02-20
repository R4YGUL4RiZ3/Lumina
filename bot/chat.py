from openai import OpenAI
import discord
from discord.ext import commands

class Chat:
    def __init__(self, bot: commands.Bot, instructions: str, api_key: str = None):
        self.client = OpenAI(api_key=api_key)

        self.guild_metadata_file = self.client.files.create(
            file=open("./cache/guild_metadata.json", "rb"),
            purpose="assistants"
        )

        self.assistant = self.client.beta.assistants.create(
            name="Lumina",
            instructions=instructions,
            model="gpt-3.5-turbo-0125",
            tools=[{"type": "code_interpreter"}],
            file_ids=[self.guild_metadata_file.id]
        )

    async def init_thread(self):
        self.bot_active = True
        self._thread = self.client.beta.threads.create()

    async def add_message(self, message: discord.Message):
        self._oapi_msg = self.client.beta.threads.messages.create(
            thread_id=self._thread.id,
            role="user",
            content=f"<{message.author.display_name}>\t" + message.content
        )
        
        self._run = self.client.beta.threads.runs.create(
            thread_id=self._thread.id,
            assistant_id=self.assistant.id
        )

    async def respond(self, message: discord.Message):
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

    async def cleanup(self):
        self.client.beta.threads.delete(self._thread.id)
        del self.chat._thread, self._run, self._oapi_msg
