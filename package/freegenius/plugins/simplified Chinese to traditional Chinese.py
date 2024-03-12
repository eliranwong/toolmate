"""
LetMeDoIt AI Plugin - convert simplified Chinese into traditional Chinese

Convert simplified Chinese into traditional Chinese in text output
"""

try:
    from opencc import OpenCC
except:
    from freegenius.utils.install import installmodule
    installmodule(f"--upgrade opencc")

from freegenius import config
from opencc import OpenCC

def convertToTraditionalChinese(text):
    if text:
        return OpenCC('s2t').convert(text)
    else:
        return text

config.outputTransformers.append(convertToTraditionalChinese)