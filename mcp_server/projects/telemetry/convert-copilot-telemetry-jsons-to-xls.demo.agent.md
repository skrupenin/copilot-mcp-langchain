## Info
- These instructions are needed to demonstrate the ability to convert raw JSONs data from GitHub Copilot telemetry into a CSV file that is easy to analyze and easy to open in Excel.

## How to ask for demo in chat
Use this case to make demo:
```
Show me demo from file:
Please process all github copilot telemetry data in `work\telemetry`. 
```

## Important
- Workspace is `mcp_server/projects/telemetry/`.
- Please use `./pipeline/telemetry.json` pipeline to process all the files. 
- Don't analyze all the files that make up the essence of this transformation — just call the pipeline with `lng_batch_run` tool.
- Cleanup `./data/in/` folder.
- Copy all user's input json files into `./data/in/` folder. 
- The pipeline will generate both CSV report and Excel report using the template in `./data/out/` folder.
- Copy `./data/out/telemetry.xlsx` back to the user's input folder in `out` directory.
- Then remove all content inside `./data/in/` and `./data/out/` folders.