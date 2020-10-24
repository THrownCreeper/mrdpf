from pathlib import Path
from mrdpf.parsers import Parsers

class SupportedFile(object):
    path = ""
    parser = ""

    def __init__(self, path, parser):
        self.path = path
        self.parser = parser

_supported_globs =   [
                        SupportedFile('com.microsoft.rdc.application-data.sqlite', Parsers.APP_SUPPORT_DB),
                        SupportedFile('com.microsoft.rdc.macos.plist', Parsers.PREFERENCES_PLIST)
                    ]

def get_supported_files(path, recurse=False):
    files = dict()

    for supported_file in _supported_globs:
        for file in Path(path).rglob(supported_file.path) if recurse else Path(path).glob(supported_file.path):
            if supported_file.parser not in files:
                files[supported_file.parser] = list()
            
            files[supported_file.parser].append(file)
    
    return files

def get_matching_glob(file):
    for supported_file in _supported_globs:
        if supported_file.path == file:
            return supported_file.parser
    return None