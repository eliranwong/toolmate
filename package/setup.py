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
    name=package,
    version="0.6.20",
    python_requires=">=3.8, <3.13",
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
        f"{package}.macOS_service",
        f"{package}.macOS_service.ToolMate_Files_workflow",
        f"{package}.macOS_service.ToolMate_Files_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Files_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Text_workflow",
        f"{package}.macOS_service.ToolMate_Text_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Text_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Summary_workflow",
        f"{package}.macOS_service.ToolMate_Summary_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Summary_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Translation_workflow",
        f"{package}.macOS_service.ToolMate_Translation_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Translation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Explanation_workflow",
        f"{package}.macOS_service.ToolMate_Explanation_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Explanation_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Pronounce_workflow",
        f"{package}.macOS_service.ToolMate_Pronounce_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Pronounce_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow",
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow.Contents",
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow.Contents.QuickLook",
        f"{package}.macOS_service.ToolMate_Download_workflow",
        f"{package}.macOS_service.ToolMate_Download_workflow.Contents",
        f"{package}.macOS_service.ToolMate_Download_workflow.Contents.QuickLook",
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
        f"{package}.macOS_service": ["*.*"],
        f"{package}.macOS_service.ToolMate_Files_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Files_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Files_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Text_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Text_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Text_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Summary_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Summary_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Summary_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Translation_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Translation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Translation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Explanation_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Explanation_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Explanation_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Pronounce_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Pronounce_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Pronounce_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_YoutubeMP3_workflow.Contents.QuickLook": ["*.*"],
        f"{package}.macOS_service.ToolMate_Download_workflow": ["*.*"],
        f"{package}.macOS_service.ToolMate_Download_workflow.Contents": ["*.*"],
        f"{package}.macOS_service.ToolMate_Download_workflow.Contents.QuickLook": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    extras_require={
        #"autogen[autobuild]==0.5.2" requires 'chromadb', 'huggingface-hub', 'sentence-transformers', 'pysqlite3-binary'?
        'linux': ["flaml[automl]", "piper-tts", "pysqlite3"],  # Dependencies for the linux module
        'cpp': ["llama-cpp-python[server]==0.3.0", "stable-diffusion-cpp-python"],  # Dependencies for cpp libraries
        'gui': ["PySide6"],  # Dependencies for the gui module
        'bible': ["uniquebible>=0.2.16", "searchbible>=0.1.6"],  # Dependencies for the bible module
    },
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
            f"tmsetup={package}.setup:main", # setup
            f"{package}lite={package}.main:lite",
            f"letmedoit={package}.main:letmedoit",
            f"{package}server={package}.api_server:main",
            f"tmserver={package}.api_server:main", # a shortcut of toolmateserver
            f"{package}client={package}.api_client:main",
            f"tm={package}.api_client:main", # essentially `tmclient`
            f"tmc={package}.api_client:chat", # practically equal to `tmclient -c` or `tm -c`
            f"tmcmd={package}.api_client:cmd", # practically equal to `tmclient -dt command` or `tm -dt command`
            f"tmtask={package}.api_client:task", # practically equal to `tmclient -dt task` or `tm -dt task`
            f"tmpython={package}.api_client:python",
            f"tmonline={package}.api_client:online",
            f"tmgoogle={package}.api_client:google",
            f"tmmp3={package}.api_client:mp3",
            f"tmmp4={package}.api_client:mp4",
            f"tmproxy={package}.api_client:proxy",
            f"tmgroup={package}.api_client:group",
            f"tmagents={package}.api_client:agents",
            f"tmcaptain={package}.api_client:captain",
            f"tmremember={package}.api_client:remember",
            f"tmrecall={package}.api_client:recall",
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
            f"{package}ai={package}.ToolMateAI:main",
            f"toolserver={package}.servers:main",
            f"chatserver={package}.servers:chat",
            f"visionserver={package}.servers:vision",
            f"customtoolserver={package}.servers:custommain",
            f"customchatserver={package}.servers:customchat",
            f"customvisionserver={package}.servers:customvision",
            #f"{package}gui={package}.qt:main",
            f"commandprompt={package}.commandprompt:main",
            f"etextedit={package}.eTextEdit:main",
            f"rag={package}.rag:main",
            f"autoassist={package}.autoassist:main",
            f"autoretrieve={package}.autoretrieve:main",
            #f"automath={package}.automath:main",
            f"autobuild={package}.autobuild:main",
            f"autocaptain={package}.autocaptain:main",
            f"geminipro={package}.geminipro:main",
            f"geminiprovision={package}.geminiprovision:main",
            f"palm2={package}.palm2:main",
            f"codey={package}.codey:main",
            f"groqchat={package}.groqchat:main",
            f"mistralchat={package}.mistralchat:main",
            f"chatgpt={package}.chatgpt:main",
            f"llamapython={package}.llamacpp:main",
            f"llamaserver={package}.llamacppserver:main",
            f"ollamachat={package}.ollamachat:main",
            #f"gemma2b={package}.ollamachat:gemma2b",
            #f"gemma7b={package}.ollamachat:gemma7b",
            #f"llava={package}.ollamachat:llava",
            #f"phi3={package}.ollamachat:phi3",
            #f"vicuna={package}.ollamachat:vicuna",
            #f"starlinglm={package}.ollamachat:starlinglm",
            #f"orca2={package}.ollamachat:orca2",
            #f"wizardlm2={package}.ollamachat:wizardlm2",
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
