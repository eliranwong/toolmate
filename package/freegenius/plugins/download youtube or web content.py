# install binary ffmpeg and python package yt-dlp to work with this plugin

"""
FreeGenius AI Plugin - download youtube or web content

* download Youtube video
* download Youtube audio and convert it into mp3
* download webcontent

[FUNCTION_CALL]
"""

from freegenius import config, showErrors, isCommandInstalled, print1, print3
import re, subprocess, os
from freegenius.utils.shared_utils import SharedUtil
from pathlib import Path


def download_web_content(function_args):
    def is_youtube_url(url_string):
        pattern = r'(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:watch\?v=|embed\/|v\/)?([a-zA-Z0-9\-_]+)'
        match = re.match(pattern, url_string)
        return match is not None

    def isFfmpegInstalled():
        ffmpegVersion = subprocess.Popen("ffmpeg -version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = ffmpegVersion.communicate()
        return False if stderr else True

    def terminalDownloadYoutubeFile(downloadCommand, url_string, outputFolder):
        if isFfmpegInstalled():
            try:
                print1("--------------------")
                # use os.system, as it displays download status ...
                os.system("cd {2}; {0} {1}".format(downloadCommand, url_string, outputFolder))
                if isCommandInstalled("pkill"):
                    os.system("pkill yt-dlp")
                print3(f"Downloaded in: '{outputFolder}'")
                try:
                    os.system(f'''{config.open} {outputFolder}''')
                except:
                    pass
            except:
                showErrors() 
        else:
            print1("Tool 'ffmpeg' is not found on your system!")
            print1("Read https://github.com/eliranwong/letmedoit/wiki/Install-ffmpeg")


    url = function_args.get("url") # required
    if is_youtube_url(url):
        print1("Loading youtube downloader ...")
        format = function_args.get("format") # required
        location = function_args.get("location", "") # optional
        if not (location and os.path.isdir(location)):
            location = os.path.join(config.localStorage, "audio" if format == "audio" else "video")
            Path(location).mkdir(parents=True, exist_ok=True)
        downloadCommand = "yt-dlp -x --audio-format mp3" if format == "audio" else "yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
        terminalDownloadYoutubeFile(downloadCommand, url, location)
        return "Finished! Youtube downloader closed!"
    elif SharedUtil.is_valid_url(url):
        try:
            folder = config.localStorage
            folder = os.path.join(folder, "Downloads")
            Path(folder).mkdir(parents=True, exist_ok=True)
            SharedUtil.downloadWebContent(url, folder=folder, ignoreKind=True)
            return "Downloaded!"
        except:
            showErrors()
            return "[INVALID]"
    else:
        print1("invalid link given")
        return "[INVALID]"

functionSignature = {
    "examples": [
        "download Youtube video",
        "download Youtube audio into mp3 format",
        "download webpage",
    ],
    "name": "download_web_content",
    "description": "download Youtube video into mp4 file or download audio into mp3 file or download webcontent",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Youtube url given by user",
            },
            "format": {
                "type": "string",
                "description": "Media format to be downloaded. Return 'video' if not given.",
                "enum": ["video", "audio"],
            },
            "location": {
                "type": "string",
                "description": "Output folder where downloaded file is to be saved",
            },
        },
        "required": ["url", "format"],
    },
}

config.addFunctionCall(signature=functionSignature, method=download_web_content)