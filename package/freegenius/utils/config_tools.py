from freegenius import config
import pprint, re, os, shutil
from freegenius.utils.config_essential import defaultSettings
from freegenius.utils.shared_utils import SharedUtil
from prompt_toolkit.shortcuts import yes_no_dialog

def loadConfig(configPath):
    with open(configPath, "r", encoding="utf-8") as fileObj:
        configs = fileObj.read()
    configs = "from freegenius import config\n" + re.sub("^([A-Za-z])", r"config.\1", configs, flags=re.M)
    exec(configs, globals())
config.loadConfig = loadConfig

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
config.setConfig = setConfig

storageDir = SharedUtil.getLocalStorage()
if os.path.isdir(storageDir):
    configFile = os.path.join(config.letMeDoItAIFolder, "config.py")
    if os.path.getsize(configFile) == 0:
        # It means that it is either a newly installed copy or an upgraded copy
        
        # delete old shortcut files so that newer versions of shortcuts can be created
        appName = config.letMeDoItName.split()[0]
        shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop", f"{appName}Tray.bat", f"{appName}Tray.command", f"{appName}Tray.desktop")
        for shortcutFile in shortcutFiles:
            shortcut = os.path.join(config.letMeDoItAIFolder, shortcutFile)
            if os.path.isfile(shortcut):
                os.remove(shortcut)
        # delete system tray shortcuts
        shortcut_dir = os.path.join(config.letMeDoItAIFolder, "shortcuts")
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
setConfig(defaultSettings)
# Google Credentials
# set required file

config.google_cloud_credentials_file = os.path.join(storageDir, "credentials_google_cloud.json")
if config.google_cloud_credentials and os.path.isfile(config.google_cloud_credentials):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials
else:
    gccfile2 = os.path.join(storageDir, "credentials_googleaistudio.json")
    gccfile3 = os.path.join(storageDir, "credentials_googletts.json")

    if os.path.isfile(config.google_cloud_credentials_file):
        config.google_cloud_credentials = config.google_cloud_credentials_file
    elif os.path.isfile(gccfile2):
        config.google_cloud_credentials = gccfile2
    elif os.path.isfile(gccfile3):
        config.google_cloud_credentials = gccfile3
    else:
        config.google_cloud_credentials = ""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.google_cloud_credentials if config.google_cloud_credentials else ""
