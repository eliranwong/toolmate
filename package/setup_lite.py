from setuptools import setup
import os, shutil

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
with open(os.path.join(package, "requirements_lite.txt"), "r") as fileObj:
    for line in fileObj.readlines():
        mod = line.strip()
        if mod:
            install_requires.append(mod)

# make sure config.py is empty
open(os.path.join(package, "config.py"), "w").close()

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name="toolmate_lite",
    version="0.6.20",
    python_requires=">=3.8, <3.13",
    description=f"ToolMate AI, developed by Eliran Wong, is a cutting-edge AI companion that seamlessly integrates agents, tools, and plugins to excel in conversations, generative work, and task execution. Supports custom workflow and plugins to automate multi-step actions.",
    long_description='''# ToolMate AI Lite

This is the lite version of ToolMate AI https://pypi.org/project/toolmate/

This `Lite` version supports running on Android Termux as well as on Windows / macOS / Linux / ChromeOS

'''+long_description,
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
    extras_require={
        'bible': ["uniquebible>=0.2.16"],  # Dependencies for the bible module
    },
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"tmsetup={package}.setup:main", # setup
            f"{package}server={package}.api_server:main", # api server
            f"tmserver={package}.api_server:main", # a shortcut of toolmateserver
            f"{package}client={package}.api_client:main", # api client
            f"tm={package}.api_client:main", # essentially `tmclient`
            f"tmc={package}.api_client:chat", # practically equal to `tmclient -c` or `tm -c`
            f"tmcmd={package}.api_client:cmd", # practically equal to `tmclient -dt command` or `tm -dt command`
            f"tmtask={package}.api_client:task", # practically equal to `tmclient -dt task` or `tm -dt task`
            f"tmpython={package}.api_client:python",
            f"tminternet={package}.api_client:internet",
            f"tmgoogle={package}.api_client:google",
            f"tmmp3={package}.api_client:mp3",
            f"tmmp4={package}.api_client:mp4",
            f"tmr={package}.api_client:reflection",
            f"tmdr={package}.api_client:deepReflection",
            f"tmt1={package}.api_client:tmt1",
            f"tmt2={package}.api_client:tmt2",
            f"tmt3={package}.api_client:tmt3",
            f"tmt4={package}.api_client:tmt4",
            f"tmt5={package}.api_client:tmt5",
            f"tmt6={package}.api_client:tmt6",
            f"tmt7={package}.api_client:tmt7",
            f"tmt8={package}.api_client:tmt8",
            f"tmt9={package}.api_client:tmt9",
            f"tmt10={package}.api_client:tmt10",
            f"tmt11={package}.api_client:tmt11",
            f"tmt12={package}.api_client:tmt12",
            f"tmt13={package}.api_client:tmt13",
            f"tmt14={package}.api_client:tmt14",
            f"tmt15={package}.api_client:tmt15",
            f"tmt16={package}.api_client:tmt16",
            f"tmt17={package}.api_client:tmt17",
            f"tmt18={package}.api_client:tmt18",
            f"tmt19={package}.api_client:tmt19",
            f"tmt20={package}.api_client:tmt20",
            f"tms1={package}.api_client:tms1",
            f"tms2={package}.api_client:tms2",
            f"tms3={package}.api_client:tms3",
            f"tms4={package}.api_client:tms4",
            f"tms5={package}.api_client:tms5",
            f"tms6={package}.api_client:tms6",
            f"tms7={package}.api_client:tms7",
            f"tms8={package}.api_client:tms8",
            f"tms9={package}.api_client:tms9",
            f"tms10={package}.api_client:tms10",
            f"tms11={package}.api_client:tms11",
            f"tms12={package}.api_client:tms12",
            f"tms13={package}.api_client:tms13",
            f"tms14={package}.api_client:tms14",
            f"tms15={package}.api_client:tms15",
            f"tms16={package}.api_client:tms16",
            f"tms17={package}.api_client:tms17",
            f"tms18={package}.api_client:tms18",
            f"tms19={package}.api_client:tms19",
            f"tms20={package}.api_client:tms20",
            f"tmconfigs={package}.api_client:configs",
            f"commandprompt={package}.commandprompt:main",
            f"etextedit={package}.eTextEdit:main",
            f"groqchat={package}.groqchat:main",
            f"mistralchat={package}.mistralchat:main",
            f"chatgpt={package}.chatgpt:main",
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
        'Programming Language :: Python :: 3.12',
    ],
)
