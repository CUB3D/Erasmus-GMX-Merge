#!/usr/bin/python

import curses
import os

stdscr = None
yCoord = 0

def init():
    global stdscr
    stdscr = curses.initscr()
    # disable key printing
    curses.noecho()
    stdscr.keypad(1)
    # Enable colours
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

 

def quit(i=0):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    exit(i)

def putString(str):
    global yCoord
    putString_Impl(0, yCoord, str)
    yCoord += 1

def putString_Impl(x, y, str, colour=0):
    stdscr.addstr(y, x, str, curses.color_pair(colour))
    stdscr.refresh()

def getMergeCases(startDir):
    dirs = [file for file in os.listdir(startDir) if file.endswith(".gmx")]
    return dirs

def drawProgressBar(x, y, percentage, char="#"):
    putString_Impl(x, y, "[")
    for i in range(1, int(percentage / 10) + 1):
        putString_Impl(x + i, y, char)
    putString_Impl(int(x + 11), y, "]")
    putString_Impl(x+13, y, str(percentage) + "%") 

def printMergeCases(startDir):
    for i in getMergeCases(startDir):
        putString("-"+i)

def putStatusLines(startDir, startY=3):
    for x in range(len(getMergeCases(startDir))):
        putString_Impl(30, startY + x, "[PENDING]", 1)

def checkProjects(projectDir):
    for dir in getMergeCases(projectDir):
        drawProgressBar(30 + len("[PENDING]") + 1, 3, 0) 
        expectedProjectName = dir.split(".")[-2]+".project.gmx"
        putString(expectedProjectName + " - " + str(os.path.exists(os.path.join(projectDir, dir, expectedProjectName))))
        if os.path.exists(os.path.join(projectDir, dir, expectedProjectName)):
            drawProgressBar(30 + len("[PENDING]") + 1, 3, 10)


init()
putString("Starting compilation")
putString("")
putString("Merging the following directories:")
printMergeCases("./Worlds")
putString("")
putString("Outputing to:")
putString("-Final.gmx")
putString_Impl(30, yCoord - 1, "[PENDING]", 1)
putString("")
putStatusLines("./Worlds")
putString("Checking projects...")

checkProjects("./Worlds")
import time
time.sleep(3)
quit(0)
