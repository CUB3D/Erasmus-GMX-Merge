#!/usr/bin/python

import curses
import os
import time
import subprocess

screen = None
yCoord = 0


# Start utility functions

def init():
    global screen
    screen = curses.initscr()
    # disable key printing
    curses.noecho()
    screen.nodelay(1)
    screen.keypad(1)
    # Enable colours
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)


def safeQuit(exitCode=0):
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    exit(exitCode)


def resetScreen():
    """
    Yes this is hacky, no this isn't recommended or remotely portable, but it works
    """
    subprocess.call(["stty", "sane"])


def putString(string):
    global yCoord
    putString_Impl(0, yCoord, string)
    yCoord += 1


def putString_Impl(x, y, string, colour=0):
    screen.addstr(y, x, string, curses.color_pair(colour))
    screen.refresh()


def drawProgressBar(x, y, percentage, char="#"):
    putString_Impl(x, y, "[")
    for segment in range(1, int(percentage / 10) + 1):
        putString_Impl(x + segment, y, char)
    putString_Impl(int(x + 11), y, "]")
    putString_Impl(x+13, y, str(percentage) + "%")


# End utility functions


def getMergeCases(startDir):
    dirs = [file for file in os.listdir(startDir) if file.endswith(".gmx")]
    return dirs


def printMergeCases(startDir):
    for case in getMergeCases(startDir):
        putString("-" + case)


def putStatusLines(startDir, startY=3):
    for x in range(len(getMergeCases(startDir))):
        putString_Impl(30, startY + x, "[PENDING]", 3)


def checkProjects(projectDir):
    putString("Checking for project files")
    mergeCases = getMergeCases(projectDir)
    for x in range(len(mergeCases)):
        case = mergeCases[x]
        drawProgressBar(30 + len("[PENDING]") + 1, 3 + x, 0)
        expectedProjectName = case.split(".")[-2] + ".project.gmx"
        if os.path.exists(os.path.join(projectDir, case, expectedProjectName)):
            drawProgressBar(30 + len("[PENDING]") + 1, 3, 10)
        else:
            putString_Impl(30, 3, "[FAIL]               ", 1)
            filePath = os.path.join(projectDir, case, expectedProjectName)
            putString("[Failure cause] " + case + " - File not found " + filePath)
            return False
        drawProgressBar(30 + len("[PENDING]") + 1, 3 + x, 100)
    return True


def runProjectTest(func, directory):
    tempYCoord = yCoord
    if func(directory):
        putString_Impl(30, tempYCoord, "[PASSED]", 2)
    else:
        putString_Impl(30, tempYCoord, "[FAILED]", 1)
        waitForAnyKey()


def waitForAnyKey():
    global screen
    putString("Press any key to continue...")
    screen.nodelay(0)
    screen.getch()
    screen.nodelay(1)

init()
putString("Starting compilation")
putString("")
putString("Merging the following directories:")
printMergeCases("./Worlds")
putString("")
putString("Outputting to:")
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

for i in range(5):
    putString_Impl(2*i, yCoord, str(5 - i) + " ", )
    screen.refresh()
    time.sleep(1)
yCoord += 1

putString("Starting merge")

resetScreen()
subprocess.call(["python", "./Threaded Merge.py", "./Worlds/"])
