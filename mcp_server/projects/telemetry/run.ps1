cd ./../../../
. ./.virtualenv/Scripts/activate.ps1
python -m mcp_server.run run lng_batch_run '{\"pipeline_file\": \"mcp_server/projects/telemetry/pipeline/telemetry.json\", \"user_params\": {\"base_directory\": \"work/telemetry\"}}'