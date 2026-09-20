
````markdown
# AI Travel Planning Assistant

This project is a Singapore travel assistant built for the Data Science, AI, Machine Learning and MLOps assignment.

The app answers travel questions using two sources:

1. A small Singapore travel knowledge base for stable destination information.
2. MCP tools for current information such as weather and currency conversion.

The main goal is to show how RAG and MCP can work together in one application.

## Links

GitHub Repository:

```text
<add your public GitHub repo link here>
````

Demo Video:

```text
<add your demo video link here>
```

## What the app can do

The assistant can answer questions like:

```text
What are the must-visit attractions in Singapore?
How can a tourist travel around Singapore?
What indoor attractions can I visit?
What is the weather in Singapore for the next three days?
Convert INR 60000 to SGD.
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

For normal destination questions, it uses the local knowledge base.

For current weather, it uses the weather MCP tool.

For currency conversion, it uses the currency MCP tool.

For mixed questions, it combines RAG and MCP results in one response.

## Project structure


ai_travel_planning_assistant/
|
--- app/
|   --- main.py
|   --- rag.py
|   --- llm.py
|   --- intent.py
|   --- memory.py
|   --- mcp_client.py
|   --- prompts.py
|   --- static/
|       --- index.html
|
|-- knowledge_base/
|   -- singapore_wikivoyage.md
|   -- visit_singapore_essential_travel_info.md
|   -- visit_singapore_itineraries.md
|   -- visit_singapore_things_to_do.md
|
|-- mcp_servers/
|   -- weather_server.py
|   -- currency_server.py
|
|-- samples/
|   -- rag_question.json
|   -- weather_question.json
|   -- currency_question.json
|   -- combined_question.json
|   -- sample_responses.md
|
|-- scripts/
|   -- ingest.py
|   -- run_api.ps1
|   -- sample_requests.ps1
|   -- test_mcp.py
|
-- .env.example
-- requirements.txt
-- README.md


## Knowledge base

I prepared the Singapore knowledge base as short markdown notes instead of dumping full webpages. Each file keeps the source title and URL so that retrieved answers can show where the information came from.

Sources used:

```text
1. Wikivoyage Singapore Travel Guide
   https://en.wikivoyage.org/wiki/Singapore

2. Visit Singapore - Essential Travel Information
   https://www.visitsingapore.com/travel-tips/essential-travel-information/

3. Visit Singapore - Sample Itineraries
   https://www.visitsingapore.com/singapore-itineraries/

4. Visit Singapore - Things To Do
   https://www.visitsingapore.com/things-to-do/
```

The knowledge base covers:

```text
Attractions
Neighbourhoods
Transport guidance
Food and local experiences
Practical travel tips
Indoor activities
Outdoor activities
Sample itineraries
```

## How the application works

At a high level, the flow is:

```text
Browser UI -> FastAPI /chat endpoint ->
Intent detection -> RAG and/or MCP tools ->
Prompt generation -> LLM response ->
Answer with sources and tool results
```

The app tries to use the right source depending on the question.

Destination-related questions use RAG.

Weather-related questions use the weather MCP server.

Currency-related questions use the currency MCP server.

Questions like itinerary planning with weather use both RAG and MCP.

## RAG workflow

The RAG flow is implemented in `app/rag.py`.

Steps:

```text
1. Load markdown files from knowledge_base/
2. Preserve source title and source URL as metadata
3. Split documents into chunks
4. Generate embeddings using HuggingFace embeddings
5. Store embeddings in Chroma
6. Retrieve relevant chunks for each destination question
7. Pass retrieved context to the answer prompt
8. Return answer with source references
```

The vector store is generated locally by running:

```powershell
python -m scripts.ingest
```

## MCP tools

There are two MCP servers in this project.

### Weather MCP

File:

```text
mcp_servers/weather_server.py
```

Tool:

```text
get_weather_forecast(city, days)
```

It uses Open-Meteo APIs to get city coordinates and weather forecast.

This tool is used for questions like:

```text
What is the weather in Singapore?
What is the forecast for the next three days?
Is rain expected during my trip?
Should I plan indoor or outdoor activities tomorrow?
```

### Currency MCP

File:

```text
mcp_servers/currency_server.py
```

Tool:

```text
convert_currency(amount, from_currency, to_currency)
```

It uses the Frankfurter exchange-rate API.

This tool is used for questions like:

```text
Convert INR 60000 to SGD.
How much is 200 SGD in INR?
Convert my travel budget from USD to Singapore dollars.
```

## Context handling

The app keeps a small in-memory session context.

It stores simple user preferences such as:

```text
family travel
children
culture
food
budget
indoor activities
outdoor activities
```

This is used for follow-up questions. For example, if the user says:

```text
I am travelling with children.
```

and then asks:

```text
Adjust the previous plan.
```

the app uses the family preference in the next response.

## Prompt strategy

The prompt is kept in `app/prompts.py`.

The prompt tells the assistant to:

```text
Use knowledge-base content for Singapore destination facts.
Use MCP results for current weather or currency information.
Avoid making unsupported factual claims.
Clearly say when information is not available.
Show source references when RAG is used.
Distinguish current tool information from generated recommendations.
Use stored user preferences during follow-up questions.
```

This was added to avoid mixing static travel facts with current information.

## Setup on Windows

Open PowerShell in the project folder.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment setup

Create a `.env` file from the example file.

```powershell
copy .env.example .env
notepad .env
```

Add your Gemini key if available:

```text
GOOGLE_API_KEY=<your_key_here>
GEMINI_MODEL=gemini-3.6-flash
```

The application has a fallback response path, so basic demo flow still works without an LLM key. For better final answers, Gemini should be configured.

## Build the knowledge index

Run:

```powershell
python -m scripts.ingest
```

Expected output:

```text
Knowledge base indexed. Chunks stored: <number>
```

## Run the application

Run:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the browser:

```text
http://127.0.0.1:8000
```

API docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Test MCP tools

Run:

```powershell
python -m scripts.test_mcp
```

This checks whether the weather and currency MCP tools are working.

## Test sample requests

Keep the API running.

Open another PowerShell window:

```powershell
.\.venv\Scripts\activate
.\scripts\sample_requests.ps1
```

## Sample API request

```powershell
$body = Get-Content .\samples\combined_question.json -Raw

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Questions used for testing

RAG-only question:

```text
What are the must-visit attractions in Singapore?
```

Weather MCP question:

```text
What is the weather in Singapore for the next three days?
```

Currency MCP question:

```text
Convert INR 60000 to SGD.
```

Combined RAG and MCP question:

```text
Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.
```

Conversation context test:

```text
I am travelling with children.
```

Follow-up:

```text
Adjust the previous plan for a family with children and keep indoor options if rain is expected.
```

## Demo flow

For the demo video, I used this flow:

```text
1. Show project folder structure.
2. Explain knowledge_base files.
3. Explain RAG pipeline in app/rag.py.
4. Explain weather and currency MCP servers.
5. Explain main API flow in app/main.py.
6. Run the FastAPI application.
7. Ask one RAG-only question.
8. Ask one weather MCP question.
9. Ask one currency MCP question.
10. Ask one combined itinerary question.
11. Ask a follow-up question to show context retention.
```

## Notes

The 'vector_store/' folder is generated locally after running the ingestion script. If it is not present, run:

```powershell
python -m scripts.ingest
```

The knowledge-base markdown files are included in the project so that evaluators can run the app without crawling or downloading content separately.

## Submission checklist

Before final submission:

```text
Update GitHub repo link in this README.
Update demo video link in this README.
Create ZIP with the complete project.
Name the ZIP as Name_Empcode_AI Travel Planning Assistant.zip.
Upload the ZIP to OneDrive.
Keep OneDrive access public.
Submit the OneDrive link in the official form.
```

```
