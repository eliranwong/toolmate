# Chat Record Management

All conversation records are saveable, searchable and shareable.

# Auto Saving

All conversation records are automatically saved in plain text formats, if the app exits properly.

The saved records are stored in directory `~/toolmate/chats/` by default, where `~` denotes your home directory.

# Manual Saving

To make sure your current conversation is saved up to a certain point, either:

* Run `.save` in ToolMate AI prompt ui.

or 

* Select `save current conversation` via ToolMate AI action menu.

# Save as ...

You can save a conversation with a custom name at a custom location. Either:

* Run `.saveas` in ToolMate AI prompt ui.

or 

* Select `save current conversation as ...` via ToolMate AI action menu.

# Open a Saved Conversation

This is a practical feature that allows users to resume any previous conversations at any time..

* Run `.open` in ToolMate AI prompt ui.

or 

* Select `open a saved conversation` via ToolMate AI action menu.

Enter a file name, if the record file is in your current directory.  Otherwise, enter the file path to open it.

# Search Previous Conversations

With the plugin "Search chat records" enabled:

* All chat records are automatically saved in vector database format, in addition to the plain text format mentioned above.
* You can use tool `@search_conversations` to search your old conversations.
* You can use tool `@load_conversations` to load an old conversation, by specifying a chat ID identified in search results.

# Share Conversations

You can simply share the saved conversations in plain text format with others.  They can load them with ToolMate AI and continue the conversations.

# Keep a Readable Copy

To save a more readable copy in plain text format, either:

* Run `.export` in ToolMate AI prompt ui.

or 

* Select `export current conversation` via ToolMate AI action menu.

Enter a file name or path to expor the current conversation.