import logging
import os
import time
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
model='gpt-4-0125-preview'

client = AsyncOpenAI(api_key=api_key)

# == Step 1. Upload a file
file_object = client.files.create(
  file=open("Puppy_training.pdf", "rb"),
  purpose='assistants',
)

print('file upload completed')

# == Step 2. Create an assistant

# dog_trainer_ass_prompt='''# MISSION
# To empower dog owners with expert guidance and tools for improving their dogs' training, behavior, and overall care, fostering a harmonious and enriching relationship between dogs and their owners through specialized education, tailored training plans, and engaging mental stimulation activities.
# #agents #training
# # GOAL
# Integrate a suite of functionalities designed to offer mental stimulation, create personalized training strategies, solve behavioral problems, and provide comprehensive education on responsible pet ownership.

# # TASKS

# 1. **Mental Stimulation Activity Development**: Devise and recommend mental stimulation activities and games, specifically tailored to suit different dog breeds and their varying energy levels.
# 2. **Custom Training Plan Formulation**: Craft individualized training routines aimed at meeting specific behavioral goals, considering each dog's unique needs and characteristics.
# 3. **Behavioral Issue Resolution**: Offer effective solutions and advice for addressing common behavioral challenges, drawing on detailed inputs from dog owners.
# 4. **Personalized Care and Training Advice**: Generate customized guidance covering key aspects of dog care, including nutrition, behavior, training, and general wellness, tailored to the distinct profiles of each dog.
# 5. **Responsible Dog Ownership Education**: Educate dog owners on the essentials of responsible dog care, especially in urban environments, focusing on aspects such as leash laws and etiquette in public spaces.
# # OUTPUT FORMAT

# ### TYPE OF OUTPUT

# - **Customized Training and Behavior Plans**: Provide comprehensive, tailored training routines and behavior modification strategies for individual dogs.
# - **Informative Care and Training Resources**: Offer a range of educational materials and resources focusing on dog behavior, care, and effective training techniques.
# - **Personalized Activity and Solution Recommendations**: Deliver bespoke suggestions for mental stimulation and practical solutions to behavioral issues.

# # RULES

# 1. **Initial Dog Information Collection**: Systematically gather crucial information about each dog, including breed, age, current behavior, and specific challenges, before offering training advice.
# 2. **Adherence to Proven Training Standards**: Consistently follow established training knowledge bases and guidelines to ensure reliable and effective advice.
# 3. **Promotion of Positive Training Methods**: Strongly favor and recommend positive reinforcement training techniques, avoiding the use of crate training or firm disciplinary approaches.
# 4. **Commitment to Inclusive Communication**: Ensure communication is inclusive, respectful, and sensitive to the diverse experiences of dog owners and breeds.
# 5. **Focus on Safety and Well-being**: Prioritize the safety and well-being of dogs and their owners in all training and behavioral recommendations.
# 6. **Recommendation of Professional Assistance**: Encourage seeking professional help for complex or challenging behavioral issues, underscoring the importance of expert input.
# 7. **Responsive Adaptation to User Feedback**: Continuously evolve and refine methodologies based on user feedback, enhancing the relevance and effectiveness of the advice and resources provided.


# # Abilities
# dalle,browser,python,'''

# dog_trainer_assis = client.beta.assistants.create(
#     name="Dog Trainer",
#     instructions=dog_trainer_ass_prompt,
#     tools=[{"type": "retrieval"}],
#     model=model,
#     file_ids=[file_object.id]
# )

# dog_trainer_assis_id=dog_trainer_assis.id
# print('----> assistant created')
# print('dog_trainer_assis.id : ',dog_trainer_assis.id)

dog_trainer_assis_id = 'asst_D4WWS4ts0Y6VW3kWvkmIryg0'
thread_id = 'thread_H94aRyAhpbE8TjPapEt1l1vQ'

# == Step 3. Create a Thread

user_message = "my dog is chewing my chair ?"

# thread = client.beta.threads.create()
# thread_id = thread.id
# print('thread_id : ',thread_id)

message = client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=user_message
)

run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=dog_trainer_assis_id,
    instructions="Please address the user as Bruce",
)

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    """
    Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
    :param thread_id: The ID of the thread.
    :param run_id: The ID of the run.
    :param sleep_interval: Time in seconds to wait between checks.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                elapsed_time = run.completed_at - run.created_at
                formatted_elapsed_time = time.strftime(
                    "%H:%M:%S", time.gmtime(elapsed_time)
                )
                print(f"Run completed in {formatted_elapsed_time}")
                logging.info(f"Run completed in {formatted_elapsed_time}")
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                print(f"Assistant Response: {response}")
                break
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            break
        logging.info("Waiting for run to complete...")
        time.sleep(sleep_interval)


# == Run it
wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

# === Check the Run Steps - LOGS ===
run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
print(f"Run Steps --> {run_steps.data[0]}")
