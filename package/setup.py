from setuptools import setup
import os, shutil

# package name
package = "freegenius"

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

# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/
setup(
    name=package,
    version="0.0.06",
    python_requires=">=3.8",
    description="FreeGenius AI, a FREE, LOCAL, OFFLINE & HIGHLY CUSTOMIZABLE AI suite that supports numerous open-source LLMs, with optional integration with AutoGen agents, OpenAI API, Google Gemini Pro and unlimited plugins.",
    long_description=long_description,
    author="Eliran Wong",
    author_email="support@letmedoit.ai",
    packages=[
        package,
        f"{package}.configs",
        f"{package}.core",
        f"{package}.plugins",
        f"{package}.temp",
        f"{package}.ui",
        f"{package}.utils",
    ],
    package_data={
        package: ["*.*"],
        f"{package}.configs": ["*.*"],
        f"{package}.core": ["*.*"],
        f"{package}.plugins": ["*.*"],
        f"{package}.temp": ["*.*"],
        f"{package}.ui": ["*.*"],
        f"{package}.utils": ["*.*"],
    },
    license="GNU General Public License (GPL)",
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            f"{package}={package}.main:main",
        ],
    },
    keywords="ai open llm ollama gpt mistral llama",
    url="https://letmedoit.ai",
    project_urls={
        "Source": "https://github.com/eliranwong/freegenius",
        "Tracker": "https://github.com/eliranwong/freegenius/issues",
        "Documentation": "https://github.com/eliranwong/freegenius/wiki",
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
