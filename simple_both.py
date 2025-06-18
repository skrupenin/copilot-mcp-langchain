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

openai =  OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

azure = AzureChatOpenAI(
    azure_deployment = os.getenv("AZURE_OPENAI_API_DEPLOYMENT"),
    api_version      = os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key          = os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT"),
    max_tokens       = 1000,
    temperature      = 0,
    verbose          = False,
    seed             = 1234
)

print("-----------------------------------------------------------")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
if LLM_PROVIDER not in ["openai", "azure"]:
    print("Invalid input. Please enter 'openai' or 'azure'.")
    sys.exit(1)
if LLM_PROVIDER == "openai":
    print("Using OpenAI as the LLM provider.")
    llm = openai
elif LLM_PROVIDER == "azure":
    print("Using Azure OpenAI as the LLM provider.")
    llm = azure    

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