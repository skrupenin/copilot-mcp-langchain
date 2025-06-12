from langchain.llms import OpenAI

OPENAI_API_KEY = "***REMOVED***"
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

prompt = "Привет, как ты себя чувствуешь сегодня?"

response = llm(prompt)
print(response)