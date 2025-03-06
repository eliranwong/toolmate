# AutoGen Integration

[AutoGen Agents](https://ag2.ai/) are integrated in the following tools in ToolMate AI:

`@proxy` Use AutoGen assistant agent to resolve a request

`@group` Use AutoGen auto-builder agent to create a team of AI agents to resolve a request that does not require coding

`@agents` Use AutoGen auto-builder agent to create a team of AI agents to resolve a request that requires coding

`@captain` Use AutoGen captain agent and tool library to resolve a request

`@examine_files` Use AutoGen retrieve assistant agent for examining file content, if config.rag_useAutoRetriever is set to True

`@examine_web_content` Use AutoGen retrieve assistant agent for examining web content, if config.rag_useAutoRetriever is set to True

Remarks: These tools are available in the full version of ToolMate AI.  The Lite version doesn't include these tools.

## Interactive Mode

To run ToolMate AI interactive mode:

> toolmate

Simple enter the tool signature, e.g. @agents, followed by your request, in ToolMate AI interactive prompt.

## CLI Aliases

Some may find it more flexible to use [ToolMate CLI options](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/ToolMate%20API%20Server.md) that come with ToolMate API client.

To check all available options, run:

> tm -h

The following command aliases are created for quick access to AutoGen tools:

`tmproxy` essentially equal to `tm -dt proxy`

`tmgroup` essentially equal to `tm -dt group`

`tmagents` essentially equal to `tm -dt agents`

`tmcaptain` essentially equal to `tm -dt captain`

## Standalone AutoGen Utilities

ToolMate AI also offers standalone AutoGen utilities:

To use AutoGen assistant agent:

> autoassist

To use AutoGen retrieve assistant agent:

> autoretrieve

To use AutoGen auto-builder agent:

> autobuild

To use AutoGen captain agent:

> autocaptain

# AutoGen Integration Setup

Interactive propmt

> toolmate .autogen

CLI:

> tmsetup -ag

# Captain Agent Setup

AutoGen Agent requires setup of Bing search and Rapid API keys.  Free plans are available.  You may follow the steps below:

## Bing Search API Key Setup

1. Sign up at https://www.microsoft.com/en-us/bing/apis/bing-web-search-api

2. Search for "Bing search" and create a bing search resource

3. Select a pricing tier (FREE plan is available, i.e. F1, at the time of writing)

![bing0](https://github.com/user-attachments/assets/d5e4a577-c0bd-4c22-8cdb-5a0e766506c1)

![bing1](https://github.com/user-attachments/assets/e4b95e19-ddfe-40e8-9aea-00b62d5be52f)

4. Go to resource

![bing3](https://github.com/user-attachments/assets/fa50eb54-5ed6-4fb2-9a25-33348c378e31)

5. Click the link for managing keys

![bing4](https://github.com/user-attachments/assets/eb7c249a-53a1-4233-b18b-3c43b44bed10)

6. Copy one of the generated keys

![bing5](https://github.com/user-attachments/assets/7e8ca6b2-f4ba-47b1-bba5-b2ca83039013)


## Rapid API Key Setup

1. Sign up at https://rapidapi.com/auth/sign-up

2. Search "Youtube Transacript" and subscribe a plan (FREE plan is available)

3. Search "Youtube MP3 Downloader" and subscribe a plan (FREE plan is available)

Some screenshots below:

![rapidapi1](https://github.com/user-attachments/assets/a24c233b-c0df-422d-b0cf-994c3bfd7cd6)

![rapidapi2](https://github.com/user-attachments/assets/3fc6f1d7-7a4f-44ae-890e-119a6d74fde7)

![rapidapi3](https://github.com/user-attachments/assets/2354f98d-5d20-459c-af17-be9bbea4f2a1)

![rapidapi4](https://github.com/user-attachments/assets/14ee9e49-f26c-43c4-8550-fb4cef740a08)

4. Go to Billing Information https://rapidapi.com/developer/billing/billing-information and select "default-application"

5. Copy the Application Key

![rapid0](https://github.com/user-attachments/assets/35db1ba6-221b-49db-9538-32ca625108d0)
