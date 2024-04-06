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
long_description = f'''# Android Version
This is a mini version of LetMeDoIt AI, created for running on Android Termux Application.

Read moare at: https://github.com/eliranwong/letmedoit/wiki/Android-Support

Install package "letmedoit" instead for full features on Windows / macOS / Linux / ChromeOS

Read more at: https://github.com/eliranwong/letmedoit/wiki/Installation

{long_description}'''

# get required packages
install_requires = []
exclude_packages = (
    "torch==2.2.1",
    "torchvision==0.17.1",
    "google-cloud-aiplatform==1.42.1",
    "google-cloud-speech",
    "google-cloud-texttospeech",
    "pygame",
    "pyautogen[retrievechat,autobuild,mathchat]==0.2.14",
    "unstructured[all-docs]",
    "chromadb",
    "docker",
    "rembg",
    "numpy",
    "seaborn[stats]",
    "sentence-transformers",
    "PySide6",
    "PyMuPDF",
    "yfinance",
    "openai-whisper",
)
with open(os.path.join(package, "requirements.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod and not mod in exclude_packages:
            install_requires.append(mod)

# make sure config.py is empty
open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=f"{package}_android",
    version="0.0.99",
    python_requires=">=3.8, <3.12",
    description=f"{appFullName}, an advanced AI assistant that can talk and take multi-step actions. Supports numerous open-source LLMs via Llama.cpp or Ollama, with optional integration with AutoGen agents, OpenAI API, Google Gemini Pro and unlimited plugins.",
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
        f"{package}.macOS_service",
        f"{package}.macOS_service.FreeGenius_Files_workflow",
        f"{package}.macOS_service.FreeGenius_Files_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Files_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Text_workflow",
        f"{package}.macOS_service.FreeGenius_Text_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Text_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Summary_workflow",
        f"{package}.macOS_service.FreeGenius_Summary_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Summary_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Translation_workflow",
        f"{package}.macOS_service.FreeGenius_Translation_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Translation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Explanation_workflow",
        f"{package}.macOS_service.FreeGenius_Explanation_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Explanation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow",
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow",
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow.Contents.QuickLook",
        f"{package}.macOS_service.FreeGenius_Download_workflow",
        f"{package}.macOS_service.FreeGenius_Download_workflow.Contents",
        f"{package}.macOS_service.FreeGenius_Download_workflow.Contents.QuickLook",
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
        f"{package}.macOS_service": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Files_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Files_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Files_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Text_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Text_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Text_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Summary_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Summary_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Summary_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Translation_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Translation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Translation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Explanation_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Explanation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Explanation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Pronounce_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_YoutubeMP3_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Download_workflow": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Download_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.FreeGenius_Download_workflow.Contents.QuickLook": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"commandprompt={package}.commandprompt:main",
            f"etextedit={package}.eTextEdit:main",
            f"chatgpt={package}.chatgpt:main",
        ],
    },
    keywords="ai assistant ollama llama llamacpp openai chatgpt gemini autogen rag agent",
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
