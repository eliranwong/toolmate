from freegenius import config
from pathlib import Path
import platform, os, sys, ctypes, subprocess, re
import shutil

def createShortcuts():
    systemtrayFile = os.path.join(config.letMeDoItAIFolder, "systemtray.py")

    thisOS = platform.system()
    appName = config.letMeDoItName.split()[0]
    # Windows icon
    if thisOS == "Windows":
        myappid = "letmedoit.ai"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", f"{appName}.ico"))
        if not os.path.isfile(windowsIconPath):
            windowsIconPath = os.path.abspath(os.path.join(sys.path[0], "icons", "LetMeDoIt.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(windowsIconPath)

    # Desktop shortcut
    # on Windows
    if thisOS == "Windows":
        shortcutBat1 = os.path.join(config.letMeDoItAIFolder, f"{appName}.bat")
        desktopShortcut1a = os.path.join(os.path.expanduser('~'), 'Desktop', f"{appName}.bat")
        desktopShortcut1b = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop', f"{appName}.bat")
        sendToShortcut1 = os.path.join(os.path.expanduser('~'), os.environ["APPDATA"], 'Microsoft\Windows\SendTo', f"{appName}.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "{sys.executable} '{config.letMeDoItFile}' \\"%1\\""'''
        # Create .bat for application shortcuts
        if not os.path.exists(shortcutBat1):
            for i in (shortcutBat1, desktopShortcut1a, desktopShortcut1b, sendToShortcut1):
                try:
                    print("creating shortcuts ...")
                    with open(i, "w") as fileObj:
                        fileObj.write(shortcutCommand1)
                    print(f"Created: {shortcutBat1}")
                except:
                    pass
        # system tray shortcut
        shortcutBat1 = os.path.join(config.letMeDoItAIFolder, f"{appName}Tray.bat")
        desktopShortcut1a = os.path.join(os.path.expanduser('~'), 'Desktop', f"{appName}Tray.bat")
        desktopShortcut1b = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop', f"{appName}Tray.bat")
        shortcutCommand1 = f'''powershell.exe -NoExit -Command "{sys.executable} '{systemtrayFile}'"'''
        # Create .bat for application shortcuts
        if not os.path.exists(shortcutBat1):
            for i in (shortcutBat1, desktopShortcut1a, desktopShortcut1b):
                try:
                    print("creating system tray shortcuts ...")
                    with open(i, "w") as fileObj:
                        fileObj.write(shortcutCommand1)
                    print(f"Created: {shortcutBat1}")
                except:
                    pass

    # on macOS
    # on iOS a-Shell app, ~/Desktop/ is invalid
    elif thisOS == "Darwin":
        desktopPath = os.path.expanduser("~/Desktop")
        if os.path.isdir(desktopPath):
            shortcut_file = os.path.join(config.letMeDoItAIFolder, f"{appName}.command")
            if not os.path.isfile(shortcut_file):
                print("creating shortcut ...")
                with open(shortcut_file, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f"cd {config.letMeDoItAIFolder}\n")
                    f.write(f"{sys.executable} {config.letMeDoItFile}\n")
                os.chmod(shortcut_file, 0o755)
                print(f"Created: {shortcut_file}")
                shutil.copy(shortcut_file, desktopPath) # overwrites older version
                print("Copied to Desktop!")
            # system tray shortcut
            shortcut_file = os.path.join(config.letMeDoItAIFolder, f"{appName}Tray.command")
            if not os.path.isfile(shortcut_file):
                print("creating system tray shortcut ...")
                with open(shortcut_file, "w") as f:
                    f.write("#!/bin/bash\n")
                    f.write(f"cd {config.letMeDoItAIFolder}\n")
                    f.write(f"{sys.executable} {systemtrayFile}\n")
                os.chmod(shortcut_file, 0o755)
                print(f"Created: {shortcut_file}")
                shutil.copy(shortcut_file, desktopPath) # overwrites older version
                print("Copied to Desktop!")

    # additional shortcuts on Linux
    elif thisOS == "Linux":
        def desktopFileContent():
            iconPath = os.path.join(config.letMeDoItAIFolder, "icons", f"{appName}.png")
            if not os.path.isfile(iconPath):
                iconPath = os.path.join(config.letMeDoItAIFolder, "icons", "LetMeDoIt.png")
            return f"""#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Path={config.letMeDoItAIFolder}
Exec={sys.executable} {config.letMeDoItFile}
Icon={iconPath}
Name={config.letMeDoItName}
"""
        linuxDesktopFile = os.path.join(config.letMeDoItAIFolder, f"{appName}.desktop")
        if not os.path.exists(linuxDesktopFile):
            print("creating shortcut ...")
            # Create .desktop shortcut
            with open(linuxDesktopFile, "w") as fileObj:
                fileObj.write(desktopFileContent())
            print(f"Created: {linuxDesktopFile}")
            try:
                # Try to copy the newly created .desktop file to:
                from pathlib import Path
                # ~/.local/share/applications
                userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
                Path(userAppDir).mkdir(parents=True, exist_ok=True)
                shutil.copy(linuxDesktopFile, userAppDir) # overwrites older version
                print(f"Copied to '{userAppDir}'!")
                # ~/Desktop
                desktopPath = os.path.expanduser("~/Desktop")
                if os.path.isdir(desktopPath):
                    shutil.copy(linuxDesktopFile, desktopPath) # overwrites older version
                    print("Copied to Desktop!")
            except:
                pass
        # system tray shortcut
        def desktopSystemTrayFileContent():
            iconPath = os.path.join(config.letMeDoItAIFolder, "icons", f"systemtray.png")
            if not os.path.isfile(iconPath):
                iconPath = os.path.join(config.letMeDoItAIFolder, "icons", "LetMeDoIt.png")
            return f"""#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Path={config.letMeDoItAIFolder}
Exec={sys.executable} {systemtrayFile}
Icon={iconPath}
Name={config.letMeDoItName} Tray
"""
        linuxDesktopFile = os.path.join(config.letMeDoItAIFolder, f"{appName}Tray.desktop")
        if not os.path.exists(linuxDesktopFile):
            print("creating system tray shortcut ...")
            # Create .desktop shortcut
            with open(linuxDesktopFile, "w") as fileObj:
                fileObj.write(desktopSystemTrayFileContent())
            print(f"Created: {linuxDesktopFile}")
            try:
                # Try to copy the newly created .desktop file to:
                from pathlib import Path
                # ~/.local/share/applications
                userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
                Path(userAppDir).mkdir(parents=True, exist_ok=True)
                shutil.copy(linuxDesktopFile, userAppDir) # overwrites older version
                print(f"Copied to '{userAppDir}'!")
                # ~/Desktop
                desktopPath = os.path.expanduser("~/Desktop")
                if os.path.isdir(desktopPath):
                    shutil.copy(linuxDesktopFile, desktopPath) # overwrites older version
                    print("Copied to Desktop!")
            except:
                pass

    # create utilities
    createUtilities()
    #createAppAlias()

def createUtilities():
    first_name = config.letMeDoItName.split()[0]
    storage = os.path.join(os.path.expanduser('~'), first_name.lower())
    try:
        Path(storage).mkdir(parents=True, exist_ok=True)
    except:
        pass

    thisOS = platform.system()
    if thisOS == "Windows":
        work_with_text_script = f'''param (
    [string]$selected_text
)
Start-Process "{sys.executable} {config.letMeDoItFile} $selected_text"'''
        work_with_text_script_path = os.path.join(storage, f"{first_name}.ps1")
        with open(work_with_text_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
    elif thisOS == "Linux":
        # work with text selection
        # Install xsel
        # > apt install xsel
        # To use this script, users need to:
        # 1. Launch "Settings"
        # 2. Go to "Keyboard" > "Keyboard Shortcuts" > "View and Customise Shortcuts" > "Custom Shortcuts"
        # 3. Select "+" to add a custom shortcut and enter the following information, e.g.:
        # Name: LetMeDoIt AI
        # Command: /usr/bin/gnome-terminal --command ~/letmedoit/letmedoit.sh
        # Shortcut: Ctrl + Alt + L
        # get selected text
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false "$selected_text"'''
        work_with_text_script_path = os.path.join(storage, first_name)
        with open(work_with_text_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # summarise selected text
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Summarize" -r "$selected_text"'''
        work_with_summary_script_path = os.path.join(storage, f"{first_name}_Summary")
        with open(work_with_summary_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # download selected url
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Download" -r "$selected_text"'''
        work_with_download_script_path = os.path.join(storage, f"{first_name}_Download")
        with open(work_with_download_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # download selected Youtube url into mp3
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Download Youtube MP3" -r "$selected_text"'''
        work_with_downloadmp3_script_path = os.path.join(storage, f"{first_name}_YoutubeMP3")
        with open(work_with_downloadmp3_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # pronounce selected text
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Pronounce" -r "$selected_text"'''
        work_with_pronunciation_script_path = os.path.join(storage, f"{first_name}_Pronunciation")
        with open(work_with_pronunciation_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # explain selected text
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Explain" -r "$selected_text"'''
        work_with_explanation_script_path = os.path.join(storage, f"{first_name}_Explanation")
        with open(work_with_explanation_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # translate selected text
        work_with_text_script = f'''#!/usr/bin/env bash
selected_text=$(echo "$(xsel -o)" | sed 's/"/\"/g')
{sys.executable} {config.letMeDoItFile} -u false -n true -i false -c "Let me Translate" -r "$selected_text"'''
        work_with_translation_script_path = os.path.join(storage, f"{first_name}_Translation")
        with open(work_with_translation_script_path, "w", encoding="utf-8") as fileObj:
            fileObj.write(work_with_text_script)
        # work with files or folders selection via NAUTILUS; right-click > scripts > LetMeDoIt
        if not config.isTermux:
            work_with_files_script = f'''#!/usr/bin/env bash
mkdir -p {storage}
# Get the selected file or folder path
path="$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"
echo "$path" > {storage}/selected_files.txt
/usr/bin/gnome-terminal --command "{sys.executable} {config.letMeDoItFile} -u false -n true -i false -f {storage}/selected_files.txt"'''
            scripts_path = os.path.expanduser("~/.local/share/nautilus/scripts")
            Path(scripts_path).mkdir(parents=True, exist_ok=True)
            work_with_files_script_path = os.path.join(scripts_path, first_name)
            with open(work_with_files_script_path, "w", encoding="utf-8") as fileObj:
                fileObj.write(work_with_files_script)
        # make script files executable
        scriptFiles = [
            work_with_translation_script_path,
            work_with_explanation_script_path,
            work_with_summary_script_path,
            work_with_text_script_path,
            work_with_pronunciation_script_path,
            work_with_downloadmp3_script_path,
            work_with_download_script_path,
        ]
        if config.isTermux:
            # added a command shortcut
            try:
                termux_shortcut_script = f'''#!/usr/bin/env bash\n{sys.executable} {config.letMeDoItFile}'''
                termux_shortcut_path = "/data/data/com.termux/files/usr/bin/letmedoit"
                with open(termux_shortcut_path, "w", encoding="utf-8") as fileObj:
                    fileObj.write(termux_shortcut_script)
                scriptFiles.append(termux_shortcut_path)
            except:
                pass
        else:
            scriptFiles.append(work_with_files_script_path)
        for i in scriptFiles:
            os.chmod(i, 0o755)
    elif thisOS == "Darwin":
        file1 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Text_workflow/Contents/document.wflow")
        file2 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Files_workflow/Contents/document.wflow")
        file3 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Explanation_workflow/Contents/document.wflow")
        file4 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Translation_workflow/Contents/document.wflow")
        file5 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Summary_workflow/Contents/document.wflow")
        file6 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Pronounce_workflow/Contents/document.wflow")
        file7 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_YoutubeMP3_workflow/Contents/document.wflow")
        file8 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Download_workflow/Contents/document.wflow")
        for i in (file1, file2, file3, file4, file5, file6, file7, file8):
            with open(i, "r", encoding="utf-8") as fileObj:
                content = fileObj.read()
            search_replace = (
                ("~/letmedoit", storage),
                ("\[LETMEDOIT_PATH\]", f"{sys.executable} {config.letMeDoItFile}"),
            )
            for search, replace in search_replace:
                content = re.sub(search, replace, content)
            with open(i, "w", encoding="utf-8") as fileObj:
                fileObj.write(content)
        file1 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Files_workflow/Contents/Info.plist")
        file2 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Text_workflow/Contents/Info.plist")
        file3 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Explanation_workflow/Contents/Info.plist")
        file4 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Translation_workflow/Contents/Info.plist")
        file5 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Summary_workflow/Contents/Info.plist")
        file6 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Pronounce_workflow/Contents/Info.plist")
        file7 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_YoutubeMP3_workflow/Contents/Info.plist")
        file8 = os.path.join(config.letMeDoItAIFolder, "macOS_service/LetMeDoIt_Download_workflow/Contents/Info.plist")
        for i in (file1, file2, file3, file4, file5, file6, file7, file8):
            with open(i, "r", encoding="utf-8") as fileObj:
                content = fileObj.read()
            content = re.sub("LetMeDoIt", first_name, content)
            with open(i, "w", encoding="utf-8") as fileObj:
                fileObj.write(content)
        folder1 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Files_workflow")
        folder1_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Files.workflow")
        folder2 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Text_workflow")
        folder2_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Text.workflow")
        folder3 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Explanation_workflow")
        folder3_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Explanation.workflow")
        folder4 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Summary_workflow")
        folder4_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Summary.workflow")
        folder5 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Translation_workflow")
        folder5_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Translation.workflow")
        folder6 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Pronounce_workflow")
        folder6_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Pronunciation.workflow")
        folder7 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_YoutubeMP3_workflow")
        folder7_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Youtube MP3.workflow")
        folder8 = os.path.join(config.letMeDoItAIFolder, "macOS_service", "LetMeDoIt_Download_workflow")
        folder8_dest = os.path.join(os.path.expanduser("~/Library/Services"), f"{first_name} Download.workflow")
        folders = (
            (folder1, folder1_dest),
            (folder2, folder2_dest),
            (folder3, folder3_dest),
            (folder4, folder4_dest),
            (folder5, folder5_dest),
            (folder6, folder6_dest),
            (folder7, folder7_dest),
            (folder8, folder8_dest),
        )
        for folder, folder_dest in folders:
            if os.path.isdir(folder_dest):
                shutil.rmtree(folder_dest, ignore_errors=True)
            shutil.copytree(folder, folder_dest)
        iconFolder = os.path.join(config.letMeDoItAIFolder, "icons")
        iconFolder_dest = os.path.join(storage, "icons")
        if not os.path.isdir(iconFolder_dest):
            shutil.copytree(iconFolder, iconFolder_dest)

def createAppAlias():
    with open(os.path.join(config.letMeDoItAIFolder, "package_name.txt"), "r", encoding="utf-8") as fileObj:
        package = fileObj.read()
    alias = package
    target = f"{sys.executable} {config.letMeDoItFile}"

    findAlias = "/bin/bash -ic 'alias letmedoit'" # -c alone does not work
    aliasOutput, *_ = subprocess.Popen(findAlias, shell=True, stdout=subprocess.PIPE, text=True).communicate()

    if not aliasOutput.strip() == f"""alias letmedoit='{target}'""":
        print("creating alias ...")
        def addAliasToLoginProfile(profile, content):
            if os.path.isfile(profile):
                content = f"\r\n{content}" if config.thisPlatform == "Windows" else f"\n{content}"
            try:
                with open(profile, "a", encoding="utf-8") as fileObj:
                    fileObj.write(content)
            except:
                pass
        home = os.path.expanduser("~")
        if config.thisPlatform == "Windows":
            """# command prompt
            profile = os.path.join(home, "AutoRun.bat")
            content = f'''doskey {alias}="{target}"'''
            addAliasToLoginProfile(profile, content)
            # powershell
            profile = os.path.join(home, "Documents", "WindowsPowerShell", "Microsoft.PowerShell_profile.ps1")
            content = f'''Set-Alias -Name {alias} -Value "{target}"'''
            addAliasToLoginProfile(profile, content)"""
            pass
        else:
            content = f"""alias {alias}='{target}'"""
            try:
                for profile in (".bash_profile", ".zprofile", ".bashrc", ".zshrc"):
                    addAliasToLoginProfile(os.path.join(home, profile), content)
                print(content)
            except:
                pass