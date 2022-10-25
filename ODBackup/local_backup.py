
"""
Skript zur lokalen, inkrementellen Sicherung gespeicherter Daten eines lokalen Ordners.
"""

import configparser
import os
import time
from cmd import Cmd
from re import match
from datetime import datetime, timedelta
from shutil import copy, copytree

cp = configparser.ConfigParser()
cp.read(r'config.ini')

src_dir = cp.get('Paths', 'source_path')
dst_dir = cp.get('Paths', 'target_path')

missing_files = []

class CLI(Cmd):
    intro = f'- - - A u t o m a t i c   B a c k u p   S o f t w a r e - - -\nType help or ? to list all commands.'
    prompt = '(bckup) '

    def do_dirs(self, arg):
        'Prints the current source and destination directory.\n'
        print(src_dir + ' -> ' + dst_dir + '\n')

    def do_src(self, arg):
        'Sets the source directory for the backup process and saves it for future uses.\n'
        global src_dir
        if match('^(.+)\:([^\/.]+)$', arg):
            src_dir = arg
            with open('config.ini', 'r') as reader:
                content = reader.readlines()
                content[1] = f'source_path: {src_dir}\n'
                with open('config.ini', 'w') as writer:
                    writer.writelines(content)
        else:
            print(f'{arg} is not a valid directory.')
            print(r'EXAMPLE -> set_src C:\Users\User\Documents' + '\n')

    def do_dst(self, arg):
        'Sets the destination directory for the backup process and saves it for future uses.\n'
        global dst_dir
        if match('^(.+)\:([^\/.]+)$', arg):
            dst_dir = arg
            with open('config.ini', 'r') as reader:
                content = reader.readlines()
                content[2] = f'target_path: {dst_dir}\n'
                with open('config.ini', 'w') as writer:
                    writer.writelines(content)
        else:
            print(f'{arg} is not a valid directory.')
            print(r'EXAMPLE -> set_dst D:\Backup\Documents' + '\n')

    def do_files(self, arg):
        'Prints all outdated files (missing or changed) to the console.\n'
        print_missing_files()

    def do_start(self, arg):
        'Starts the backup process. Takes an optional argument to set a timer.\n'
        compare_dirs()
        if missing_files:
            if arg:
                try:
                    timer = int(arg)
                    print(f"The backup process will start at {datetime.now().replace(microsecond=0)  + timedelta(seconds=timer)}\n")
                    time.sleep(timer)
                    back_up_changes()
                except ValueError:
                    print('The given argument for the timer has to be a number.\n')
            else:
                back_up_changes()
    
    def do_clear(self, arg):
        'Clears the Console.\n'
        os.system('cls')
    
    def do_quit(self, arg):
        'Quits the Application.\n'
        return True

def compare_dirs(src_path=None) -> None :
    missing_files.clear()

    if not src_path:
        src_path = src_dir
    
    dst_path = src_path.replace(src_dir, dst_dir)

    for file in os.listdir(src_path):
        src_file = f'{src_path}\\{file}'
        dst_file = f'{dst_path}\\{file}'

        if file in os.listdir(dst_path):
            if os.path.isdir(src_file):
                compare_dirs(src_file)
            elif os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                missing_files.append(src_file)
            continue
        else:
            missing_files.append(src_file)

def print_missing_files() -> None :
    compare_dirs()
    if missing_files:
        print(f'Currently {len(missing_files)} files are outdated:')
        for file in missing_files:
            print(file)
    else:
        print('All files are up to date.')
    print()

def back_up_changes() -> None :
    print_missing_files()
    if missing_files:
        for path in missing_files:
            dst = path.replace(src_dir, dst_dir)
            if os.path.isdir(path):
                copytree(path, dst)
            else:
                copy(path, dst)
        missing_files.clear()
    print('Backup done!\n')

if __name__ == '__main__': 
    os.system('cls')
    CLI().cmdloop()
