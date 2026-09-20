# Sample questions and expected response behaviour

## RAG-only destination question
Question: What are the must-visit attractions in Singapore?

Expected behaviour:
- Uses the Singapore knowledge base.
- Retrieves attractions and neighbourhood notes.
- Returns grounded recommendations such as Marina Bay, Gardens by the Bay, Chinatown, Little India, Kampong Glam, Sentosa, Mandai and Botanic Gardens.
- Shows source titles.

## MCP-only weather question
Question: What is the weather in Singapore for the next three days?

Expected behaviour:
- Selects MCP weather tool.
- Calls the weather server.
- Shows current/forecast data and clearly indicates that it came from an MCP tool.

## MCP-only currency question
Question: Convert INR 60000 to SGD.

Expected behaviour:
- Selects MCP currency tool.
- Calls the currency server.
- Returns converted amount, rate/date if available, and clearly indicates that currency came from an MCP tool.

## Combined RAG + MCP question
Question: Create a three-day Singapore itinerary for next week and adjust it according to the weather forecast.

Expected behaviour:
- Uses RAG for attractions, indoor/outdoor choices, transport and itinerary knowledge.
- Uses MCP weather for current forecast.
- Produces a day-wise weather-aware itinerary with indoor alternatives.
- Distinguishes knowledge-base facts, MCP current information and generated recommendations.

## Multi-turn context
Turn 1: I am travelling with children.
Turn 2: Plan a three-day Singapore trip and consider rain.

Expected behaviour:
- Retains family preference.
- Suggests child-friendly options and indoor alternatives when weather suggests rain.
