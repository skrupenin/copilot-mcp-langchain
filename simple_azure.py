import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI 
from dotenv import load_dotenv

load_dotenv()

llm = AzureChatOpenAI(
    azure_deployment = os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
    api_version      = os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key          = os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT"),
    max_tokens       = 1000,
    temperature      = 0,
    verbose          = False,
    seed             = 1234
)

prompt = "Hello, how are you feeling today?"
print("-----------------------------------------------------------")
print(prompt)

response = llm.invoke(prompt)
print("-----------------------------------------------------------")
print(response)
print("-----------------------------------------------------------")