from setuptools import setup
import os, shutil

# Notes: Steps to change package name
# 1. change folder name "letmedoit" to <pacakge_name>
# 2. edit package/package_name.txt and change its content to <pacakge_name>
# 3. search for "from letmedoit" and replace with "from <package_name>"

# package name
package_name_0 = os.path.join("package_name.txt")
with open(package_name_0, "r", encoding="utf-8") as fileObj:
    package = fileObj.read()
package_name_1 = os.path.join(package, "package_name.txt") # package readme
shutil.copy(package_name_0, package_name_1)

# delete old shortcut files
apps = {
    "freegenius": ("FreeGenius", "FreeGenius AI"),
}
appName, appFullName = apps[package]
shortcutFiles = (f"{appName}.bat", f"{appName}.command", f"{appName}.desktop")
for shortcutFile in shortcutFiles:
    shortcut = os.path.join(package, shortcutFile)
    if os.path.isfile(shortcut):
        os.remove(shortcut)

# update package readme
latest_readme = os.path.join("..", "README.md") # github repository readme
package_readme = os.path.join(package, "README.md") # package readme
shutil.copy(latest_readme, package_readme)
with open(package_readme, "r", encoding="utf-8") as fileObj:
    long_description = fileObj.read()

# get required packages
install_requires = []
with open(os.path.join(package, "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod:
            install_requires.append(mod)

# make sure config.py is empty
open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=package,
    version="0.0.12",
    python_requires=">=3.8, <3.12",
    description=f"{appFullName}, an advanced AI assistant, leveraging the capabilities of ChatGPT API, Gemini Pro and AutoGen, capable of engaging in conversations, executing codes with auto-healing, and assisting you with a wide range of tasks on your local devices.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@letmedoit.ai",
    packages=[
        package,
        f"{package}.audio",
        f"{package}.files",
        f"{package}.history",
        f"{package}.icons",
        f"{package}.plugins",
        f"{package}.temp",
        f"{package}.utils",
        f"{package}.gui",
        f"{package}.macOS_service",
        f"{package}.macOS_service.LetMeDoIt_Files_workflow",
        f"{package}.macOS_service.LetMeDoIt_Files_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Files_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Text_workflow",
        f"{package}.macOS_service.LetMeDoIt_Text_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Text_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow",
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow",
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow",
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow",
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow",
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow.Contents.QuickLook",
        f"{package}.macOS_service.LetMeDoIt_Download_workflow",
        f"{package}.macOS_service.LetMeDoIt_Download_workflow.Contents",
        f"{package}.macOS_service.LetMeDoIt_Download_workflow.Contents.QuickLook",
    ],
    package_data={
        package: ["*.*"],
        f"{package}.audio": ["*.*"],
        f"{package}.files": ["*.*"],
        f"{package}.history": ["*.*"],
        f"{package}.icons": ["*.*"],
        f"{package}.plugins": ["*.*"],
        f"{package}.temp": ["*.*"],
        f"{package}.utils": ["*.*"],
        f"{package}.gui": ["*.*"],
        f"{package}.macOS_service": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Files_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Files_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Files_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Text_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Text_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Text_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Summary_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Translation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Explanation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Pronounce_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_YoutubeMP3_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Download_workflow": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Download_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.LetMeDoIt_Download_workflow.Contents.QuickLook": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"{package}tray={package}.systemtray:main",
            f"{package}gui={package}.qt:main",
            f"commandprompt={package}.commandprompt:main",
            f"etextedit={package}.eTextEdit:main",
            f"autoassist={package}.autoassist:main",
            f"autoretriever={package}.autoretriever:main",
            f"automath={package}.automath:main",
            f"autobuilder={package}.autobuilder:main",
            f"geminipro={package}.geminipro:main",
            f"geminiprovision={package}.geminiprovision:main",
            f"palm2={package}.palm2:main",
            f"codey={package}.codey:main",
            f"chatgpt={package}.chatgpt:main",
            f"ollamachat={package}.ollamachat:main",
            f"mistral={package}.ollamachat:mistral",
            f"mixtral={package}.ollamachat:mixtral",
            f"llama2={package}.ollamachat:llama2",
            f"llama213b={package}.ollamachat:llama213b",
            f"llama270b={package}.ollamachat:llama270b",
            f"gemma2b={package}.ollamachat:gemma2b",
            f"gemma7b={package}.ollamachat:gemma7b",
            f"llava={package}.ollamachat:llava",
            f"phi={package}.ollamachat:phi",
            f"vicuna={package}.ollamachat:vicuna",
            f"codellama={package}.ollamachat:codellama",
            f"starlinglm={package}.ollamachat:starlinglm",
            f"orca2={package}.ollamachat:orca2",
        ],
    },
    keywords="ai assistant openai chatgpt gemini autogen rag interpreter auto-heal",
    url="https://letmedoit.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/letmedoit",
        "Tracker": "https://github.com/eliranwong/letmedoit/issues",
        "Documentation": "https://github.com/eliranwong/letmedoit/wiki",
        "Funding": "https://www.paypal.me/letmedoitai",
    },
    classifiers=[
        # Reference: https://pypi.org/classifiers/

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
