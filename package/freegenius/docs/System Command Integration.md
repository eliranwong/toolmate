## System Command Integration

Two new tools were added from Version: 0.2.90+

`@command` Execute the given command

`@append_command` Append assistant previous response to the given command and execute.

```
@command echo "Hello World!"
@append_command echo
```

These new tools work with multiple tools in a single prompt.

For an example, to integrate `fabric` with other FreeGenius AI tools, you may do something like this:

```
@command /home/ubuntu/go/bin/fabric -m gemini-1.5-pro -p write_essay "What is machine learning?"
@append_command /home/ubuntu/go/bin/fabric -m llama3.1:latest -p extract_wisdom
@append_command /home/ubuntu/go/bin/fabric -m mistral-large:123b -p summarize
@ask_gemini Explain it to a five-year kid
@ask_chatgpt Translate it into Chinese
```

# Difference from running system command on their own?

System Command integration in FreeGenius AI allows interaction of any system commands with other AI tools, supported by FreeGenius AI. System command output is directly integrated into the main FreeGenius AI message chain.

# Fabric Integration

Read more about fabric integration at https://github.com/eliranwong/freegenius/blob/main/package/freegenius/docs/Fabric%20Integration.md