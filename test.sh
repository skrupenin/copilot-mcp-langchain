# then ask for API keys and update .env file
# we need to set LLM_PROVIDER
# and either
# AZURE_OPENAI_API_KEY
# AZURE_OPENAI_ENDPOINT
# or 
# OPENAI_API_KEY

####################################
### activate virtual environment ###
####################################
. ./.virtualenv/Scripts/activate

############################################################
### to check connection to the OpenAI/Azure LLM provider ###
############################################################
python simple_openai.py 
python simple_azure.py 
python simple_both.py 

##########################################
### to test MCP server with MCP client ###
##########################################
python mcp_client.py

##########################
### lng_get_tools_info ###
##########################
# it returns all available MCP tools and their descriptions
python -c "import asyncio
from mcp_server.tools.lng_get_tools_info.tool import run_tool
result = asyncio.run(run_tool('lng_get_tools_info', {}))
print(result)"

#######################
### lng_count_words ###
#######################
# it counts words in the input text
# sample of how to run python function
python -c "import asyncio
from mcp_server.tools.lng_count_words.tool import run_tool
result = asyncio.run(run_tool('lng_count_words', {'input_text': 'Hello pirate!'}))
print(result)"

#####################
### lng_run_chain ###
#####################
# it runs a simple chain with the input text
# sample of how to run several python functions with langchain
python -c "import asyncio
from mcp_server.tools.lng_run_chain.tool import run_tool
result = asyncio.run(run_tool('lng_run_chain', {'input_text': 'Hello pirate!'}))
print(result)"

######################
### lng_agent_demo ###
######################
# it runs a simple agent demo with the input text
# sample of how to run several python functions with langchain in Agent mode
python -c "import asyncio
from mcp_server.tools.lng_agent_demo.tool import run_tool
result = asyncio.run(run_tool('lng_agent_demo', {'input_text': 'Hello pirate!', 'task': 'Reverse this text and then capitalize it'}))
print(result)"

#############################
### lng_structured_output ###
#############################
# it formats the output in different formats
# possible output formats: json, xml, csv, yaml, pydantic

# json
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'json'}))
print(result)"

# xml
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'xml'}))
print(result)"

# csv
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'csv'}))
print(result)"

# yaml
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'yaml'}))
print(result)"

# pydantic
python -c "import asyncio
from mcp_server.tools.lng_structured_output.tool import run_tool
result = asyncio.run(run_tool('lng_structured_output', {'question': 'Tell me more about Matrix', 'output_format': 'pydantic'}))
print(result)"

############################
### lng_chain_of_thought ###
############################
# it runs a chain of thought with memory
# it allows to ask several questions in a row and remember the context
# demonstration of technique
python -c "import asyncio
from mcp_server.tools.lng_chain_of_thought.tool import run_tool
async def test_cot_with_memory():
    # First request - starts a new session
    result1 = await run_tool('lng_chain_of_thought', {
        'question': 'If John has 5 apples and he gives 2 to Mary, how many apples does John have left?',
        'session_id': 'apple_problem',
        'new_session': True
    })
    print('First question result:')
    print(result1)
    
    # Second request - continues the session
    result2 = await run_tool('lng_chain_of_thought', {
        'question': 'If John then buys 3 more apples, how many does he have now?',
        'session_id': 'apple_problem'
    })
    print('Second question with memory:')
    print(result2)
asyncio.run(test_cot_with_memory())"

############################################################
### lng_save_prompt_template ### lng_use_prompt_template ###
############################################################
# demonstration of prompting with templates technique
# it allows to save a prompt template and then use it with different parameters
# lng_prompt_template_save - saves a template
# lng_prompt_template_use - uses a saved template with parameters
python -c "import asyncio
from mcp_server.tools.lng_prompt_template.save.tool import run_tool as save_tool
from mcp_server.tools.lng_prompt_template.use.tool import run_tool as use_tool
async def test_tools():
    save_result = await save_tool('lng_prompt_template_save', {'template': 'Tell me about {topic} in the style of {style}.'})
    print('Save template result:', save_result)   
    use_result = await use_tool('lng_prompt_template_use', {'topic': 'artificial intelligence', 'style': 'a pirate'})
    print('Use template result:', use_result)
asyncio.run(test_tools())"

###########################################
### lng_rag_add_data ### lng_rag_search ###
###########################################
# it adds data to the RAG system and then searches for it
# demonstration of RAG tools
python -c "import asyncio
from mcp_server.tools.lng_rag.add_data.tool import run_tool as add_data_tool
from mcp_server.tools.lng_rag.search.tool import run_tool as search_tool
async def test_rag_tools():
    add_result = await add_data_tool('lng_rag_add_data', {'input_text': 'Hello pirate!'})
    print('Add data result:', add_result)
    search_result = await search_tool('lng_rag_search', {'query': 'Pirate'})
    print('Search result:', search_result)
asyncio.run(test_rag_tools())"

#################################################
### WinAPI tools testing (Windows automation) ###
#################################################

#################################
### lng_winapi_list_processes ###
#################################
# try to find processes with windows
python -c "import asyncio
from mcp_server.tools.lng_winapi.list_processes.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_list_processes', {'filter': 'chrome', 'only_with_windows': True}))
print(result[0].text)"

##############################
### lng_winapi_window_tree ###
##############################
# show window element tree structure
python -c "import asyncio
from mcp_server.tools.lng_winapi.window_tree.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_window_tree', {'pid': 18672}))
print(result[0].text)"

#####################################
### lng_winapi_get_window_content ###
#####################################
# deep analysis of window content (structure mode)
python -c "import asyncio
from mcp_server.tools.lng_winapi.get_window_content.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_get_window_content', {'pid': 18672, 'mode': 'structure', 'max_depth': 3}))
print(result[0].text)"

# text extraction mode
python -c "import asyncio
from mcp_server.tools.lng_winapi.get_window_content.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_get_window_content', {'pid': 18672, 'mode': 'text_only', 'max_depth': 2}))
print(result[0].text)"

# interactive elements only
python -c "import asyncio
from mcp_server.tools.lng_winapi.get_window_content.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_get_window_content', {'pid': 18672, 'mode': 'interactive', 'max_depth': 4}))
print(result[0].text)"

# full analysis with specific element types
python -c "import asyncio
from mcp_server.tools.lng_winapi.get_window_content.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_get_window_content', {'pid': 18672, 'mode': 'full', 'element_types': ['Button', 'Edit', 'Text'], 'max_depth': 2}))
print(result[0].text)"

##############################
### lng_winapi_send_hotkey ###
##############################
# single hotkey (Ctrl+T for new tab)
python -c "import asyncio
from mcp_server.tools.lng_winapi.send_hotkey.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_send_hotkey', {'pid': 18672, 'hotkey': '^t'}))
print(result[0].text)"

# system key (F12 for DevTools)
python -c "import asyncio
from mcp_server.tools.lng_winapi.send_hotkey.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_send_hotkey', {'pid': 18672, 'key': 'F12'}))
print(result[0].text)"

# text input
python -c "import asyncio
from mcp_server.tools.lng_winapi.send_hotkey.tool import run_tool
result = asyncio.run(run_tool('lng_winapi_send_hotkey', {'pid': 18672, 'text': 'Hello Windows Automation!'}))
print(result[0].text)"

# complex sequence (open DevTools, navigate to Console, run JavaScript)
python -c @"
import asyncio
from mcp_server.tools.lng_winapi.send_hotkey.tool import run_tool

async def test_complex_sequence():
    sequence = [
        {'type': 'hotkey', 'value': '^+i'},
        {'type': 'delay', 'value': 1000},
        {'type': 'key', 'value': 'F12'},
        {'type': 'delay', 'value': 500},
        {'type': 'text', 'value': 'console.log(\"Hello from automation!\");'},
        {'type': 'key', 'value': 'ENTER'}
    ]
    result = await run_tool('lng_winapi_send_hotkey', {'pid': 18672, 'sequence': sequence, 'delay': 200})
    print('Complex sequence result:', result[0].text)

asyncio.run(test_complex_sequence())
"@

########################
### clean all caches ###
########################
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force