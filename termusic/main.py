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
CURRENT_PATH = ""
AUDIO_FILES = []
MAX_ROW = 24
cidx = None
cpage = None
_skip = False
_paused = False
_loop = False
std = None


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


def draw_utils():
    y, x = std.getmaxyx()
    utils = curses.newwin(5, x - 30, 0, 0)
    utils.box()
    if cpage is None and cidx is None:
        pass
    else:
        utils.addstr(2, 10, AUDIO_FILES[cpage][cidx])
        utils.addstr(2, 10, CURRENT_PATH)

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

def draw_playlist_box(stdscr, page, idx):
    maxy, maxx = stdscr.getmaxyx()
    pos = 3
    playlist_box = curses.newwin(maxy, 30, 0, maxx - 30)
    playlist_box.box()
    playlist_box.addstr(1, 8, f"Tracks - {page + 1}/{len(AUDIO_FILES)}", curses.color_pair(1))


    for af in AUDIO_FILES[page]:
        if AUDIO_FILES[page].index(af) == idx:
            playlist_box.addstr(pos, 2, textwrap.shorten(os.path.splitext(os.path.basename(af))[0], width=27, placeholder="..."), curses.color_pair(2))
            pos += 1
        else:
            playlist_box.addstr(pos, 2, textwrap.shorten(os.path.splitext(os.path.basename(af))[0], width=27, placeholder="..."))
            pos += 1

    stdscr.refresh()
    playlist_box.refresh()


def main(stdscr):
    global std
    std = stdscr
    mixer.init()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.clear()
    global AUDIO_FILES, cpage, cidx, _paused, _loop
    page = 0
    idx = 0
    
    AUDIO_FILES = list(chunks(extract_audiof(CURRENT_PATH), MAX_ROW))
    draw_playlist_box(stdscr, page, idx)
    draw_utils()

    music_ = threading.Thread(target=music)
    music_.start()

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
            cpage, cidx = page, idx
            
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

        key_pressed = stdscr.getch()
    os._exit(0)

current_path = initalize()
curses.wrapper(main)




