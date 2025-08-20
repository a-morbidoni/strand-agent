import os
from strands import Agent
from strands_tools import file_read, file_write
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Option 1: Using OpenAI (requires OPENAI_API_KEY environment variable)
model = OpenAIModel(
    client_args={
        "api_key": os.getenv("OPENAI_API_KEY"),
        # opcional: para servidor compatible con OpenAI
        # "base_url": "<URL_CUSTOM>"
    },
    model_id="gpt-4o",  # o cualquier otro modelo que quieras usar
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

agent = Agent(
    tools=[file_read, file_write],
    model=model,
)

# Ask the agent a question
message = """
leer el archivo 'read.txt' ubicado en la carpeta 'docs' y escribir en el archivo read-2.txt una continuacion del texto aleatoria ubicado en la carpeta 'docs'
"""

response = agent(message)

print(response)
