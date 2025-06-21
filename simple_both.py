import sys
import os
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI 
from mcp_server.llm import llm

model = llm()

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

response = model.invoke(prompt)

print("-----------------------------------------------------------")
print(response)
print("-----------------------------------------------------------")