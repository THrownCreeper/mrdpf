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
    userIdKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class DeviceHistoryInfo(DataclassArchiver):
    deviceKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class Device(DataclassArchiver):
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
    sessionIdKey: str
    timestampKey: str

@dataclass_json
@dataclasses.dataclass
class ClientFolderRedirectionEntity(DataclassArchiver):
    readOnly: bool
    path: str
    name: str
    id: str

@dataclass_json
@dataclasses.dataclass
class BookmarkOrderItemEntity(DataclassArchiver):
    id: str
    children: list

archiver.update_class_map({ 
    'MSUserIdHistoryInfo': UserIdHistoryInfo,
    'MSDeviceHistoryInfo': DeviceHistoryInfo,
    'MSDevice': Device,
    'MSSessionHistoryInfo' : SessionHistoryInfo,
    'Client.FolderRedirectionEntity' : ClientFolderRedirectionEntity ,
    'BookmarkOrderItemEntity': BookmarkOrderItemEntity })

def _read_plist(path: str, format: plistlib.PlistFormat) -> dict:
    if not os.path.isfile(path):
        raise ValueError(f'File {path} does not exist')

    with open(path, 'rb') as file:
        return plistlib.load(file, fmt=format, dict_type=dict)

def decode_plist(data: bytes, format: plistlib.PlistFormat = plistlib.FMT_BINARY):
    return plistlib.loads(data, fmt=format, dict_type=dict)

def read_bplist(path: str) -> dict:
    return _read_plist(path, plistlib.FMT_BINARY)

def read_plist(path: str) -> dict:
    return _read_plist(path, plistlib.FMT_XML)

def read_nskeyedarchive(data: bytes) -> dict:
    return archiver.unarchive(data)