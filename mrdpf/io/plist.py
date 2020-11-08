import os
import plistlib
import dataclasses
import json

from datetime import datetime

from dataclasses_json import dataclass_json
from bpylist import archiver
from bpylist.archive_types import DataclassArchiver

@dataclass_json
@dataclasses.dataclass
class UserIdHistoryInfo(DataclassArchiver):
    """Models UserIdHistory PLIST class"""
    userIdKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class DeviceHistoryInfo(DataclassArchiver):
    """Models DeviceHistoryInfo PLIST class"""
    deviceKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class Device(DataclassArchiver):
    """Models Device PLIST class"""
    model: str
    sdkVersion: str
    osBuild: str
    appVersion: str
    timeZoneOffset: str
    osVersion: str
    locale: str
    liveUpdatePackageHash: str
    liveUpdateReleaseLabel: str
    liveUpdateDeploymentKey: str
    osApiLevel: str
    wrapperRuntimeVersion: str
    wrapperSdkVersion: str
    carrierCountry: str
    appNamespace: str
    sdkName: str
    appBuild: str
    wrapperSdkName: str
    screenSize: str
    osName: str
    carrierName: str
    oemName: str

@dataclass_json
@dataclasses.dataclass
class SessionHistoryInfo(DataclassArchiver):
    """Models SessionHistoryInfo PLIST class"""
    sessionIdKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class ClientFolderRedirectionEntity(DataclassArchiver):
    """Models ClientFolderRedirectionEntity PLIST class"""
    readOnly: bool
    path: str
    name: str
    id: str

@dataclass_json
@dataclasses.dataclass
class BookmarkOrderItemEntity(DataclassArchiver):
    """Models BookmarkOrderItemEntity PLIST class"""
    id: str
    children: list

# update archiver so it can process custom types in PLISTs
archiver.update_class_map({ 
    'MSUserIdHistoryInfo': UserIdHistoryInfo,
    'MSDeviceHistoryInfo': DeviceHistoryInfo,
    'MSDevice': Device,
    'MSSessionHistoryInfo' : SessionHistoryInfo,
    'Client.FolderRedirectionEntity' : ClientFolderRedirectionEntity ,
    'BookmarkOrderItemEntity': BookmarkOrderItemEntity })

def _read_plist(path: str, format: plistlib.PlistFormat) -> dict:
    """Helper function. Read a plist from given path using provided format."""
    if not os.path.isfile(path):
        raise ValueError(f'File {path} does not exist')

    with open(path, 'rb') as file:
        return plistlib.load(file, fmt=format, dict_type=dict)

def decode_plist(data: bytes, format: plistlib.PlistFormat = plistlib.FMT_BINARY) -> dict:
    """Decode byte string into dictionary using provided format.
    
    :returns: Parsed PLIST
    :rtye: dict
    """
    return plistlib.loads(data, fmt=format, dict_type=dict)

def read_bplist(path: str) -> dict:
    """Read binary plist from file at path.
    
    :returns: Parsed PLIST
    :rtye: dict
    """
    return _read_plist(path, plistlib.FMT_BINARY)

def read_plist(path: str) -> dict:
    """Read plaintext XML plist from file at path.
    
    :returns: Parsed PLIST
    :rtye: dict
    """
    return _read_plist(path, plistlib.FMT_XML)

def read_nskeyedarchive(data: bytes) -> dict:
    """Decode binary string encoded using NSKeyedArchiver.
    
    :returns: Parsed PLIST
    :rtye: dict
    """
    return archiver.unarchive(data)