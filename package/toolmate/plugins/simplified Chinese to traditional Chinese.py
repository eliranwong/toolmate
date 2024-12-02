"""
ToolMate AI Plugin - convert simplified Chinese into traditional Chinese

Convert simplified Chinese into traditional Chinese in text output
"""

try:
    from opencc import OpenCC
except:
    from toolmate import installPipPackage
    installPipPackage(f"--upgrade opencc-python-reimplemented")

from toolmate import config
from opencc import OpenCC

def convertToTraditionalChinese(text):
    if text:
        return OpenCC('s2t').convert(text)
    else:
        return text

config.outputTextConverters.append(convertToTraditionalChinese)