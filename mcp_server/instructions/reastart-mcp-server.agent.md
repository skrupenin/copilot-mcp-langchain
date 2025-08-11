- To restart the MCP server, you can use the following command:
  + on Windows: `Get-Process python* | Where-Object { $_.ProcessName -like "*python*" } | Stop-Process -Force`
  + on Linux: `pkill -f python`
- Then just call any MCP tool - server will start automatically.