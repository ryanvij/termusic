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


# Relative path to assets folder, from __file__
ASSETS = Path(__file__).parent / 'assets'
# .ogg, .mp3 and .wav are the currently supported audio formats, and only files with these extensions are extracted from the folder.
audio_formats = ['.ogg', '.wav', '.mp3']
MAX_ROW = 10
tracks = []
CURRENT_PATH = ""
AUDIO_FILES = []
MAX_ROW = 10
_close = False

def extract_audiof(PATH):
    return [os.path.abspath(f) for f in os.scandir(PATH) if f.is_file()
            if os.path.splitext(f)[1] in audio_formats]

def write_file(path):
    
    with open(ASSETS/"termusicpaths.txt", "a+") as f:
        with open(ASSETS/"termusicpaths.txt", "r") as rf:
            c = rf.readlines()
            for pathf in c:
                if pathf.strip("\n") == path:
                    print("Directory is already being tracked.")
                    sys.exit()
                else:
                    continue

        f.write(path+"\n")
        sys.exit()



def initalize():
    global CURRENT_PATH
    parser = argparse.ArgumentParser(prog='termusic')
    parser.add_argument('--track', metavar='PATH', required=False, help="relative path or abspath to playlist dir.")
    arguments = parser.parse_args()

    if arguments.track is None:
        with open(ASSETS/"termusicpaths.txt", "r") as rf:
            if len(rf.readlines()) > 1:
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
            write_file(os.path.abspath(arguments.track))
        else:
            print("ERROR : AUDIO FILES NOT FOUND IN DIRECTORY")
            sys.exit()





def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def draw_select(stdscr, idx, paths):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    stdscr.clear()
    pos = 3
    stdscr.addstr(pos-2, 2, "Select Playlist", curses.color_pair(1))
    for path in paths:
        if paths.index(path) == idx:
            stdscr.addstr(pos, 3, "> " +  path)
        else:
            stdscr.addstr(pos, 3, path)

        pos += 2

def select_playlist(stdscr):

    idx = 0
    paths = []
    with open(ASSETS/"termusicpaths.txt", "r") as pt:
        paths = list(map(lambda x: x.strip("\n"), pt.readlines()))
    draw_select(stdscr, idx, paths)

    key = stdscr.getch()

    while key != 113:
        if key == curses.KEY_DOWN and idx != len(paths) - 1:
            idx += 1
            draw_select(stdscr, idx, paths)
        elif key == curses.KEY_UP and idx != 0:
            idx -= 1
            draw_select(stdscr, idx, paths)
        elif key == curses.KEY_ENTER or key == 10:
            if os.path.exists(paths[idx]):
                return paths[idx]
            
        key = stdscr.getch()


#--------------------------------------------------------------------
# MUSIC
#--------------------------------------------------------------------

def load_playlist(pg, index):
    global _close
    fsong = AUDIO_FILES[pg][index]
    flattened = []
    for i in AUDIO_FILES:
        for j in i:
            flattened.append(j)

    findex = flattened.index(fsong)
    print(flattened[findex:])
    for song in flattened[findex:]:
        mixer.music.load(song)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.5)

#--------------------------------------------------------------------
# UI 
#--------------------------------------------------------------------

def draw_playlist_box(stdscr, page, idx):
    maxy, maxx = stdscr.getmaxyx()
    pos = 3
    playlist_box = curses.newwin(maxy, 30, 0, maxx - 30)
    playlist_box.box()
    playlist_box.addstr(1, 8, f"Tracks - {page + 1}/{len(AUDIO_FILES)}", curses.color_pair(1))


    for af in AUDIO_FILES[page]:
        if AUDIO_FILES[page].index(af) == idx:
            playlist_box.addstr(pos, 2, textwrap.shorten(os.path.basename(af), width=27, placeholder="..."), curses.color_pair(2))
            pos += 1
        else:
            playlist_box.addstr(pos, 2, textwrap.shorten(os.path.basename(af), width=27, placeholder="..."))
            pos += 1

    stdscr.refresh()
    playlist_box.refresh()


def main(stdscr):
    mixer.init()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    global AUDIO_FILES, cpage, cidx, _close
    page = 0
    idx = 0
    
    AUDIO_FILES = list(chunks(extract_audiof(CURRENT_PATH), MAX_ROW))
    draw_playlist_box(stdscr, page, idx)


    key_pressed = stdscr.getch()
    while key_pressed != 113:
        if key_pressed == curses.KEY_DOWN and idx != len(AUDIO_FILES[page]) - 1:
            idx += 1
            draw_playlist_box(stdscr, page, idx)

        if key_pressed == curses.KEY_UP and idx != 0:
            idx -= 1
            draw_playlist_box(stdscr, page, idx)

        if key_pressed == curses.KEY_RIGHT and page != len(AUDIO_FILES) - 1:
            page += 1
            idx = 0
            draw_playlist_box(stdscr, page, idx)

        if key_pressed == curses.KEY_LEFT and page != 0:
            page -= 1
            idx = 0
            draw_playlist_box(stdscr, page, idx)

        if key_pressed == 10:
            music = threading.Thread(target=load_playlist, args=(page, idx,))
            music.start()



        key_pressed = stdscr.getch()









current_path = initalize()
curses.wrapper(main)