import subprocess, re, sys

def installmodule(module, update=True):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"

    isInstalled, _ = subprocess.Popen("pip -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    pipInstallCommand = f"{sys.executable} -m pip install"

    if isInstalled:

        if update:
            from freegenius import config
            if not config.pipIsUpdated:
                pipFailedUpdated = "pip tool failed to be updated!"
                try:
                    # Update pip tool in case it is too old
                    updatePip = subprocess.Popen(f"{pipInstallCommand} --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    *_, stderr = updatePip.communicate()
                    if not stderr:
                        print("pip tool updated!")
                    else:
                        print(pipFailedUpdated)
                except:
                    print(pipFailedUpdated)
                config.pipIsUpdated = True
        try:
            upgrade = (module.startswith("-U ") or module.startswith("--upgrade "))
            if upgrade:
                moduleName = re.sub("^[^ ]+? (.+?)$", r"\1", module)
            else:
                moduleName = module
            print(f"{'Upgrading' if upgrade else 'Installing'} '{moduleName}' ...")
            installNewModule = subprocess.Popen(f"{pipInstallCommand} {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = installNewModule.communicate()
            if not stderr:
                print(f"Package '{moduleName}' {'upgraded' if upgrade else 'installed'}!")
            else:
                print(f"Failed {'upgrading' if upgrade else 'installing'} package '{moduleName}'!")
                if config.developer:
                    print(stderr)
            return True
        except:
            return False

    else:

        print("pip command is not found!")
        return False

