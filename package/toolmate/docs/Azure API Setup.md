Deploy to selected resource

A Free Github API Key allows you to use OpenAI models, like gpt-4o

![azureinfo](https://github.com/user-attachments/assets/d27c8baa-a609-4cc0-ad08-484300b3d2fa)

1. Go to https://github.com/ > Signup
2. Go to https://github.com/marketplace/models/azure-openai/gpt-4o or https://github.com/marketplace/models/catalog and select gpt-4o
3. Get API Key > Get production key
4. Sign up and sign in Azure account
6. Select `Deploy to selected resource`
7. Locate the newly created resource under `All resources`
8. Select Azure Open AI
9. Copy one of the `API keys` and `inference endpoint` store it in a secure place

Optional - Change Tokens per Minute Rate Limit

1. Under the newly created resource, select the newly depolyed model > `Edit`
2. Adjust "Tokens per Minute Rate Limit"
3. Click `Save and close`

![Tokens_per_minute_rate_limit](https://github.com/user-attachments/assets/71fa9a47-1963-47fc-bc00-520e6000dcab)

Optional - Add custom model names to the model selection list in ToolMate AI

The Azure model selection' in ToolMate interface can be configured by changing the value of `azureOpenAIModels` manually in `config.py`. Its default value is `["gpt-4o", "gpt-4o-mini"]`. You may change it to, for example, `["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4o-realtime-preview"]`.  Make sure you have the configured names match the deployed model names in your Azure resources.

Alternately, 

1. Run `tmsetup -ec`
2. Locate the item `azureOpenAIModels` and change its value

# Setup in ToolMate AI

Setup AI backend either in interactive mode:

> toolmate

or via CLI option:

> tmsetup -m

> Select "Azure" as the backend

> Enter your Azure API key

> Enter your Azure inference endpoint

> select an OpenAI model

![azure1](https://github.com/user-attachments/assets/da0604bc-c876-47ac-bfc0-4a2ff0c4889f)

![azure2](https://github.com/user-attachments/assets/032dd16d-2492-429c-96f4-6850b1b7eeb8)

![azure3](https://github.com/user-attachments/assets/c202d160-396f-44c5-beea-7570ae960560)

# Links

https://github.com/marketplace

https://ai.azure.com/github

https://portal.azure.com/

https://learn.microsoft.com/en-us/azure/ai-services/openai/reference