import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI 
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_DEPLOYMENT=os.getenv("AZURE_OPENAI_API_DEPLOYMENT")

llm = AzureChatOpenAI(
    azure_deployment = AZURE_OPENAI_API_DEPLOYMENT,
    model            = AZURE_OPENAI_API_VERSION,
    api_version      = AZURE_OPENAI_API_VERSION,
    api_key          = AZURE_OPENAI_API_KEY,
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