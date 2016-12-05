from pprint import pprint
from xmlstuff import XMLParser
from gamemaker import *
import os
def getXmlDict(file):
    xmlDict = XMLParser(file)
    #pprint(xmlDict)
    return xmlDict

def recursiveFileLoading(child, project, ending):
    """
    Recursively scans a child node to find the names of all items in the tree
    :param child: The element in the tree that acts as a directory
    :param project: the project instance
    :param ending: The file ending of that project file (e.g. ".object.gmx" for object files)
    :return: A list containing the names of all items in the tree
    """
    # Note this function ignores the actual names of the subdirectories which be needed later when the new project is
    # built (Unless we are just going to ignore them and create a folder for each project's files)
    tempStorage = []
    for baby in child["children"]:
        path = project.expandPath(baby["content"]) + ending
        print("Loading: ", path)
        if len(child["children"]) > 0:
            tempStorage.extend(recursiveFileLoading(baby, project, ending))
        tempStorage.append(getXmlDict(path))
    return tempStorage

def loadConfigFiles(project):
    """
    Loads the data from the config files into the project
    :param project: The project object
    """
    for child in project["Configs"]["children"]:
        configPath = project.expandPath(child["content"]) + ".config.gmx" # expands the path
        print("Loading path:", configPath)
        project.configs.append(getXmlDict(configPath)) #appends all the returned config files in the directory

def loadObjectFiles(project):
    """
    Loads the data from the object files into the project
    :param project: The project object
    """
    for child in project["objects"]["children"]:
        configPath = project.expandPath(child["content"]) + ".object.gmx"
        #If the object has children then it has no "useful" content (all whitespace)
        if len(child["children"]) > 0:
            #recursivly scan for objects
            print("Found subdir: " + child["attributes"][0][1])
            project.objects.extend(recursiveFileLoading(child, project, ".object.gmx"))
        else:
            print("Loading path:", configPath)
            project.objects.append(getXmlDict(configPath))


def loadScriptFiles(project):
    """
    Loads the data from the scripts into a list of script objects in the project
    :param project: The project object
    """
    for child in project["scripts"]["children"]:
        configPath = project.expandPath(child["content"]) + ".gml"
        print("Loading path:", configPath)
        project.scripts.append(Script(child["content"], project))

def loadRoomFiles(project):
    """
    Loads the data from the room files into the project
    :param project: The project object
    """
    for child in project["rooms"]["children"]:
        configPath = project.expandPath(child["content"]) + ".room.gmx"
        print("Loading path:", configPath)
        project.rooms.append(getXmlDict(configPath))

def loadSpriteFiles(project):
    """
    Loads sprite data from the sprite files into the project
    :param project: The project object
    """
    for child in project["sprites"]["children"]:
        configPath = project.expandPath(child["content"]) + ".sprite.gmx"
        print("Loading path:", configPath)
        project.sprites.append(getXmlDict(configPath))

def checkCollision(projects):
    """
    Checks through all catagories in the checkCases list to see if there are any copies in all projects in the projects list
    :param projects: A list of project objects
    """
    checkCases = ["objectNames","roomNames","scriptNames","spriteNames"]#A list of all the different element types we will be searching for
    collisionList = [] #A list to notate all naming collisions using "collision at [projectName] [case] [level]
    passList = []#a list to store all non collisions so all the data can be accessed so it doesnt have to be searched again
    for case in checkCases:#iterate through all the cases
        caseAspects = [] #a list of all the different elements by name, specific to the type 
        for project in projects: #iterate through all the projects
            for level in project.resolutionTable[case]: #go through all elements of the resolution table of the current project using the current case
                if level not in caseAspects:#check if the level is the the list of stored elements
                    caseAspects.append(level)#if not append
                    passList.append([project.projectName,case,level])
                else: #else join the collision to a table to be printed at the end
                    collisionList.append([project.projectName,case,level])
    for x in collisionList:#output all collisions
        print("collision at",x[0] + ":",x[1],x[2])#returns all name collisions
    return collisionList,passList

def nameChanger(collisionList,passList):
    """
    A method to use the names of the collision and then simply rename them using the common structure of the game maker profile
    :param collisionList: a list of all collisions inside the profiles
    :param passList: a list to of all the elements that didnt collide but simply need to be moved to the correct position.
    """
    #NOTE could be able to remove the passList function but change around the order so that the folder structure creation
    #NOTE takes place first then as the file is being copied it is renamed.
    for name in collisionList:#change all values in the resolution table that collide
        pass

def createFolderStructure(projects,startDir):
    """
    A method to generate the folder structure in a new directory
    :param projects: a list of all the different gameMakerProject types
    :param startDir: a location for the new merged project to be located
    """
    cases = ["Configs","objects","Output","rooms","script","sprites"]
    print("Making start directory")
    os.makedirs(startDir)
    for case in cases:
        print("Making",case,"directory")
        os.makedirs(startDir +"/"+case)
        
def parseProjectData(file):
    """
    Loads the data from the project into a project object and builds
    resolution tables from this data
    :param file: The path to the root diretory in the project
    """
    project = gameMakerProject(file)#Create an instance of the game maker project type using the passed file location as the root
    project.project = getXmlDict(project.expandPath(project.projectName + ".project.gmx")) #concatanate ".project.gmx" using the Expand path function and then parse it using the XML parser from XMLstuff
    print("Loading and parsing config")
    loadConfigFiles(project)#call config load
    print("Loading object files")
    loadObjectFiles(project)
    print("Parsing scripts")
    loadScriptFiles(project)
    print("Loading room data")
    loadRoomFiles(project)
    print("Loading sprite data")
    loadSpriteFiles(project)
    project.buildResolutionTable()
    return project

project1 = parseProjectData("./Examples/Erasmus.gmx")#Start using the file Erasmus in the example
project2 = parseProjectData("./Examples/FireWorldScales.gmx")#throws error as not finding file
checkCollision([project1,project2])
createFolderStructure([project1,project2],"./Examples/Merge")
input()#hang
