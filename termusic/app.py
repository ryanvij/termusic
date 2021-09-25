# -*- coding: utf-8 -*-
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import argparse
import curses
import sys
import textwrap
import time
import threading
from pathlib import Path
from pygame import mixer
from utils import extract_audiof, write_file, chunks
from ui import draw_select, select_playlist, draw_playlist_box


# Relative path to assets folder, from __file__
ASSETS = Path(__file__).parent / 'assets'
# .ogg, .mp3 and .wav are the currently supported audio formats, and only files with these extensions are extracted from the folder.
audio_formats = ['.ogg', '.wav', '.mp3']
MAX_ROW = 10
CURRENT_PATH = ""
AUDIO_FILES = []
MAX_ROW = 24
cidx = None
cpage = None
_skip = False
_paused = False
_loop = False
std = None

def initalize():
    global CURRENT_PATH
    parser = argparse.ArgumentParser(prog='termusic')
    parser.add_argument('--track', metavar='PATH', required=False, help="relative path or abspath to playlist dir.")
    arguments = parser.parse_args()

    if arguments.track is None:
        with open(ASSETS/"paths.txt", "r") as rf:
            if len(rf.readlines()) >= 1:
                CURRENT_PATH = curses.wrapper(select_playlist)
                return CURRENT_PATH
        
            else:
                print("Track a directory, before starting the program.")
                sys.exit()





    elif arguments.track.lower() == "cwd":
        if len(extract_audiof(os.getcwd())) > 0:
            write_file(os.getcwd())
        else:
            print("ERROR : AUDIO FILES NOT FOUND IN DIRECTORY")
            sys.exit()
    elif not os.path.exists(os.path.abspath(arguments.track)):
        print("INVALID PATH")
        sys.exit()
    elif os.path.exists(os.path.abspath(arguments.track)):
        if len(extract_audiof(os.path.abspath(arguments.track))) > 0:
            write_file(os.path.abspath(os.path.expanduser(arguments.track)))
        else:
            print("ERROR : AUDIO FILES NOT FOUND IN DIRECTORY")
            sys.exit()


def draw_utils():
    y, x = std.getmaxyx()
    utils = curses.newwin(5, x - 30, 0, 0)
    utils.box()
    uy, ux = utils.getmaxyx()

    if cpage is None and cidx is None:
        pass
    else:
        utils.addstr(2, 5, f"Playing : {os.path.splitext(os.path.basename(AUDIO_FILES[cpage][cidx]))[0]}")

        if _paused:
            utils.addstr(2, ux - 10, "PAUSED")
    utils.refresh()


#--------------------------------------------------------------------
# MUSIC
#--------------------------------------------------------------------

def load_playlist(pg, index):
    global cpage, cidx
    fsong = AUDIO_FILES[pg][index]
    flattened = []
    for i in AUDIO_FILES:
        for j in i:
            flattened.append(j)
    findex = flattened.index(fsong)

    for song in flattened[findex:]:
        for i in AUDIO_FILES:
            for j in i:
                if j == song:
                    cidx = i.index(j)
                    cpage = AUDIO_FILES.index(i)
                    
        mixer.music.load(song)
        mixer.music.play()
        draw_utils()
        
        while mixer.music.get_busy() or _paused:
            if cpage != pg or cidx != index:
                return 0
                
            time.sleep(0.01)
        if _loop:
                return 0

        mixer.music.unload()


    cpage, cidx = 0, 0
    return 0


def music():
    while cpage is None and cidx is None:
        time.sleep(0.1)

    while True:
        load_playlist(cpage, cidx)
        

#--------------------------------------------------------------------
# UI 
#--------------------------------------------------------------------




def main(stdscr):
    global std
    std = stdscr
    mixer.init()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    global AUDIO_FILES, cpage, cidx, _paused, _loop, MAX_ROW
    page = 0
    idx = 0
    
    _, x = stdscr.getmaxyx()
    MAX_ROW = round(x / 5)
    AUDIO_FILES = list(chunks(extract_audiof(CURRENT_PATH), MAX_ROW))
    draw_playlist_box(stdscr, page, idx, AUDIO_FILES)
    draw_utils()

    music_ = threading.Thread(target=music)
    music_.start()

    key_pressed = stdscr.getch()

    try:
        while key_pressed != 113:
            if key_pressed == curses.KEY_DOWN and idx != len(AUDIO_FILES[page]) - 1:
                idx += 1

            if key_pressed == curses.KEY_UP and idx != 0:
                idx -= 1

            if key_pressed == curses.KEY_RIGHT and page != len(AUDIO_FILES) - 1:
                page += 1
                idx = 0

            if key_pressed == curses.KEY_LEFT and page != 0:
                page -= 1
                idx = 0

            if key_pressed == 10:
                cpage, cidx = page, idx
                _paused = False
                
            if key_pressed == ord("p") and not _paused:
                mixer.music.pause()
                _paused = True

            elif key_pressed == ord("p") and _paused:
                mixer.music.unpause()
                _paused = False

            elif key_pressed == ord("s"):
                if cidx == len(AUDIO_FILES[cpage]) - 1:
                    if cpage != len(AUDIO_FILES) - 1:
                        cpage += 1
                        cidx = 0
                    else:
                        cpage, cidx = 0, 0

                else:
                    cidx += 1
                _paused = False


            elif key_pressed == ord("a"):  
                if cpage == 0:
                    if cidx == 0:
                        cpage, cidx = 0, 0
                    else:
                        cidx -= 1

                else:
                    if cidx == 0:
                        cpage -= 1
                        cidx = len(AUDIO_FILES[cpage]) - 1

                    else:
                        cidx -= 1
                _paused = False

            elif key_pressed == ord("w"):
                if mixer.music.get_busy():
                    try:
                        mixer.music.set_pos(0)
                    except:
                        pass

            elif key_pressed == ord("l") and not _loop:
                _loop = True

            elif key_pressed == ord("l") and _loop:
                _loop = False

            draw_utils()
            draw_playlist_box(stdscr, page, idx, AUDIO_FILES)
            key_pressed = stdscr.getch()
    except:
        print("WINDOW RESIZE ERROR")
        os._exit(0)

    os._exit(0)

current_path = initalize()
curses.wrapper(main)
