from freegenius import config, isCommandInstalled
import os, shutil

# add config item `fabricPath`.  Users can customise fabric path by editing its value in `config.py`.
whichFabric = shutil.which("fabric")
persistentConfigs = (
    ("fabricPath", whichFabric if whichFabric else "fabric"),
)
config.setConfig(persistentConfigs)

if isCommandInstalled(config.fabricPath) or os.path.isfile(config.fabricPath):
    # add aliases
    config.aliases["@fabric "] = f"@command {config.fabricPath} "
    config.aliases["@append_fabric "] = f"@append_command {config.fabricPath} "
    # add input suggestions
    config.inputSuggestions += ["@fabric ", "@append_fabric "]
else:
    print2("`fabric` not found! Read https://github.com/danielmiessler/fabric for installation!")