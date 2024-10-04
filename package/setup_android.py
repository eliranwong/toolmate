from setuptools import setup
from setuptools.command.install import install
import os, shutil, platform, sys

# package name
package_name_0 = os.path.join("package_name.txt")
with open(package_name_0, "r", encoding="utf-8") as fileObj:
    package = fileObj.read()
package_name_1 = os.path.join(package, "package_name.txt") # package readme
shutil.copy(package_name_0, package_name_1)

# delete old shortcut files
apps = {
    "freegenius": ("FreeGenius", "FreeGenius AI"),
    "toolmate": ("ToolMate", "ToolMate AI"),
    "toolmateai": ("ToolMate", "ToolMate AI"),
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
    name="toolmate_android",
    version="0.3.78",
    python_requires=">=3.8, <3.12",
    description=f"ToolMate AI, developed by Eliran Wong, is a cutting-edge AI companion that seamlessly integrates agents, tools, and plugins to excel in conversations, generative work, and task execution. Supports custom workflow and plugins to automate multi-step actions.",
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
        f"{package}.docs",
        f"{package}.help",
        f"{package}.utils",
        f"{package}.gui",
    ],
    package_data={
        package: ["*.*"],
        f"{package}.audio": ["*.*"],
        f"{package}.files": ["*.*"],
        f"{package}.history": ["*.*"],
        f"{package}.icons": ["*.*"],
        f"{package}.plugins": ["*.*"],
        f"{package}.temp": ["*.*"],
        f"{package}.docs": ["*.*"],
        f"{package}.help": ["*.*"],
        f"{package}.utils": ["*.*"],
        f"{package}.gui": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"commandprompt={package}.commandprompt:main",
            f"etextedit={package}.eTextEdit:main",
            f"groqchat={package}.groqchat:main",
            f"llamacppserver={package}.llamacppserver:main",
            f"ollamachat={package}.ollamachat:main",
            f"llava={package}.ollamachat:llava",
        ],
    },
    keywords="ai assistant ollama llama llamacpp groq openai chatgpt gemini autogen rag agent stable-diffusion fabric dalle imagen",
    url="https://letmedoit.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/toolmate",
        "Tracker": "https://github.com/eliranwong/toolmate/issues",
        "Documentation": "https://github.com/eliranwong/toolmate/wiki",
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
