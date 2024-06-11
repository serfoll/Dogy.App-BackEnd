import asyncio
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI, AsyncAssistantEventHandler
from typing_extensions import override

# Load environment variables
load_dotenv()

dogy_id = os.getenv("DOGY_COMPANION_ID")
openai_key = os.getenv("OPENAI_API_KEY")

# Define an event handler class
class EventHandler(AsyncAssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.responses = []

    @override
    async def on_text_created(self, text) -> None:
        print(f"\nassistant > {text.value}", end="", flush=True)
        self.responses.append(text.value)

    @override
    async def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)
        self.responses.append(delta.value)

    async def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    async def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
                self.responses.append(delta.code_interpreter.input)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)
                        self.responses.append(output.logs)

# Function to interact with OpenAI API
async def ask_dogy(user_message: str, user_name: str) -> str:
    client = AsyncOpenAI(api_key=openai_key)
    dogy = await client.beta.assistants.retrieve(assistant_id=dogy_id)
    thread = await client.beta.threads.create()

    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=f'{user_message}. Address me as {user_name}'
    )

    event_handler = EventHandler()

    async with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=dogy.id,
        event_handler=event_handler,
    ) as stream:
        await stream.until_done()

    # Skip the first response (assuming it's the duplicate "Hi")
    return "".join([str(response) for response in event_handler.responses[1:]])

# Main function to run the ask_dogy function
if __name__ == "__main__":
    response = asyncio.run(ask_dogy("Hello, how are you?", "John"))
    print(response)
