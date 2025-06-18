import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

prompt = "Hello, how are you feeling today?"
print("-----------------------------------------------------------")
print(prompt)

response = llm.invoke(prompt)
print("-----------------------------------------------------------")
print(response)
print("-----------------------------------------------------------")