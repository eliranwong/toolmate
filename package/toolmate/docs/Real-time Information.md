# Real-time Information

LLMs have limitations in their knowledge base, which is current only up to the point when they were trained. ToolMate AI offers the following tools to extend LLMs' abilities and obtain the most up-to-date information from the internet:

`@search_google` Search Google for real-time information or latest updates when LLM lacks information (Requirements: 'keywords')

`@search_searxng` Perform online searches to obtain the latest and most up-to-date, real-time information (Requirements: 'query')

`@ask_internet` an alias to `@search_searxng`

`@search_tavily` Search for online information with Tavily (Requirements: 'query')

`@ask_tavily` Get a direct and short answer from internet via Tavily (Requirements: 'query')

`@datetimes` Get information about dates and times (Requirements: 'code')

`@search_weather_info` Answer a query about weather (Requirements: 'code')

`@search_finance` Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request (Requirements: 'code')

# Comparison

For general searches, `@search_searxng` / `@ask_internet` offers better results than `@search_tavily` and `@search_google`.

# Additional Setup

For `@search_searxng` / `@ask_internet` setup, read:

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Perplexica%20and%20SearXNG%20Integration.md#searxng-setup

For `@search_tavily` and `@ask_tavily` setup, read:

https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Tavily%20API%20Setup.md