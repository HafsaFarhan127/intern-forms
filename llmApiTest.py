from dotenv import load_dotenv
import os

#loading the env file
load_dotenv()

#checking if env var is accessed
api_key = os.getenv("GEMINI_API_KEY")

#print("API Key:", api_key)

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.(built-in if i have another api name then need to pass it in as param)
client = genai.Client() #request to llm
#sending requests to the gemini 2.0 flash model
response = client.models.generate_content(
    model="gemini-2.5-pro", contents="say meow"
    #its the same api key just change the model code.
)
print(response.text)

response2 = client.models.generate_content(
    model="gemini-2.0-flash", contents="Can you tell me your name and say response2 at the end"
)
print(response2.text)