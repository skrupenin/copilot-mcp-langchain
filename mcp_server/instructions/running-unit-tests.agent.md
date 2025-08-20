- Please store all unit tests in the `stuff` folder inside the folder with `tool.py`.
- Run all tests to make sure everything works correctly: 
  + `python -m pytest mcp_server/tools/{TOOL_NAME}/ --tb=no -q`
  + `python -m unittest mcp_server.tools.{TOOL_NAME}.stuff.test -v`
  + `python mcp_server/tools/{TOOL_NAME}/stuff/test.py`
  + `python -m unittest mcp_server.tools.{TOOL_NAME}.stuff.test.{TestClass}.{test_method} -v` (single test)
- Tests should contain `// given`, ``// when`, and `// then` blocks to make it clear what the test does.
- Follow the rule of no more than 1 assert per test.
- Use an approach where the assert block compares the string representation of the expected and actual results, rather than comparing objects.