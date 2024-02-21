from openai import OpenAI
import discord
from discord.ext import commands

class Client:
    def __init__(self, instructions: str, model: str, api_key: str = None):
        self.client = OpenAI(api_key=api_key)

        self.guild_metadata_file = self.client.files.create(
            file=open("./cache/guild_metadata.json", "rb"),
            purpose="assistants"
        )

        self.assistant = self.client.beta.assistants.create(
            name="Lumina",
            instructions=instructions,
            model=model,
            tools=[{"type": "code_interpreter"}],
            file_ids=[self.guild_metadata_file.id]
        )

    async def init_thread(self):
        self.bot_active = True
        self._thread = self.client.beta.threads.create()

    async def add_message(self, message: str):
        self._oapi_msg = self.client.beta.threads.messages.create(
            thread_id=self._thread.id,
            role="user",
            content=message
        )
        
        self._run = self.client.beta.threads.runs.create(
            thread_id=self._thread.id,
            assistant_id=self.assistant.id
        )

    async def respond(self) -> str:
        while self._run.status != "completed":
            current_run = self.client.beta.threads.runs.retrieve(
                thread_id=self._thread.id,
                run_id=self._run.id
            )
            print(f"Thread run current status: {current_run.status}")
            
            if current_run.status == "completed":
                break
            
        response = self.client.beta.threads.messages.list(thread_id=self._thread.id)
        response_text = response.data[0].content[0].text.value

        return response_text
    
    async def cleanup(self):
        self.client.beta.threads.delete(self._thread.id)
        del self.chat._thread, self._run, self._oapi_msg
