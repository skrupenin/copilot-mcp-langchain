import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env")
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

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