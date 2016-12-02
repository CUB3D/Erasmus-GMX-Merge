from pprint import pprint
from xmlstuff import XMLParser
from gamemaker import *

def getXmlDict(file):
    xmlDict = XMLParser(file)
    #pprint(xmlDict)
    return xmlDict

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
        if child["name"] != "object":#a quick get around for if the data is split into sub groups
            for Baby in child["children"]:#iterates through all the children of the children
                configPath = project.expandPath(Baby["content"]) + ".object.gmx"
                print("Loading path:", configPath)
        else:
            configPath = project.expandPath(child["content"]) + ".object.gmx"
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
    for case in checkCases:#iterate through all the cases
        caseAspects = [] #a list of all the different elements by name, specific to the type 
        for project in projects: #iterate throug all the projects
            for level in project.resolutionTable[case]: #go through all elements of the resolution table of the current project using the current case
                if level not in caseAspects:#check if the level is the the list of stored elements
                    caseAspects.append(level)#if not append
                else: #else join the collision to a table to be printed at the end
                    collisionList.append("Collision at " + project.projectName + " : " + case + " " + level)
    for x in collisionList:#output all collisions
        print(x)#returns all name collisions
    return collisionList #TODO reformat this to use the correct data structure so it can be evaluated at a later date

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
input()#hang
