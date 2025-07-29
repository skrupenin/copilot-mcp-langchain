- If you need to test the tool after creation or modification do the following:
```bash
python -m mcp_server.run run lng_winapi_window_tree '{\"pid\":18672}'
```
- If you need to run two or more tools together, you can run them in parallel with bathch command:
```bash
python -m mcp_server.run batch lng_llm_rag_add_data '{\"input_text\":\"Hello pirate!\"}' lng_llm_rag_search '{\"query\":\"Pirate\"}'
```
- Log file in this case will be `mcp_server/logs/mcp_runner.log`.
