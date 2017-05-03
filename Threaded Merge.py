from Main import performMerge
import os,shutil
from math import *
from tempfile import mkdtemp
from threading import Thread
from utils import fixPaths

from random import randint


class MergeThread(Thread):
    project1 = ""
    project2 = ""
    output = ""
    force = False
    done = False

    def __init__(self, project1, project2, force, ExitDir):
        super(MergeThread, self).__init__()
        self.project1 = project1
        self.project2 = project2
        self.output = genTempFile(ExitDir)
        self.force = force

    def run(self):
        performMerge(self.project1, self.project2, self.output, self.force)
        self.done = True


def genTempFile(ExitDir):
    name = os.path.join(ExitDir, "./TEMP/temp") + str(randint(1000, 99999999))
    os.makedirs(name)
    return name


def MultiMerge(folder, force=False):
    """
    Merges multiple game maker projects together
    :param folder: The location of all projects to be merged, must be a single directory
    :param force: If true then directories will be overwritten without asking permission
    """
    if os.path.exists(os.path.join(folder, "Final.gmx")):
        print("Output exists, removing")
        shutil.rmtree(os.path.join(folder, "Final.gmx"))

    # gens a list of all directories in the sub directory
    val = [file for file in os.listdir(folder) if file.endswith(".gmx")]

    if len(val):
        threadPool = []
        storeArray = []

        while len(storeArray) != 1:
            if storeArray:
                val = storeArray
            storeArray = []
            num = len(val) % 2
            count = 0

            for arr in range(0, len(val)-num, 2):
                local1 = os.path.join(folder, val[arr])
                local2 = os.path.join(folder, val[arr+1])
                mergeThread = MergeThread(local1, local2, force, folder)
                threadPool.append(mergeThread)
                print(local1, local2)
                mergeThread.start()
                print("Merge done")
                # this could be any function
                storeArray.append(mergeThread.output.split("./")[-1])
                # shutil.rmtree(local1)
                # shutil.rmtree(local2)
                count += 1
            # wait for all merges to finish on this level
            while True:
                allDone = True
                for thread in threadPool:
                    if not thread.done:
                        allDone = False
                if allDone:
                    break
            threadPool.clear()
            if num:
                local1 = os.path.join(folder, val[-1])
                local2 = os.path.join(folder, storeArray[-1])
                output = mkdtemp()
                performMerge(local1, local2, output, force)
                storeArray[-1] = output
                count += 1
        shutil.move(os.path.join(folder, storeArray[0]), os.path.join(folder, "Final.gmx"))
        fixPaths(os.path.join(folder, "Final.gmx"))
        renamedFile = storeArray[0].split("/")
        originalName = os.path.join(folder, "Final.gmx", renamedFile[-1] + ".project.gmx")
        newName = os.path.join(folder, "Final.gmx", "Final.project.gmx")
        os.rename(originalName, newName)
        print("Copied Completely You can find the final project in", os.path.join(folder, "Final/Final.project.gmx"))
    else:
        print("nothing in directory")

MultiMerge("./worlds-build/", True)
