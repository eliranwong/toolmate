from toolmate import config, isCommandInstalled, print2
import os, shutil, subprocess

# add config item `fabricPath`.  Users can customise fabric path by editing its value in `config.py`.
whichFabric = shutil.which("fabric")
persistentConfigs = (
    ("fabricPath", whichFabric if whichFabric else "fabric"),
)
config.setConfig(persistentConfigs)

if isCommandInstalled(config.fabricPath) or os.path.isfile(config.fabricPath):
    # add aliases
    config.aliases["@fabric_pattern "] = f"@command {config.fabricPath} -p "
    config.aliases["@append_fabric_pattern "] = f"@append_command {config.fabricPath} -p "
    config.aliases["@fabric "] = f"@command {config.fabricPath} "
    config.aliases["@append_fabric "] = f"@append_command {config.fabricPath} "
    # add input suggestions
    patterns = subprocess.run("fabric -l", shell=True, capture_output=True, text=True).stdout.split("\n\t")[1:]
    patterns = {f"{i} ": None for i in patterns}
    config.inputSuggestions += [{"@fabric_pattern": patterns}, {"@append_fabric_pattern": patterns}]
    patterns = {"-p": patterns}
    config.inputSuggestions += [{"@fabric": patterns}, {"@append_fabric": patterns}]

    config.builtinTools["fabric"] = "Execute a fabric command"
    config.builtinTools["append_fabric"] = "Execute a fabric command with the previous text output appended to it"
else:
    print2("`fabric` not found! Read https://github.com/danielmiessler/fabric for installation!")
