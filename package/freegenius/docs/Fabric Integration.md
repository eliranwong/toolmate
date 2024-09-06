# Fabric Integration

Integration of `fabric` has been available from version: 0.2.90+.

Enter `@fabric` or `@append_fabric`, followed by fabric parameters

`@fabric` Execute the given fabric command

`@append_fabric` Append assistant previous response to the given fabric command and execute.

# How to use `fabric` with other FreeGenius AI tools?

Assuming `fabric` is installed and the FreeGenius AI tool plugin `fabric` is enabled, you may run something like:

```
@fabric -m gemini-1.5-pro -p write_essay "What is machine learning?"
@append_fabric -m llama3.1:latest -p extract_wisdom
@append_fabric -m mistral-large:123b -p summarize
@ask_gemini Explain it to a five-year kid
@ask_chatgpt Translate it into Chinese
```

For using multiple tools in a single prompt, read https://github.com/eliranwong/freegenius/wiki/Multiple-Tools-in-One-Go

# Difference from Running Fabric Alone

Fabric integration in FreeGenius AI brings `fabric` to interact with other AI tools, supported by FreeGenius AI. Fabric output is directly integrated into the main FreeGenius AI message chain.

# Requirement

Install `fabric` first! Read https://github.com/danielmiessler/fabric

# How does the integration work?

The integration works with the tools `@command` and `@append_command` in FreeGenius AI

`@command` Execute the given command

`@append_command` Append assistant previous response to the given command and execute.

In plugin `fabric.py`, two aliases are created:

`@fabric` -> `@command fabric`

`@append_fabric` -> `@append_command fabric`

Version 0.2.91 added config item `fabricPath`.  Users can customise fabric path by editing its value in `config.py`.

Read more about system command integration at system command integration at https://github.com/eliranwong/freegenius/wiki/System-Command-Integration
