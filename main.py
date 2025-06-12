from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env")
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

template = """
Привет, {name}, как ты себя чувствуешь сегодня?
"""
prompt_template = PromptTemplate(
    input_variables=["name"],  
    template=template
)

name = "Саша"
prompt = prompt_template.format(name=name)

response = llm.invoke(prompt)
print(response)