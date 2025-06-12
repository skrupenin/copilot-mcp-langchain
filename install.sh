python --version

python -m venv langchain_env
bash ./langchain_env/Scripts/activate

pip install langchain openai
pip install --upgrade langchain
pip install langchain_community
pip install -U langchain-openai

SCRIPT="main.py"
cat <<EOL > $SCRIPT
from langchain.llms import OpenAI

OPENAI_API_KEY = "***REMOVED***"
llm = OpenAI(openai_api_key=OPENAI_API_KEY)

prompt = "Привет, как ты себя чувствуешь сегодня?"

response = llm(prompt)
print(response)
EOL
chmod +x $SCRIPT

python $SCRIPT