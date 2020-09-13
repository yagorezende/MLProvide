from . import settings
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
