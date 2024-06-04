#dogy_companion.py
import asyncio
from dotenv import load_dotenv
import logging
from openai import AsyncOpenAI
import os
import time
from pprint import pprint

load_dotenv()

dogy_id = os.getenv("DOGY_COMPANION_ID")
openai_key = os.getenv("OPENAI_API_KEY")


async def ask_dogy(user_message: str , user_name: str):
  print(f"Asking Dogy {openai_key}")
  client = AsyncOpenAI(api_key=openai_key)
  dogy = await client.beta.assistants.retrieve(assistant_id=dogy_id)
  thread = await client.beta.threads.create()

  if user_message == "":
    user_message = "Hi, dogy!"
  if user_name == "":
     user_name = "Gio"

  message = await client.beta.threads.messages.create(
    thread_id =thread.id,
    role = 'user',
    content = user_message
  )


  run = await client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=dogy.id,
    instructions= f'Please address the user as {user_name}'
  )

  await wait_for_run_completion(client, thread.id, run.id)

  response = await client.beta.threads.messages.list(thread_id=thread.id)

  return response.data[0].content[0].text.value


async def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.
    """
    while True:
        try:
            run = await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = await client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[-1]  # Assuming you want the last message
                response = last_message.content
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        await asyncio.sleep(sleep_interval)


if __name__ == "__main__":
  pprint(asyncio.run(ask_dogy("","")))
