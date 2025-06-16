# lblod-MCP
This repo contains the code to query Flanders' Centrale Vindplaats SPARQL endpoint using MCP.

## Set-up
### Install uv
MacOS/Linux:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows:
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
### LLM API Key (Anthropic for now)
Create a .env folder in the [lblod-mcp-client](/lblod-mcp-client) folder containing your Anthropic API Key as follows:
```
ANTHROPIC_API_KEY="sk-ant-SECRET_PART"
```

## Execution
Open two terminals, and run one of the following two commands in each terminal.

Terminal 1:
```
uv --directory /ABSOLUTE/PATH/TO/lblod-mcp-server/FOLDER/ run server.py
```
Terminal 2:
```
uv --directory /ABSOLUTE/PATH/TO/lblod-mcp-client/FOLDER/ run client.py /ABSOLUTE/PATH/TO/lblod-mcp-server/FOLDER/server.py
```
In terminal 2, the chat application will then start, allowing you to query the Centrale Vindplaats SPARQL endpoint with the implemented functionalities.

