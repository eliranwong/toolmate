# Tool Selection Configurations

You can always manually call a tool by entering a tool name prefixed with `@`.  You can even call multiple tools in a single request.  Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Supported%20Backends%20and%20Models.md

To automate the tool selection process, ToolMate AI has two agents built-in for such purpose. They are `Tool Screening Agent` and `Tool Selection Agent`.

Remarks: Both `Tool Screening Agent` and `Tool Selection Agent` work only when you do not manually specify a tool in your request. Therefore, even they are enabled, you can still manually use `@` to call a particular tool or multiple tools.

# Tool Screening Agent

`Tool Screening Agent` suggests `Tool Selection Agent` whether a tool is required based on your entry.

You can enable / disable `Tool Screening Agent` in `Tool Selection Configurations` via [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md).  However, this option is only applied if `Tool Selection Agent` is enabled. Read more below.

# Tool Selection Agent

You can enable / disable `Tool Selection Agent` in `Tool Selection Configurations` via [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md)

![too_dependence](https://github.com/eliranwong/toolmate/assets/25262722/a637ed22-47d0-474f-bbbb-5dabb1b31e24)

ToolMate AI enhances LLM capabilities by offering tools through plugins. When a user makes a request, ToolMate AI searches for and selects a suitable tool from its tool store. This search involves finding similarities between the user query and the examples provided in the tool plugins. Users have the flexibility to customize the tool selection process by adjusting three key configurations:

1. tool_dependence
2. tool_auto_selection_threshold
3. tool_selection_max_choices

# Tool Dependence

The value of 'tool_dependence' determines how you want to rely on tools.

Default: 0.8

Acceptable range: 0.0 - 1.0

A value of 0.0 indicates that tools are disabled. ToolMate's responses are totally based on capabilities of the selected LLM.

A value of 1.0 indicates that tools always apply for each response.

A value between 0.0 and 0.1 indicates that a tool is selected only when tool distance search is less than or equal to its value.

Therefore, you are more likely to use tools when you set a higher value.

# Tool Auto Selection Threshold

The value of 'tool_auto_selection_threshold' determines the threshold of automatic tool selection.

Default: 0.5

Acceptable range: 0.0 - [the value of tool_dependence]

A value of 0.0 indicates that automatic tool selection is disabled. Users must manually choose a tool from the most relevant options identified in each tool search.

A value that is equal to or larger than the value of 'tool_dependence' indicates that tool selection is always automatic.

A value between 0.0 and the value of 'tool_dependence' indicates that tool selection is only automatic when its value is larger than or equal to the tool search distance. Users need to choose a tool from the most relevant options in case automatic tool selection is not applied and tool search distance is less than or equal to the value of tool_dependence.

# Tool Selection Max Choices

The value of 'tool_selection_max_choices' determines the maximum number of available options for manual tool selection.

Default: 4

# How to change the tool selection configurations:

1. Enter a blank entry '' and select 'change tool selection configurations' from the action menu.

2. Follow the prompts and enter values to change the configurations.

# Quick Way to Change Tool Dependence

To make a change, you enter enter the value of tool_dependence and tool_auto_selection_threshold, separated by '!', in ToolMate AI prompt, e.g.:

> 0.9!0.2

Tool dependence changed to: 0.9<br>
Tool auto selection threshold changed to: 0.2

You can also just enter a float value in ToolMate AI prompt to adjust the values instantly.

> 0.8
                                                                                                                                                                              
Tool dependence changed to: 0.8<br>
Tool auto selection threshold changed to: 0.5

Note: Wheh 'tool_auto_selection_threshold' is not specified in the last case, the value of tool_auto_selection_threshold is calculated based on the value of tool_dependence * 5/8.
