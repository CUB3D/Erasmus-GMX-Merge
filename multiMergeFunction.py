from math import *

def ArraySum(arr):#calc sum array
    return arr[0] +arr[1]

###############TEST##################################
x= 20
val = []
for x in range(1,2**x + 1):
    val.append(x)

print(len(val))

#######Useable function##########
storeArray = []
for x in range(0,int(log(len(val),2))):
    if storeArray != []:
        val = storeArray
    storeArray = []
    num = len(val) % 2
    for arr in range(0,len(val)-num,2):
        newArray = [val[arr],val[arr+1]]#create new array with values
        storeArray.append(ArraySum(newArray)) #### this could be any function
    print(len(storeArray))#shows shortening
    if num:
        storeArray[-1] = ArraySum([val[-1],storeArray[-1]])####here we would have to change functions again

####outputs value#####
print(storeArray)
