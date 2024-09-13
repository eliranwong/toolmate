from toolmate import config
import pprint, re, os, shutil
from toolmate.utils.config_essential import defaultSettings
from prompt_toolkit.shortcuts import yes_no_dialog

def loadConfig(configPath):
    with open(configPath, "r", encoding="utf-8") as fileObj:
        configs = fileObj.read()
    configs = "from toolmate import config\n" + re.sub("^([A-Za-z])", r"config.\1", configs, flags=re.M)
    exec(configs, globals())

def setConfig(defaultSettings, thisTranslation={}, temporary=False):
    for key, value in defaultSettings:
        if not hasattr(config, key):
            value = pprint.pformat(value)
            exec(f"""config.{key} = {value} """)
            if temporary:
                config.excludeConfigList.append(key)
    if thisTranslation:
        for i in thisTranslation:
            if not i in config.thisTranslation:
                config.thisTranslation[i] = thisTranslation[i]

storageDir = config.localStorage

# restore configs from backup
if os.path.isdir(storageDir):
    configFile = os.path.join(config.toolMateAIFolder, "config.py")
    if os.path.getsize(configFile) == 0:
        # It means that it is either a newly installed copy or an upgraded copy
        
        # delete old shortcut files so that newer versions of shortcuts can be created
        appName = config.toolMateAIName.split()[0]
        shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop", f"{appName}Hub.bat", f"{appName}Hub.command", f"{appName}Hub.desktop")
        for shortcutFile in shortcutFiles:
            shortcut = os.path.join(config.toolMateAIFolder, shortcutFile)
            if os.path.isfile(shortcut):
                os.remove(shortcut)
        # delete system tray shortcuts
        shortcut_dir = os.path.join(config.toolMateAIFolder, "shortcuts")
        shutil.rmtree(shortcut_dir, ignore_errors=True)

        # check if config backup is available
        backupFile = os.path.join(storageDir, "config_backup.py")
        if os.path.isfile(backupFile):
            restore_backup = yes_no_dialog(
                title="Configuration Backup Found",
                text=f"Do you want to use the following backup?\n{backupFile}"
            ).run()
            if restore_backup:
                try:
                    loadConfig(backupFile)
                    shutil.copy(backupFile, configFile)
                    print("Configuration backup restored!")
                    #config.restartApp()
                except:
                    print("Failed to restore backup!")

# load new / unsaved configs
setConfig(defaultSettings)
