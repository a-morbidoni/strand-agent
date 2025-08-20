import os
from strands import Agent
from strands_tools import calculator, current_time
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
    tools=[calculator, current_time],
    model=model,
)

# Ask the agent a question
message = """
si naci el 4/12/1989, cuantos dias llevo con vida? 
"""

response = agent(message)

print(response)
