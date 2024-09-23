# Tool Selection Agent

![tool_selection_agent_compressed](https://github.com/user-attachments/assets/c963ca48-cb01-4eb7-b40d-57e2a4a92eaf)

You can always manually call a specific tool by entering a tool name prefixed with `@`.  You can even call multiple tools in a single request.  Read https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Supported%20Backends%20and%20Models.md

To automate the tool selection process, ToolMate AI offers a `Tool Selection Agent` built-in for such purpose. When `Tool Selection Agent` is enabled, it recommends appropriate tools to resolve your requests.

# Enhance Tool Selection

Enabling the `Tool Selection Agent` prompts the question, "Would you like to inform the Tool Selection Agent of each tool's requirements? Doing so could improve the selection outcome, but it will consume more tokens and processing power." When this option is enabled, ToolMate AI communicates each tool's requirements to the tool selection agent to improve the selection process. However, this comes at the cost of increased input tokens and computing power requirements.

# Automatic Tool Selection

With the `Tool Selection Agent` enabled, you have the additional option to enable `Automatic Tool Selection`. This allows the `Tool Selection Agent` to automatically apply the first recommended tool for each request. The `Tool Selection Agent` may recommend multiple tools to resolve a single request. You can enable the `Automatic Tool Selection` option to automatically use the most relevant tool, or disable the option to manually select a tool from the recommendations. With manual selection, you can choose the `chat only` option, which outputs only LLM-based response without use of any third-party tools, or select `more ...` to view and choose from all enabled tools.

# Configurations

<img width="842" alt="action_menu_tools" src="https://github.com/user-attachments/assets/954c0a79-b735-4c61-a371-e985a83a0f69">

You can enable / disable `Tool Selection Agent` in `Automatic Tool Selection` in one of the following ways:

* Select `configure tool selection agent` from [Action Menu](https://github.com/eliranwong/toolmate/blob/main/package/toolmate/docs/Action%20Menu.md)

* Enter `.tools` in ToolMate AI prompt.

<img width="842" alt="tools1" src="https://github.com/user-attachments/assets/3592dd35-ca6e-45f1-9379-47dc9d92f0eb">

<img width="842" alt="tools2" src="https://github.com/user-attachments/assets/93eafe01-781d-4336-a97f-04868e6a83dc">

<img width="842" alt="tools3" src="https://github.com/user-attachments/assets/3928d857-1a24-4440-8687-a73c6bf45bc1">

# Backward Compatibility to LetMeDoIt

`Tool Selection Agent` works only with backends other than LetMeDoIt mode.  In LetMeDoIt mode, tool selection is handled by ChatGPT auto fucntion callings.