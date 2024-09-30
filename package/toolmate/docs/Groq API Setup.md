# Groq Cloud API Key

Groq Cloud API Key allows you to have FREE access to [selected open source LLMs](https://console.groq.com/docs/models).

At the time of writing, use of Groq Cloud API is FREE.

# Generate Groq API Key

1. Go to https://console.groq.com/keys

2. Log in with a registered account

3. Click menu item "API Keys" on the left

4. Click button "Create API Key"

5. Enter a name, for example, "toolmate"

6. Copy or make a note of the created API key

![groq_api_key](https://github.com/eliranwong/toolmate/assets/25262722/d479ad5f-40b5-4d9b-a766-83db023ead1c)

# Set Up Groq API Key in ToolMate AI

1. Enter ".apikeys" in ToolMate AI prompt

2. Follow the dialog and enter your Groq API key(s)

# Support Mulitple Groq API Keys

ToolMate AI supports use of multiple groq API keys.  API keys take turns for running inference.

To use multiple groq API keys, when you prompts entering Groq API key, enter a list of groq API keys, instead of a single key, e.g.

```
["groq_api_key_1", "groq_api_key_2", "groq_api_key_3"]
```