from freegenius import config

config.aliases["@fabric"] = "@command fabric"
config.aliases["@append_fabric"] = "@append_command fabric"

config.inputSuggestions += ["@fabric", "@append_fabric"]