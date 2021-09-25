import curses
import os
from pathlib import Path
import textwrap

ASSETS = Path(__file__).parent / 'assets'

def draw_playlist_box(stdscr, page, idx, AUDIO_FILES):
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
    with open(ASSETS/"paths.txt", "r") as pt:
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
    os._exit(0)