# Mistral AI API Key Setup

Mistral AI API Key allows you to have FREE access to [selected open source LLMs](https://docs.mistral.ai/getting-started/models/models_overview/).

At the time of writing, Mistral AI offers API keys for both FREE and paid tier users.

Even FREE tier users can use Mistral Large models

![mistral_large](https://github.com/user-attachments/assets/8f262ec0-511d-461f-a094-e634f3004fc1)

# Generate Mistral API Key

![api_setup](https://github.com/user-attachments/assets/a93d6875-dbe8-44d6-84d4-6f924e6d54aa)

1. Go to https://console.mistral.ai/api-keys/

2. Log in with a registered account (Note that each free plan requires a phone number to verify.)

3. Click menu item "API Keys" on the left

4. Click button "Create new Key"

5. Enter a name, for example, "toolmate"

6. Copy or make a note of the created API key

# Switch Backend to Mistral AI

![mistral1](https://github.com/user-attachments/assets/55180829-e3c9-411f-82cd-62a56469fa0f)

![mistral2](https://github.com/user-attachments/assets/42d699e4-f4cb-4642-930d-57866752d65d)

![mistral3](https://github.com/user-attachments/assets/a62fa6e3-06f2-46dd-afe3-0d9dc72ddbe6)

1. Enter `.model` in ToolMate AI prompt or select `change AI backends and models` via action menu.

2. Select `Mistral AI API` as the AI platform.

3. Follow through the dialogs instructions to complete the model selection.

# Set Up Mistral API Key in ToolMate AI

![mistralapi1](https://github.com/user-attachments/assets/092a051f-d813-4975-bff8-454919c99840)

1. Enter ".apikeys" in ToolMate AI prompt or select `change API keys` via action menu.

2. Follow the prompts and enter your Mistral API key(s)

# Support Mulitple Mistral API Keys

![mistralapi2](https://github.com/user-attachments/assets/7bf3612d-625f-40ce-996c-db24f3d43b55)

ToolMate AI supports use of multiple Mistral AI API keys.  API keys take turns for running inference.

To use a single Mistral AI API key, simply enter your key.

To use multiple Mistral AI API keys, following the following format in your entry, e.g.

```
["mistral_api_key_1", "mistral_api_key_2", "mistral_api_key_3"]
```

# Remarks:

Tools `mistral` and `@examine_images_pixtral` work only if you enter valid Mistral AI API key(s)

# Related Wiki Page

[Groq API Key Setup](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Groq%20API%20Setup.md)