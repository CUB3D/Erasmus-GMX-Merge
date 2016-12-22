from Main import performMerge
import os,shutil
from math import *
def MultiMerge(folder):
    """
    Merges mutiple game maker projects together  
    :param Folder: The location of all projects to be merged, must be a single directory
    :return:
    """
    val = os.listdir(folder)#gens a list of all directories in the sub directory
    if len(val):
        storeArray = []
        while len(storeArray) != 1:
            if storeArray != []:
                val = storeArray
            storeArray = []
            num = len(val) % 2
            count = 0
            for arr in range(0,len(val)-num,2):
                local1 = os.path.join(folder,val[arr])
                local2 = os.path.join(folder,val[arr+1])
                output = os.path.join(folder,"Merge_"+str(count))
                print(local1,local2)
                performMerge(local1, local2, output)
                storeArray.append(output) #### this could be any function
                shutil.rmtree(local1)
                shutil.rmtree(local2)
                count += 1
            print(len(storeArray))
            if num:
                local1 = os.path.join(folder, val[-1])
                local2 = os.path.join(folder, storeArray[-1])
                output = os.path.join(folder, "Merge_" + str(count))
                performMerge(local1, local2, output)
                storeArray[-1] = output ####here we would have to change functions again
                count += 1
        os.rename(storeArray[0],os.path.join(folder,"Final"))
    else:
        print("nothing in directory")

MultiMerge("./Examples/")