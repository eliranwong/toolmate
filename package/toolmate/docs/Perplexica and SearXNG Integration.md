# Perplexica and SearXNG Integration

Perplexica and SearXNG are both helpful for researching latest information.

# Install SearXNG and Perplexica

Installing Perplexica comes with installation of SearXNG.

```
cd ~/toolmate
git clone https://github.com/ItzCrazyKns/Perplexica
cd Perplexica
cp sample.config.toml config.toml
docker compose up -d
```

To install on Android, read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Docker%20Setup%20on%20Android%20Termux.md

# Perplexica Setup

Tool `@ask_perplexica` is bult to integrate Perplexica capabilities with other ToolMate AI tools.  Simply ask a question following `@ask_perplexica` like the screenshot below.  You can make it more powerful, by [using it together with other tools in a ToolMate AI workflow](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Running%20Multiple%20Tools%20in%20One%20Go.md).

![ask_perplexica](https://github.com/user-attachments/assets/95e60cfc-5649-42ae-afe1-665d9211ddc2)

In addition, users can quickly launch Perplexica web interface via ToolMate AI system tray.

<img width="313" alt="Perplexica" src="https://github.com/eliranwong/toolmate/assets/25262722/bb1651f4-0321-4f9a-9e4a-c2f113021736">

ToolMate automatically set up Perplexica for Linux users, if your device have `docker` installed.

Windows / macOS users need to set up manually. Read: https://github.com/ItzCrazyKns/Perplexica

Default location of Perplexica is set to: ~/toolmate/Perplexica

You can customise Perplexica location by modifying item 'perplexica_directory' in config.py.

# SearXNG Setup

SearXNG is a free internet metasearch engine which aggregates results from various search services and databases. Users are neither tracked nor profiled.

Setting up Perplexica installs SearXNG automatically.  If you want to install a standalone SearXNG, read https://github.com/searxng/searxng#setup.

ToolMate AI plugin `search searxng` retrieve information from online searches via SearXNG server, to resolve your quries.

For example, you may ask something like:

> @search_searxng What is the current time in Hong Kong?

`@ask_internet` is an alias to `@search_searxng`, therefore, it is the same as above to ask like:

> @ask_internet What is the current time in Hong Kong?

The plugins assumes SearXNG is installed with Perplexica locally, with the following configurations:

searx_server = "localhost"
searx_port = 4000

You may customise these two values by manually editing the file `config.py`.

## Specify Categories for Searches

You may specify categories for your searches: `!general` `!translate` `!web` `!wikimedia` `!images` `!web` `!videos` `!web` `!news` `!web` `!wikimedia` `!map` `!music` `!lyrics` `!radio` `!it` `!packages` `!q&a` `!repos` `!software_wikis` `!science` `!scientific_publications` `!wikimedia` `!files` `!apps` `!social_media`

These categories are loaded for input suggestions when you enter `@search_searxng ` or `@ask_internet `.

For example:

> @ask_internet !news London today

Read supported categories at: https://docs.searxng.org/user/configured_engines.html

# Direct Google Search

If you don't want to set up SearXNG, you can still use tool `@search_google` to search for online information.  However, `@search_searxng` often gives better results in our testings.