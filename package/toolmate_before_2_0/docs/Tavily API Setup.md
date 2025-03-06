# Tavily API Setup

Tavily's Search API is a search engine built specifically for AI agents (LLMs), delivering real-time, accurate, and factual results at speed.

# Get a Tavily API Key

Log in https://app.tavily.com/sign-in and get an API key.

# Set Up Tavily API Key in ToolMate AI

1. Enter ".apikeys" in ToolMate AI prompt

2. Follow the dialog and enter your Tavily API key(s)

# Support Mulitple Groq API Keys

ToolMate AI supports use of multiple Tavily API keys.  API keys take turns for running inference.

To use multiple Tavily API keys, when you prompts entering Tavily API key, enter a list of Tavily API keys, instead of a single key, e.g.

```
["tavily_api_key_1", "tavily_api_key_2", "tavily_api_key_3"]
```