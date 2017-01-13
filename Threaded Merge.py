from Main import performMerge
import os,shutil
from math import *
from tempfile import mkdtemp
from threading import Thread

from random import randint

class MergeThread(Thread):
    project1 = ""
    project2 = ""
    output = ""
    force = False
    done = False

    def genTempFile(self,ExitDir):
        name = os.path.join(ExitDir,"/TEMP/temp") + str(randint(1000, 99999999))
        os.makedirs(name)
        return name
        
        

    def __init__(self, project1, project2, force,ExitDir):
        super(MergeThread, self).__init__()
        self.project1 = project1
        self.project2 = project2
        self.output = self.genTempFile(ExitDir)#mkdtemp()
        self.force = force

    def run(self):
        performMerge(self.project1, self.project2, self.output, self.force)
        self.done = True

def MultiMerge(folder, force=False):
    """
    Merges multiple game maker projects together
    :param folder: The location of all projects to be merged, must be a single directory
    :param force: If true then directories will be overwritten without asking permission
    """
    val = os.listdir(folder)#gens a list of all directories in the sub directory
    if len(val):
        threadPool = []
        storeArray = []
        while len(storeArray) != 1:
            if storeArray != []:
                val = storeArray
            storeArray = []
            num = len(val) % 2
            count = 0
            for arr in range(0, len(val)-num, 2):
                local1 = os.path.join(folder, val[arr])
                local2 = os.path.join(folder, val[arr+1])
                mergeThread = MergeThread(local1, local2, force,folder)
                threadPool.append(mergeThread)
                print(local1, local2)
                mergeThread.start()
                print("Merge done")
                storeArray.append(mergeThread.output) #this could be any function
                #shutil.rmtree(local1)
                #shutil.rmtree(local2)
                count += 1
            #wait for all merges to finish on this level
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
                storeArray[-1] = output #here we would have to change functions again
                count += 1
        shutil.move(storeArray[0], os.path.join(folder, "Final"))
        renamedFile = storeArray[0].split("/")
        os.rename(os.path.join(folder,"Final",renamedFile[-1]+".project.gmx"),os.path.join(folder,"Final/Final.project.gmx"))
        print("Copied Completely You can find the final project in",os.path.join(folder,"Final/Final.project.gmx"))
    else:
        print("nothing in directory")

MultiMerge("./Examples/", True)
