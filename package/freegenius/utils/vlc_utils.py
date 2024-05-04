from freegenius import config, getHideOutputSuffix
import os, sys, re, platform, subprocess, shutil

class VlcUtil:

    macVlc = windowsVlc = ""

    @staticmethod
    def isVlcPlayerInstalled():
        # on macOS
        macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
        VlcUtil.macVlc = macVlc if platform.system() == "Darwin" and os.path.isfile(macVlc) else ""
        # on Windows
        windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
        if platform.system() == "Windows":
            if os.path.isfile(windowsVlc):
                VlcUtil.windowsVlc = windowsVlc
            elif shutil.which("vlc"):
                # Windows users can install vlc command with scoop
                # read: https://github.com/ScoopInstaller/Scoop
                # instll scoop
                # > iwr -useb get.scoop.sh | iex
                # > scoop install aria2
                # install vlc
                # > scoop bucket add extras
                # > scoop install vlc
                VlcUtil.windowsVlc = "vlc"
            else:
                VlcUtil.windowsVlc = ""
        if (VlcUtil.macVlc or VlcUtil.windowsVlc or shutil.which("vlc")):
            return True
        else:
            return False

    @staticmethod
    def openVlcPlayer():
        def run(command):
            os.system("{0}{1}{2} &".format("nohup " if shutil.which("nohup") else "", command, getHideOutputSuffix()))
        VlcUtil.closeVlcPlayer()
        try:
            if VlcUtil.windowsVlc:
                os.system(VlcUtil.windowsVlc)
            elif VlcUtil.macVlc:
                run(VlcUtil.macVlc)
            elif shutil.which("vlc"):
                run("vlc")
        except:
            print("No VLC player is found!")

    @staticmethod
    def closeVlcPlayer():
        try:
            if platform.system() == "Windows":
                os.system("taskkill /IM vlc.exe /F")
            else:
                os.system("pkill VLC")
                os.system("pkill vlc")
        except:
            pass

    @staticmethod
    def playMediaFile(filePath, vlcSpeed=None, audioGui=False):
        if vlcSpeed is None:
            vlcSpeed = config.vlcSpeed
        # get full path and escape double quote
        if isinstance(filePath, str):
            filePath = os.path.abspath(filePath).replace('"', '\\"')
        else:
            # when filePath is a list
            filePath = [os.path.abspath(i).replace('"', '\\"') for i in filePath]
            filePath = '" "'.join(filePath)
        VlcUtil.playMediaFileVlcGui(filePath, vlcSpeed) if re.search("(.mp4|.avi)$", filePath.lower()[-4:]) or audioGui else VlcUtil.playMediaFileVlcNoGui(filePath, vlcSpeed)

    # play audio file with vlc without gui
    @staticmethod
    def playMediaFileVlcNoGui(filePath, vlcSpeed=None):
        if vlcSpeed is None:
            vlcSpeed = config.vlcSpeed
        # vlc on macOS
        if VlcUtil.macVlc:
            command = f'''{VlcUtil.macVlc} --intf rc --play-and-exit --rate {vlcSpeed} "{filePath}"{getHideOutputSuffix()}'''
        # vlc on windows
        elif VlcUtil.windowsVlc:
            command = f'''"{VlcUtil.windowsVlc}" --intf dummy --play-and-exit --rate {vlcSpeed} "{filePath}"'''
        # vlc on other platforms
        elif shutil.which("cvlc"):
            command = f'''cvlc --play-and-exit --rate {vlcSpeed} "{filePath}"{getHideOutputSuffix()}'''
        # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


    # play video file with vlc with gui
    @staticmethod
    def playMediaFileVlcGui(filePath, vlcSpeed):
        # vlc on macOS
        if VlcUtil.macVlc:
            command = f'''{VlcUtil.macVlc} --play-and-exit --rate {vlcSpeed} "{filePath}"{getHideOutputSuffix()}'''
        # vlc on windows
        elif VlcUtil.windowsVlc:
            command = f'''"{VlcUtil.windowsVlc}" --play-and-exit --rate {vlcSpeed} "{filePath}"'''
        # vlc on other platforms
        elif shutil.which("vlc"):
            command = f'''vlc --play-and-exit --rate {vlcSpeed} "{filePath}"{getHideOutputSuffix()}'''
        # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

if __name__ == '__main__':
    speed = float(sys.argv[1])
    audioFile = " ".join(sys.argv[2:])
    VlcUtil.playMediaFile(audioFile, speed)
    isVlcPlaying = os.path.join("temp", "isVlcPlaying")
    if os.path.isfile(isVlcPlaying):
        os.remove(isVlcPlaying)

