"""
ToolMate AI Plugin - search SearXNG

Default Configurations
(assuming Perplexica is installed locally)
searx_server = "localhost"
searx_port = 4000

You can manually edit config.py to customise these settings.

[TOOL_CALL]
"""

if not config.isTermux:

    from langchain_community.utilities import SearxSearchWrapper
    from toolmate import config, isServerAlive, print1, print2, plainTextToUrl

    persistentConfigs = (
        ("searx_server", "http://localhost"),
        ("searx_port", 4000),
    )
    config.setConfig(persistentConfigs)
    if config.searx_server == "localhost":
        config.searx_server = "http://localhost"

    if isServerAlive(config.searx_server, config.searx_port):

        temporaryConfigs = (
            # tabs: https://docs.searxng.org/user/configured_engines.html
            ("searx_tabs", [
                "!general ",
                "!translate ",
                "!web ",
                "!wikimedia ",
                "!images ",
                "!web ",
                "!videos ",
                "!web ",
                "!news ",
                "!web ",
                "!wikimedia ",
                "!map ",
                "!music ",
                "!lyrics ",
                "!radio ",
                "!it ",
                "!packages ",
                "!q&a ",
                "!repos ",
                "!software_wikis ",
                "!science ",
                "!scientific_publications ",
                "!wikimedia ",
                "!files ",
                "!apps ",
                "!social_media ",
            ]),
            ("searx_categories", []),
        )
        config.setConfig(temporaryConfigs, temporary=True)

        def search_searxng(function_args):
            query = function_args.get("query") # required
            config.currentMessages[-1] = {"role": "user", "content": query}
            if config.searx_categories:
                config.searx_categories = [i[1:] for i in config.searx_categories]
                categories = ",".join(config.searx_categories)
            context = SearxSearchWrapper(searx_host=f"{config.searx_server}:{config.searx_port}").run(query, categories=config.searx_categories if config.searx_categories else None)
            fullUrl = f"{config.searx_server}:{config.searx_port}/search?q={plainTextToUrl(query)}&categories={categories}" if config.searx_categories else f"{config.searx_server}:{config.searx_port}/search?q={plainTextToUrl(query)}"
            config.searx_categories = []
            config.stopSpinning()
            print2("```url")
            try:
                print1(fullUrl)
            except:
                print(fullUrl)
            print2("```")
            return context

        functionSignature = {
            "examples": [
                "Search SearXNG",
            ],
            "name": "search_searxng",
            "description": "Perform online searches to obtain the latest and most up-to-date, real-time information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original request in detail, including any supplementary information",
                    },
                },
                "required": ["query"],
            },
        }

        config.addFunctionCall(signature=functionSignature, method=search_searxng)
        config.aliases["@ask_internet "] = "@search_searxng "
        for i in config.searx_tabs:
            tool = i[1:-1]
            config.aliases[f'@{"qna" if tool=="q&a" else tool} '] = f"@search_searxng {i}"
            config.inputSuggestions.append(f'@{"qna" if tool=="q&a" else tool} ')
            config.builtinTools["qna" if tool=="q&a" else tool] = f"""Search the '{"questions_and_answers" if tool=="q&a" else tool}' category for online information."""
        tabsDict = {i: None for i in config.searx_tabs}
        config.inputSuggestions += ["Search SearxNG: ", {"@search_searxng": tabsDict}, {"@ask_internet": tabsDict}]

    else:

        print1(f"Searx Host `{config.searx_server}:{config.searx_port}`! Plugin `search searxng not enabled!`")