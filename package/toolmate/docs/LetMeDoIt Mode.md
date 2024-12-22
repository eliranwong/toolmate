# LetMeDoIt Mode

You can use LetMeDoIt mode, by setting "config.llmBackend" to "letmedoit".

In LetMeDoIt mode, the assistant handles all your requests as [LetMeDoIt AI](https://github.com/eliranwong/letmedoit) does

## Differences between LetMeDoIt Mode and ChatGPT Mode

Both LetMeDoIt Mode and ChatGPT Mode are powered by ChatGPT models.

Major differences are listed below:

1. Configurations are different even both are powered 

ChatGPT Mode: "config.llmBackend" set to "openai"

LetMeDoIt Mode: "config.llmBackend" set to "letmedoit"

2. Screening

ChatGPT Mode: Screening of user requests is optional

LetMeDoIt Mode: Screening option is not applicable

3. Tool Selection from Multiple Options

ChatGPT Mode: Determined by the closest similarity search in ToolMate AI tool store. User selection will be supported by introducing config.auto_tool_selection_threshold and config.maximum_tool_choices 

LetMeDoIt Mode: Totally determined by ChatGPT models

4. Token Costs

ChatGPT Mode: Cheaper, as only one tool, the selected one, is handled in each function call.

LetMeDoIt Mode: More expensive, as all enabled tools are handled together in each function call, which is required for automatic tool selection.

5. Speed

ChatGPT Mode: Slower in case only a few tools are in place. Faster in case there are many tools installed and enabled.

LetMeDoIt Mode: Faster in case only a few tools are in place. Slower in case there are many tools installed and enabled.

6. Prompt

ChatGPT Mode: As tool selection is partially determined by similarity search, use more explicit and relevant in prompt requests to enhance tool selection.

LetMeDoIt Mode: Smarter in tool auto selection.

7. Testing

ChatGPT Mode: Still in testing stage that some tools may not work.  Please kindly help report of any issues at https://github.com/eliranwong/toolmate/issues 

LetMeDoIt Mode: All tools were originally developed for LetMeDoIt AI. They should work out of the box.