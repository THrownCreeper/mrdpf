from base64 import b64encode
import copy
import time
import tempfile
import os
import sqlite3
import shutil
from typing import Optional
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

import bpylist
import pandas as pd
from dataclasses_json import dataclass_json

from mrdpf.io.plist import read_bplist
from mrdpf.io.plist import read_nskeyedarchive
from mrdpf.io.plist import UserIdHistoryInfo
from mrdpf.io.plist import ClientFolderRedirectionEntity

class Parsers(Enum):
    PREFERENCES_PLIST = 1
    APP_SUPPORT_DB = 2

class BaseParser(object):
    parser_type = None

    def __init__(self, paser_type):
        self.paser_type = paser_type
    
    def parse(self):
        pass

@dataclass_json
@dataclass
class Preferences(object):
    telemetry_previous_send_diagnostics: bool
    nswindow_frame_mainwindow: str
    kms_analytics_is_enabled: bool
    removed_home_folder_redirection: bool
    telemetry_previous_daily_events_time: datetime
    user_id_history: dict()
    past_devices_key: dict()
    first_run_experience_launched_version: str
    telemetry_device_id: str
    ms_install_id: str
    telemetry_previous_app_launch_version: str
    session_id_history: dict()

    def get_headers(self):
        return [
            'TelemetryPreviousSendDiagnostics',
            'NSWindow Frame MainWindow',
            'kMSAnalyticsIsEnabledKey',
            'Developer.removedHomeFolderRedirection',
            'TelemetryPreviousDailyEventsTimeKey',
            'UserIdHistory',
            'pastDevicesKey',
            'ClientSettings.FirstRunExperienceLaunchedVersion',
            'TelemetryDeviceId',
            'MSInstallId',
            'TelemetryPreviousAppLaunchVersion',
            'SessionIdHistory'
        ]

    def to_list(self):
        return [
            self.telemetry_previous_send_diagnostics,
            self.nswindow_frame_mainwindow,
            self.kms_analytics_is_enabled,
            self.removed_home_folder_redirection,
            self.telemetry_previous_daily_events_time,
            self.user_id_history,
            self.first_run_experience_launched_version,
            self.past_devices_key
        ]

@dataclass_json
@dataclass
class Bookmark(object):
    pk: str
    ent: str
    opt: str
    friendly_name: str
    hostname: str
    zid: str
    rdp_string: str
    folder_redirection_config: ClientFolderRedirectionEntity
    last_connected: datetime
    redirect_camera: bool
    redirect_folders: bool
    redirect_clipboard: bool
    redirect_printers: bool
    redirect_smartcard: bool
    bookmark_folder: int
    fok_bookmark_folder: int
    credential: int
    gateway: int
    creation_source: str
    authoring_tool: str
    admin_mode: bool
    audio_capture_enabled: bool
    audio_playback: str
    auto_reconnect_enabled: bool
    color_depth: int
    dynamic_resolution_enabled: bool
    retina_enabled: bool
    input_mode: str
    use_all_monitors: bool
    screen_type: str
    screen_type_height: int
    screen_type_width: int
    screen_type_resolution: int
    screen_type_scale: bool
    swap_mouse_button: bool
    

class PreferencesPlistParser(BaseParser):
    path: str
    preferences: Preferences
    data: dict()

    def __init__(self, path):
        super().__init__(Parsers.PREFERENCES_PLIST)
        self.path = path

    def parse(self) -> Preferences:
        
        self.data = read_bplist(self.path)

        past_devices_key = read_nskeyedarchive(self.data['pastDevicesKey'])
        for device in past_devices_key:
            device.timestampKey = datetime.fromtimestamp(device.timestampKey).strftime('%Y-%m-%d %H:%M:%S.%f')

        user_id_history = read_nskeyedarchive(self.data['UserIdHistory'])
        for user in user_id_history:
            user.timestampKey = datetime.fromtimestamp(user.timestampKey).strftime('%Y-%m-%d %H:%M:%S.%f')

        session_id_history = read_nskeyedarchive(self.data['SessionIdHistory']) if 'SessionIdHistory' in self.data else dict()
        for session in session_id_history:
            session.timestampKey = datetime.fromtimestamp(session.timestampKey).strftime('%Y-%m-%d %H:%M:%S.%f')

        telemetry_previous_daily_events_time = self.data['TelemetryPreviousDailyEventsTimeKey'] if 'TelemetryPreviousDailyEventsTimeKey' in self.data else None
        if telemetry_previous_daily_events_time:
            telemetry_previous_daily_events_time = datetime.fromtimestamp(telemetry_previous_daily_events_time).strftime('%Y-%m-%d %H:%M:%S.%f')

        self.preferences = Preferences(
            self.data['TelemetryPreviousSendDiagnostics'],
            self.data['NSWindow Frame MainWindow'],
            self.data['kMSAnalyticsIsEnabledKey'],
            self.data['Developer.removedHomeFolderRedirection'],
            telemetry_previous_daily_events_time,
            user_id_history,
            past_devices_key,
            self.data['ClientSettings.FirstRunExperienceLaunchedVersion'],
            b64encode(self.data['TelemetryDeviceId']).decode('UTF8'),
            self.data['MSInstallId'],
            self.data['TelemetryPreviousAppLaunchVersion'],
            session_id_history
        )

        return self

class AppSupportDbParser(BaseParser):
    path = ''
    _tmp_path = ''
    tables: list = list()
    tables_nw: list = list()
    wal: bool = False
    bookmarks: list = list()

    def __init__(self, path):
        super().__init__(Parsers.PREFERENCES_PLIST)
        self.path = path

    def parse(self):
        tmp_dir = tempfile.TemporaryDirectory()

        # copy main sqlite database
        self._tmp_path = shutil.copy(self.path, tmp_dir.name)

        # dump all data from tables
        self.tables_nw = self._get_tables()

        # copy over shm and wal if they exist and re-prase
        wal_path = str(self.path) + '-wal'
        if os.path.isfile(wal_path):
            shutil.copy(wal_path, tmp_dir.name)
            self.wal = True

        shm_path = str(self.path) + '-shm'
        if os.path.isfile(shm_path):
            shutil.copy(shm_path, tmp_dir.name)
            self.wal = True

        # read data again if a WAL file was present
        
        self.tables = self._get_tables() if self.wal else self.tables_nw
        self._process_tables(self.tables)
        
        return self
    
    def _process_tables(self, tables: list):
        for (name, table) in tables:
            for (_, row) in table.iterrows():
                if 'ZBOOKMARKENTITY' == name:
                    self.bookmarks.append(self._make_bookmark(row))

    def _make_bookmark(self, row):
        folder_redirection = row['ZFOLDERREDIRECTIONCOLLECTION']
        if folder_redirection:
            parsed_folder_redirection = read_nskeyedarchive(folder_redirection)

        last_connection = row['ZLASTCONNECTED']
        if last_connection:
            parsed_last_connection = datetime.fromtimestamp(read_nskeyedarchive(last_connection)).strftime('%Y-%m-%d %H:%M:%S.%f')

        return Bookmark(row['Z_PK'],
                        row['Z_ENT'],
                        row['Z_OPT'],
                        row['ZFRIENDLYNAME'],
                        row['ZHOSTNAME'],
                        row['ZID'],
                        row['ZRDPSTRING'],
                        parsed_folder_redirection if folder_redirection else None,
                        parsed_last_connection if last_connection else None,
                        row['ZCAMERAREDIRECTIONENABLED'],
                        row['ZFOLDERREDIRECTIONENABLED'],
                        row['ZPASTEBOARDREDIRECTIONENABLED'],
                        row['ZPRINTERREDIRECTIONENABLED'],
                        row['ZSMARTCARDREDIRECTIONENABLED'],
                        row['ZBOOKMARKFOLDER'],
                        row['Z_FOK_BOOKMARKFOLDER'],
                        row['ZCREDENTIAL'],
                        row['ZGATEWAY'],
                        row['ZCREATIONSOURCEENUM'],
                        row['ZAUTHORINGTOOL'],
                        row['ZADMINMODE'],
                        row['ZAUDIOCAPTUREENABLED'],
                        row['ZAUDIOPLAYBACKENUM'],
                        row['ZAUTORECONNECTENABLED'],
                        row['ZCOLORDEPTHENUM'],
                        row['ZDYNAMICRESOLUTIONENABLED'],
                        row['ZENABLERETINA'],
                        row['ZINPUTMODEENUM'],
                        row['ZSCREENTYPEALLMONITORS'],
                        row['ZSCREENTYPEENUMTYPE'],
                        row['ZSCREENTYPEHEIGHT'],
                        row['ZSCREENTYPEWIDTH'],
                        row['ZSCREENTYPERESOLUTIONTYPE'],
                        row['ZSCREENTYPESCALE'],
                        row['ZSWAPMOUSEBUTTON'])

    def _get_tables(self):
        conn = sqlite3.connect(self._tmp_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = cursor.fetchall()

        tables = list()
        for table_name in table_names:
            table_name = table_name[0]
            table = pd.read_sql_query(f"SELECT * from {table_name}" , conn)
            tables.append([table_name, table])
        
        cursor.close()
        conn.close()

        return tables

    def dump_tables(self, path: str) -> list:
        return self._dump_tables(path, self.tables)

    def dump_tables_nw(self, path: str) -> list:
        return self._dump_tables(path, self.tables_nw)

    def _dump_tables(self, path: str, tables: list) -> list:
        paths = list()
        for table in tables:
            file_path = os.path.join(path, table[0] + '.csv')
            table[1].to_csv(file_path, index_label='index')
            paths.append(file_path)

        return paths