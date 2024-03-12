import os, glob


class FileUtil:

    @staticmethod
    # Note: pathlib.Path(file).stem does not work with file name containg more than one dot, e.g. "*.db.sqlite"
    def fileNamesWithoutExtension(dir, ext):
        files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
        return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])