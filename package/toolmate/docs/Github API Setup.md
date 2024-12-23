# Get Free Github API Key

A Free Github API Key allows you to use OpenAI models, like gpt-4o

1. Go to https://github.com/ > Signup
2. Go to https://github.com/marketplace/models/azure-openai/gpt-4o or https://github.com/marketplace/models/catalog and select gpt-4o
3. Get API Key > Get developer key > Generate new token (classic)
4. "You do not need to give any permissions to the token. Note that the token will be sent to a Microsoft service."
5. Give a note, e.g. "toolmate"
6. Generate token
7. Copy the generated token and store it in a secure place

# Setup in ToolMate AI

Setup AI backend either in interactive mode:

> toolmate

or via CLI option:

> tmsetup -m

1. Select "Github"

2. Enter your Github API key

3. Select an OpenAI model

![github01](https://github.com/user-attachments/assets/7260142c-8ed6-4e82-b367-febe81c624dc)

![github02](https://github.com/user-attachments/assets/d8ae5b2c-6a81-41f5-ad0b-d6ebfab36327)

![github03](https://github.com/user-attachments/assets/d9c4d711-7e98-488e-a33b-7cb4a27a72aa)

Remarks: You can enter either a single API key or a list of multiple API keys. For multiple key entry, follow the format: ['api_key_1', 'api_key_2', 'api_key_3']. Multiple keys take turn for generating responses.