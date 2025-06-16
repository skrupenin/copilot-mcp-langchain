import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI 
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
     raise ValueError("OPENAI_API_KEY not found in .env")
openai = OpenAI(openai_api_key=OPENAI_API_KEY)

AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_DEPLOYMENT=os.getenv("AZURE_OPENAI_API_DEPLOYMENT")
if AZURE_OPENAI_API_KEY is None or \
   AZURE_OPENAI_API_VERSION is None or \
   AZURE_OPENAI_ENDPOINT is None or \
   AZURE_OPENAI_API_DEPLOYMENT is None:
    raise ValueError("One or more Azure OpenAI environment variables not found in .env")

azure = AzureChatOpenAI(
    azure_deployment = AZURE_OPENAI_API_DEPLOYMENT,
    model            = AZURE_OPENAI_API_VERSION,
    api_version      = AZURE_OPENAI_API_VERSION,
    api_key          = AZURE_OPENAI_API_KEY,
    max_tokens       = 1000,
    temperature      = 0,
    verbose          = False,
    seed             = 1234
)

answer = input("OpenAI or Azure? (o/a): ").strip().lower()
if answer == 'o':
    llm = openai
elif answer == 'a':
    llm = azure
else:
    print("Invalid input. Please enter 'o' for OpenAI or 'a' for Azure.")
    sys.exit(1)

template = """
"Tell me about {topic} in the style of {style}."
"""
prompt_template = PromptTemplate(
    input_variables=["topic", "style"],  
    template=template
)

topic = "artificial intelligence"
style = "a pirate"
prompt = prompt_template.format(topic=topic, style=style)
print("-----------------------------------------------------------")
print(prompt)

response = llm.invoke(prompt)

print("-----------------------------------------------------------")
print(response)
print("-----------------------------------------------------------")