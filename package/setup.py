from setuptools import setup
from setuptools.command.install import install
import os, shutil, platform, sys

class PreInstallCommand(install):
    """Pre-installation for installation mode."""
    # setting 'CMAKE_ARGS' for installation of 'llama-cpp-python'
    # read https://github.com/abetlen/llama-cpp-python
    def run(self):
        # https://github.com/abetlen/llama-cpp-python#installation-configuration
        os.system('''$env:CMAKE_ARGS = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"''' if platform.system() == "Windows" else '''CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"''')
        os.environ['CMAKE_ARGS'] = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
        install.run(self)

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
    version="0.2.78",
    python_requires=">=3.8, <3.12",
    description=f"{appFullName}, an advanced AI assistant that can talk and take multi-step actions. Supports numerous open-source LLMs via Llama.cpp or Ollama or Groq Cloud API, with optional integration with AutoGen agents, OpenAI API, Google Gemini Pro and unlimited plugins.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@letmedoit.ai",
    cmdclass={
        'install': PreInstallCommand,
    },
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
        f"{package}.gui": ["*.*"],
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
            f"letmedoit={package}.main:letmedoit",
            f"{package}hub={package}.systemtray:main",
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
            f"autoretriever={package}.autoretriever:main",
            #f"automath={package}.automath:main",
            f"autobuilder={package}.autobuilder:main",
            f"geminipro={package}.geminipro:main",
            f"geminiprovision={package}.geminiprovision:main",
            f"palm2={package}.palm2:main",
            f"codey={package}.codey:main",
            f"groqchat={package}.groqchat:main",
            f"chatgpt={package}.chatgpt:main",
            f"llamacpp={package}.llamacpp:main",
            f"llamacppserver={package}.llamacppserver:main",
            f"ollamachat={package}.ollamachat:main",
            f"mistral={package}.ollamachat:mistral",
            f"mixtral={package}.ollamachat:mixtral",
            f"llama3={package}.ollamachat:llama3",
            f"llama370b={package}.ollamachat:llama370b",
            f"gemma2b={package}.ollamachat:gemma2b",
            f"gemma7b={package}.ollamachat:gemma7b",
            f"llava={package}.ollamachat:llava",
            f"phi3={package}.ollamachat:phi3",
            f"vicuna={package}.ollamachat:vicuna",
            f"codellama={package}.ollamachat:codellama",
            f"starlinglm={package}.ollamachat:starlinglm",
            f"orca2={package}.ollamachat:orca2",
            f"wizardlm2={package}.ollamachat:wizardlm2",
        ],
    },
    keywords="ai assistant ollama llama llamacpp groq openai chatgpt gemini autogen rag agent stable-diffusion",
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
