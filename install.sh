python --version

python -m venv langchain_env
bash ./langchain_env/Scripts/activate

pip install langchain openai
pip install --upgrade langchain
pip install langchain_community
pip install -U langchain-openai
pip install python-dotenv
pip install modelcontextprotocol anyio click
pip install "mcp[cli]"
pip show mcp

SCRIPT="main.py"
cat <<EOL > $SCRIPT
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
EOL
chmod +x $SCRIPT

python $SCRIPT