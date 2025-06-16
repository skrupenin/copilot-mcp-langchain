from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI 
from mcp_server.config import LLM_PROVIDER, OPENAI_API_KEY, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_DEPLOYMENT

if LLM_PROVIDER == "openai":
    print("Using OpenAI LLM.")
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
else:
    print(f"Using Azure OpenAI LLM: {AZURE_OPENAI_API_DEPLOYMENT} at {AZURE_OPENAI_ENDPOINT} with API version {AZURE_OPENAI_API_VERSION}.")
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