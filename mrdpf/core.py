import os
from dataclasses import dataclass

from mrdpf.parsers import Parsers
from mrdpf.parsers import PreferencesPlistParser
from mrdpf.parsers import AppSupportDbParser

@dataclass
class ParsedResult(object):
    path: str
    data: object

def run_parsers(files: dict) -> dict:
    ret = dict()

    for key in files.keys():
        if type(key) != Parsers:
            raise TypeError(f'Unsupported key type {type(key)}, requires type=Parser')
            
        for file in files[key]:
            if key == Parsers.PREFERENCES_PLIST:
                parser = PreferencesPlistParser(file)
            elif key == Parsers.APP_SUPPORT_DB:
                parser = AppSupportDbParser(file)
            else:
                continue

            val = parser.parse()

            if val is not None:
                if key not in ret:
                    ret[key] = list()
                
                ret[key].append(ParsedResult(file, val))

    return ret