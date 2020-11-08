#!/usr/bin/env python3

import argparse
import csv
import json
import os
import shutil

from termcolor import colored, cprint
from colorama import init

from mrdpf.core import run_parsers
from mrdpf.io.general import get_supported_files
from mrdpf.io.general import get_matching_glob
from mrdpf.parsers import Parsers
from mrdpf.helpers import DataclassJSONEncoder

header =    r"            _____  _____  _____   __ " + '\n'\
            r"           |  __ \|  __ \|  __ \ / _|" + '\n'\
            r"  _ __ ___ | |__) | |  | | |__) | |_ " + '\n'\
            r" | '_ ` _ \|  _  /| |  | |  ___/|  _|" + '\n'\
            r" | | | | | | | \ \| |__| | |    | |  " + '\n'\
            r" |_| |_| |_|_|  \_\_____/|_|    |_|  " + '\n'

def create_dir(path):
    append = 0
    while os.path.isdir(path):
        append += 1
        path = path + '_' + str(append) if append != 0 else ''

    cprint(f'=> Creating folder {path}', 'green')
    os.mkdir(path)
    return path

def create_file(path, name, extension):
    append = 0
    file_name = os.path.join(path, name + '.' + extension)

    while os.path.isfile(file_name):
        append += 1
        file_name = os.path.join(path, name + '_' + (str(append) if append != 0 else '') + '.' + extension)

    return file_name

def write_data(path, name, extension, data):
    file_name = create_file(path, name, extension)
    if len(data) > 0:
        cprint(f'=> Writing {len(data)} {name} to {file_name}', 'green')
        write_dataclass_list_to_csv(file_name, data)
    else:
        cprint(f'-- No {name} to write', 'cyan')


def write_dataframe(path, name, extension, data):
    file_name = create_file(path, name, extension)

    if len(data) > 0:
        cprint(f'=> Writing {name} to {file_name}', 'green')
        data.to_csv(file_name)
            
    else:
        cprint(f'-- No {name} to write', 'cyan')

def write_dataclass_list_to_csv(path: str, data: list):
    with open(path, 'w', newline='') as file:  
        writer = csv.writer(file, delimiter=',')
        headers_writter = False

        for item in data:
            d = item.to_dict()

            if not headers_writter:
                writer.writerow(d.keys())
                headers_writter = True

            writer.writerow(d.values())

if __name__ == '__main__':
    init()

    cprint(header, 'cyan')
    cprint('Author: Jonathan Holtmann\n', 'cyan')

    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-d', '--dir', help='Directory to search for compatible files')
    input_group.add_argument('-f', '--file', help='File to parse')

    parser.add_argument('-o', '--out', help='Folder to write results to', required=True)

    parser.add_argument('--no-recurse', help='Do not recurse if input option is --dir. Ignored otherwise.', action='store_true')
    parser.add_argument('--clear', help='Clear output directory before writing results (will delete all files below out directory)', action='store_true')

    args = parser.parse_args()

    if not os.path.isdir(args.out):
        parser.error(f'Output directory {args.out} does not exist')

    if args.clear:
        cprint(f'-- Deleting all files and folders in {args.out}', 'red')

        for file_name in os.listdir(args.out):
            file_path = os.path.join(args.out, file_name)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                cprint(f'Failed to delete {file_path} -- {e}: %s', 'red')

    if args.dir is not None:
        cprint(f'-- Given directory "{args.dir}"', 'cyan')

        if not os.path.isdir(args.dir):
            parser.error(f'Directory {args.dir} does not exist')

        files = get_supported_files(args.dir, not args.no_recurse)
    elif args.file is not None:
        cprint(f'Given file "{args.file}"', 'cyan')

        if not os.path.isdir(args.file):
            parser.error(f'File {args.file} does not exist')

        parser = get_matching_glob(args.file)

        if parser:
            files = { parser: [args.file] }
        else:
            parser.error(f'File {args.file} is not supported by mrdpf')
    
    cprint(f'++ Got {sum([len(data) for data in files.values()])} files to parse using {len(files)} parsers', 'cyan')

    results = run_parsers(files)

    cprint(f'=> Got results from {len(results)} parsers', 'green')

    write_log = list()

    for parser in results.keys():
        cprint(f'++ Processing results from parser {parser}', 'cyan')

        if parser == Parsers.PREFERENCES_PLIST:
            append = 0
            for result in results[parser]:
                file_name = create_file(args.out, 'preferences_plist', 'json')

                cprint(f'=> Writing file {file_name}', 'green')

                with open(file_name, 'w') as out_file:
                    json.dump(result.data.preferences, out_file, cls=DataclassJSONEncoder, indent=4)
                    write_log.append([str(result.path), parser, file_name, ''])
        elif parser == Parsers.APP_SUPPORT_DB:
            for result in results[parser]:
                # dump tables
                folder_name = create_dir(os.path.join(args.out, 'DB_DUMP'))
                cprint(f'=> Dumping app support database to folder {folder_name}', 'green')
                dump_paths = result.data.dump_tables(folder_name)
                write_log.append([str(result.path), parser, folder_name, 'Database Dump Folder'])
                [write_log.append([str(dump_path), parser, folder_name, 'Database Table']) for dump_path in dump_paths]

                # dump no-wal tables
                if result.data.wal:
                    folder_name = create_dir(os.path.join(args.out, 'DB_DUMP_IGNORE_WAL'))
                    cprint(f'=> Dumping app support database (ignoring wal) to folder {folder_name}', 'green')
                    dump_paths = result.data.dump_tables_nw(folder_name)
                    write_log.append([str(result.path), parser, folder_name, 'Database Dump Folder'])
                    [write_log.append([str(dump_path), parser, folder_name, 'Database Table']) for dump_path in dump_paths] 
                
                file_name = create_file(args.out, 'bookmarks', 'csv')
                if len(result.data.bookmarks) > 0:
                    cprint(f'=> Writing {len(result.data.bookmarks)} bookmarks to {file_name}', 'green')
                    write_dataclass_list_to_csv(file_name, result.data.bookmarks)
                else:
                    cprint('-- No bookmarks to write', 'cyan')

                write_data(args.out, 'metadata', 'csv', result.data.metadata)
                write_data(args.out, 'bookmark_order', 'csv', result.data.bookmark_order)
        elif parser == Parsers.OFFLINE_STORAGE:
            for result in results[parser]:
                write_dataframe(args.out, 'offline_storage', 'csv', result.data.parameters)
                
                
    headers = ['Input File', 'Parsed Using', 'Parsed To', 'Extra Information']

    with open(os.path.join(args.out, 'write_log.csv'), 'w', newline='') as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for line in write_log:
            writer.writerow(line)
    
    cprint(f'=> Wrote "write_log.csv" to {args.out}', 'green')
    cprint(f'== Done', 'cyan')