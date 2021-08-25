# -*- coding: utf-8 -*-
import os
import argparse
import string
import curses
from loguru import logger
import sys
import time
from pathlib import Path
from pygame import mixer

ASSETS = Path(__file__).parent / 'assets'
audio_formats = ['.ogg', '.wav', '.mp3']


def extract_audiof(PATH):
    return [os.path.abspath(f) for f in os.scandir(PATH) if f.is_file()
            if os.path.splitext(f)[1] in audio_formats]


def initalize():
    parser = argparse.ArgumentParser(prog='termusic')
    parser.add_argument('--track', metavar='PATH', required=False)
    arguments = parser.parse_args()

    if arguments.track is None:
        if os.path.exists(ASSETS / 'termusicpaths.txt'):
            with open(ASSETS / 'termusicpaths.txt', 'r') as f:
                if len(f.readlines()) == 0:
                    print('Track a directory, by using the --track argument before starting the music player.')
                    sys.exit()
        else:
            print('Track a directory, by using the --track argument before starting the music player.')
            sys.exit()
    else:
        if os.path.isdir(arguments.track):
            if len(extract_audiof(arguments.track)) > 0:
                if os.path.exists(ASSETS / 'termusicpaths.txt'):
                    with open(ASSETS / 'termusicpaths.txt', 'r') as f:
                        for path in f.readlines():
                            if path.strip('\n') == arguments.track:
                                print('Directory is already being tracked.')
                                sys.exit()

                    with open(ASSETS / 'termusicpaths.txt', 'a+') as f:
                        f.write(arguments.track)
                        f.write('\n')
            else:
                print('NO AUDIO FILES FOUND!')
                sys.exit()

    tracked_dirs = []
    with open(ASSETS / 'termusicpaths.txt', 'r') as f:
        for path in f.readlines():
            tracked_dirs.append(path.strip('\n'))

    return tracked_dirs




mixer.init()
logger.add('termusic.log',format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}')

def main(stdscr):
   pass

curses.wrapper(main)