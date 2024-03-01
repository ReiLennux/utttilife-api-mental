import os
import time
#from dotenv import load_dotenv
from openai import OpenAI
client = OpenAI()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
from rich.console import Console
console = Console()

# Load environment variables from .env
#load_dotenv()

# Existing file and assistant information
# Get file and assistant IDs from environment variables

assistant_id = os.getenv('OPENAI_ASSISTANT_ID')

# Create a list to hold file IDs
file_ids = []

# Load multiple file IDs from environment variables
for i in range(10):  # Assuming you have 10 files
    file_id = os.getenv(f'OPENAI_FILE{i}_ID')
    if file_id:
        file_ids.append(file_id)

# Create a new thread
my_thread = client.beta.threads.create()

# Loop until the user enters "quit"
while True:
    # Get user input
    user_input = input("User: ")

    # Check if the user wants to quit
    if user_input.lower() == "quit":
        console.print("\nAssistant: Conversacion Finalizada! :wave:", style="black on white")
        break

    # Add user message to the thread
    my_thread_message = client.beta.threads.messages.create(
        thread_id=my_thread.id,
        role="user",
        content=user_input,
        file_ids=file_ids
    )

    # Run the assistant
    my_run = client.beta.threads.runs.create(
        thread_id=my_thread.id,
        assistant_id=assistant_id,
        instructions="Por favor, ayuda al usuario como un psicologo en base a la informacion verificada de los archivos que te he subido."
    )

    # Initial delay before the first retrieval
    time.sleep(10)

    # Periodically retrieve the run to check its status
    while my_run.status in ["queued", "in_progress"]:
        keep_retrieving_run = client.beta.threads.runs.retrieve(
            thread_id=my_thread.id,
            run_id=my_run.id
        )

        if keep_retrieving_run.status == "completed":
            # Retrieve the messages added by the assistant to the thread
            all_messages = client.beta.threads.messages.list(
                thread_id=my_thread.id
            )

            # Display assistant message
            console.print(f"\nAssistant: {all_messages.data[0].content[0].text.value}\n", style="black on white")

            break
        elif keep_retrieving_run.status in ["queued", "in_progress"]:
            # Delay before the next retrieval attempt
            time.sleep(5)
            pass
        else:
            break