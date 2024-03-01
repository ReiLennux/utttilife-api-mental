import os

def get_file_ids():
    return [os.getenv(f'OPENAI_FILE{i}_ID') for i in range(10) if os.getenv(f'OPENAI_FILE{i}_ID')]
