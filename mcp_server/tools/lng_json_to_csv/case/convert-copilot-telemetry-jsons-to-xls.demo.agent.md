## Info
- These instructions are needed to demonstrate the ability to convert raw JSONs data from GitHub Copilot telemetry into a CSV file that is easy to analyze and easy to open in Excel.

## How to ask for demo in chat
Use this case to make demo:
```
Show me demo from file:
Please process all github copilot telemetry data in `./mcp_server/tools/lng_json_to_csv/case/data`. 
```

## Important
- Please use `telemetry.json` pipeline to process all the files.
- Don't analyze all the files that make up the essence of this transformation — just call the pipeline.
- Do all the demo stuff in the `work` folder: `in` for input data, `out` for output data.
- Copy `telemetry.xlsx` template file to `work/telemetry/in/` folder along with JSON files.
- The pipeline will generate both CSV report and Excel report using the template.
- Final Excel result will be saved as `telemetry_result.xlsx` in the `out` folder.