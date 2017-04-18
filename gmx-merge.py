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
    stdscr.nodelay(1)
    stdscr.keypad(1)
    # Enable colours
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
 

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
        putString_Impl(30, startY + x, "[PENDING]", 3)

def checkProjects(projectDir):
    putString("Checking for project files")
    mergeCases = getMergeCases(projectDir)
    for i in range(len(mergeCases)):
        dir = mergeCases[i]
        drawProgressBar(30 + len("[PENDING]") + 1, 3 + i, 0) 
        expectedProjectName = dir.split(".")[-2]+".project.gmx"
        if os.path.exists(os.path.join(projectDir, dir, expectedProjectName)):
            drawProgressBar(30 + len("[PENDING]") + 1, 3, 10)
        else:
            putString_Impl(30, 3, "[FAIL]               ", 1)
            putString("[Failure cause] " + dir + " - File not found " + os.path.join(projectDir, dir, expectedProjectName))
            return False
        drawProgressBar(30 + len("[PENDING]") + 1, 3 + i, 100) 
    return True

def runProjectTest(func, dir):
    tempYCoord = yCoord
    if(func(dir)):
        putString_Impl(30, tempYCoord, "[PASSED]", 2)
    else:
        putString_Impl(30, tempYCoord, "[FAILED]", 1)
        waitForAnyKey()

def waitForAnyKey():
    global stdscr
    putString("Press any key to continue...")
    stdscr.nodelay(0)
    stdscr.getch()
    stdscr.nodelay(1)

init()
putString("Starting compilation")
putString("")
putString("Merging the following directories:")
printMergeCases("./Worlds")
putString("")
putString("Outputing to:")
putString("-Final.gmx")
putString_Impl(30, yCoord - 1, "[PENDING]", 1)
putStatusLines("./Worlds")
waitForAnyKey()
yCoord -= 1
putString(" " * 80)
putString("Checking projects...")
runProjectTest(checkProjects, "./Worlds")
putString("Starting project merge in 5 seconds")
putString("Press Ctrl-C to cancel")
from time import sleep
for i in range(5):
    putString_Impl(2*i, yCoord, str(5 - i) + " ", )
    stdscr.refresh()
    sleep(1)
yCoord += 1

putString("Starting merge")
from subprocess import call
call(["stty", "sane"])
call(["python", "./Threaded Merge.py", "./Worlds/"])
