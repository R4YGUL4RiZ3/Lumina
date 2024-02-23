from typing import List, Literal, Any
from openai import OpenAI
import discord
from discord.ext import commands

ModelTypes = Literal["gpt-4-0125-preview", "gpt-4-1106-preview", "gpt-4", "gpt-4-32k", "gpt-3.5-turbo-0125", 'gpt-3.5-turbo-instruct']

class Client:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key)
    
    def setup(self, model: ModelTypes, instructions: str, files: List[Any] = None):
        self.assistant = self.client.beta.assistants.create(
            name="Lumina",
            instructions=instructions,
            model=model,
            tools=[{"type": "code_interpreter"}],
            file_ids=[file.id for file in files]
        )

    async def init_thread(self):
        self._thread = self.client.beta.threads.create()
        print("called init_thread")

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
    
    async def transcribe(self, )

    async def speak(self, input: str, output_file: str):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=input
        )
        response.stream_to_file(output_file)
    
    async def create_file(self, src_file: str):
        file = self.client.files.create(
            file=open(src_file, "rb"),
            purpose="assistants"
        )
        return file
    
    async def cleanup(self):
        self.client.beta.threads.delete(self._thread.id)
        del self._thread, self._run, self._oapi_msg

    async def cancel_run(self):
        self._run = self.client.beta.threads.runs.cancel(
            thread_id=self._thread.id,
            run_id=self._run.id
        )
