"""
LetMeDoIt AI Plugin - search latest news

search latest news

[FUNCTION_CALL]
"""

from freegenius import config
import feedparser

# Function method to get the latest news from a specific RSS feed
def search_latest_news(function_args: dict) -> str:
    keywords = function_args.get("keywords")
    feed_url = f"https://news.google.com/rss/search?q={keywords}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)

    # Print the title and link of each news item
    config.stopSpinning()
    config.print2(config.divider)
    for index, entry in enumerate(feed.entries):
        if index < 10:
            if not index == 0:
                config.print2(config.divider)
            # title
            title = re.sub("<[^<>]*?>", "", entry.title)
            config.print3(f"Title: {title}")
            # link
            link = re.sub("<[^<>]*?>", "", entry.link)
            config.print3(f"Link: {link}")
    config.print2(config.divider)
    return ""

# Function signature to work with ChatGPT function calling
functionSignature = {
    "intent": [
        "access to internet real-time information",
    ],
    "examples": [
        "Tell me latest news about",
    ],
    "name": "search_latest_news",
    "description": "Search the latest news with given keywords",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "The keywords for searching the latest news, delimited by plus sign '+'.  For example, return 'London+UK' if keywords are 'London' and 'UK'.",
            },
        },
        "required": ["keywords"],
    },
}

# The following line integrate the function method and signature into LetMeDoIt AI
config.addFunctionCall(signature=functionSignature, method=search_latest_news)

# The following line is optional. It adds an input suggestion to LetMeDoIt AI user input prompt
config.inputSuggestions.append("Tell me the latest news about ")