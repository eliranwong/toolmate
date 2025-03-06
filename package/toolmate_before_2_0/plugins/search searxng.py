"""
ToolMate AI Plugin - search SearXNG

Default Configurations
(assuming Perplexica is installed locally)
searx_server = "localhost"
searx_port = 4000

You can manually edit config.py to customise these settings.

[TOOL_CALL]
"""

from toolmate import config, isServerAlive, print1, print2, plainTextToUrl, convert_html_to_markdown, get_local_ip
import re, requests

persistentConfigs = (
    ("searx_server", "http://localhost"),
    ("searx_port", 4000),
)
config.setConfig(persistentConfigs)
if config.searx_server == "localhost":
    config.searx_server = "http://localhost"

if not isServerAlive(re.sub("http://|https://", "", config.searx_server), config.searx_port):
    config.searx_server = f"http://{get_local_ip()}" # access to the server running outside a container

if isServerAlive(re.sub("http://|https://", "", config.searx_server), config.searx_port):

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

    def refineSearchResults(content, removeLink=True):
        content = convert_html_to_markdown(content)
        content = re.sub(r"\nNext page\n[\d\D]*$", "", content) # trim the footer
        searchResults = content.split("\n#")[1:] # trim the header
        refinedSearchResults = []
        for index, result in enumerate(searchResults):
            paragraphs = result.split("\n\n")
            textOnlyParagraphs = []
            for paragraph in paragraphs:
                if not re.search(r"\n\[[^\[\]]+\]\([^\)\)]+\)\n", f"\n{paragraph.strip()}\n"):
                    textOnlyParagraphs.append(paragraph.strip())
            if textOnlyParagraphs:
                refinedSearchResults.append("\n\n".join(textOnlyParagraphs))
            elif strippedResult := result.strip():
                refinedSearchResults.append(strippedResult)
            if len(refinedSearchResults) >= config.maximumInternetSearchResults:
                break
        return "#" + "\n\n#".join(refinedSearchResults)

    def search_searxng(function_args):
        if function_args:
            query = function_args.get("query")
            config.currentMessages[-1] = {"role": "user", "content": query}
        else:
            query = config.currentMessages[-1]["content"]
        if config.searx_categories:
            config.searx_categories = [i[1:] for i in config.searx_categories]
            categories = ",".join(config.searx_categories)
        #from langchain_community.utilities import SearxSearchWrapper
        #context = SearxSearchWrapper(searx_host=f"{config.searx_server}:{config.searx_port}").run(query, categories=config.searx_categories if config.searx_categories else None)
        fullUrl = f"{config.searx_server}:{config.searx_port}/search?q={plainTextToUrl(query)}&categories={categories}" if config.searx_categories else f"{config.searx_server}:{config.searx_port}/search?q={plainTextToUrl(query)}"
        context = requests.get(fullUrl, timeout=60).text
        context = refineSearchResults(context) if context else ""
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
            "properties": {} if not config.tool_selection_agent else {
                "query": {
                    "type": "string",
                    "description": "The original request in detail, including any supplementary information",
                },
            },
            "required": [] if not config.tool_selection_agent else ["query"],
        },
    }

    config.addToolCall(signature=functionSignature, method=search_searxng)
    config.aliases["@online "] = "@search_searxng "
    config.builtinTools["online"] = "Perform online searches to obtain the latest and most up-to-date, real-time information"
    for i in config.searx_tabs:
        tool = i[1:-1]
        config.aliases[f'@{"qna" if tool=="q&a" else tool} '] = f"@search_searxng {i}"
        config.inputSuggestions.append(f'@{"qna" if tool=="q&a" else tool} ')
        config.builtinTools["qna" if tool=="q&a" else tool] = f"""Search the '{"questions_and_answers" if tool=="q&a" else tool}' category for online information."""
    tabsDict = {i: None for i in config.searx_tabs}
    config.inputSuggestions += ["Search SearxNG: ", {"@search_searxng": tabsDict}, {"@online": tabsDict}]

else:

    print1(f"Searx Host `{config.searx_server}:{config.searx_port}` not found! Plugin `search searxng not enabled!`")