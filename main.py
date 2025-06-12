from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

OPENAI_API_KEY = "***REMOVED***"
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

response = llm(prompt)
print(response)