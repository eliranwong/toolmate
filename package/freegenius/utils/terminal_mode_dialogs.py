from freegenius import config
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog


class TerminalModeDialogs:

    def __init__(self, parent) -> None:
        self.parent = parent
        self.style = Style.from_dict(
            {
                "dialog": "bg:ansiblack",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiblack {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiblack ansiwhite",
                "dialog shadow": "bg:ansiblack",
            }
        ) if config.terminalResourceLinkColor.startswith("ansibright") else Style.from_dict(
            {
                "dialog": "bg:ansiwhite",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiwhite {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiwhite ansiblack",
                "dialog shadow": "bg:ansiwhite",
            }
        )

    def getValidOptions(self, options=[], descriptions=[], bold_descriptions=False, filter="", default="", title="Available Options", text="Select an option:"):
        if not options:
            return ""
        filter = filter.strip().lower()
        if descriptions:
            descriptionslower = [i.lower() for i in descriptions]
            values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options) if (filter in option.lower() or filter in descriptionslower[index])]
        else:
            values = [(option, option) for option in options if filter in option.lower()]
        if not values:
            if descriptions:
                values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options)]
            else:
                values = [(option, option) for option in options]
        result = radiolist_dialog(
            title=title,
            text=text,
            values=values,
            default=default if default and default in options else values[0][0],
            style=self.style,
        ).run()
        if result:
            notice = f"You've chosen: {result}"
            splittedContent = notice.split(": ", 1)
            key, value = splittedContent
            print_formatted_text(HTML(f"<{config.terminalPromptIndicatorColor2}>{key}:</{config.terminalPromptIndicatorColor2}> {value}"))
            return result
        return ""

    def displayFeatureMenu(self, heading, features):
        values = [(command, command if config.terminalDisplayCommandOnMenu else self.parent.dotCommands[command][0]) for command in features]
        result = radiolist_dialog(
            title=heading,
            text="Select a feature:",
            values=values,
            default=features[0],
            style=self.style,
        ).run()
        if result:
            self.parent.printRunningCommand(result)
            return self.parent.getContent(result)
        else:
            return self.parent.exitAction()
            #return ""

    def getMultipleSelection(self, title="Multiple Selection", text="Select item(s):", options=["ALL"], descriptions=[], default_values=["ALL"]):
        if descriptions:
            values = [(option, descriptions[index]) for index, option in enumerate(options)]
        else:
            values = [(option, option) for option in options]
        return checkboxlist_dialog(
            title=title,
            text=text,
            values=values,
            default_values=default_values,
            style=self.style,
        ).run()
