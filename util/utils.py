import errno
import os

from configs import settings
from shutil import copyfile


class FileHandler:
    """
    Use this class to manage files
    """
    def __init__(self, uri: str, mode: str):
        self.file_path = uri
        self.file = None
        self.mode = mode
        self.content = ""

    def read(self):
        """
        Reads the whole file into the content attribute
        """
        self.content = self.file.read()
        return self

    def write(self):
        self.file.write(self.content)
        return self

    def copy_file(self, dst: str):
        self.create_file_tree(dst)
        copyfile(self.file_path, dst)
        return self

    def close(self) -> None:
        self.file.close()

    def open(self):
        self.file = open(self.file_path, self.mode)
        return self

    def create_file_tree(self, path=None):
        """
        * Use this method if you intent to open a file that can bot be already created
        * this method will create the file directory
        * If the path already exists, then this method does nothing
        """
        if path is None:
            path = self.file_path
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        return self

class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def change(color, value):
        return color + str(value) + Bcolors.ENDC


class Mlog:
    @staticmethod
    def DEBUG(*args, **kwargs):
        if getattr(settings, 'LOG_LEVEL', False) == 'DEBUG':
            print('\033[92m DEBUG:', *args, '\033[0m', **kwargs)

    @staticmethod
    def INFO(*args, **kwargs):
        if getattr(settings, 'LOG_LEVEL', False) in ['DEBUG', 'INFO']:
            print('\033[94m INFO:', *args, '\033[0m', **kwargs)

    @staticmethod
    def ERROR(*args, **kwargs):
        if getattr(settings, 'LOG_LEVEL', False) in ['DEBUG', 'INFO', 'ERROR']:
            print('\033[91m ERROR:', *args, '\033[0m', **kwargs)
