from pprint import pprint
from xmlstuff import XMLParser
from gamemaker import *

def getXmlDict(file):
    xmlDict = XMLParser(file)
    #pprint(xmlDict)
    return xmlDict

def recursiveFileLoading(child, project, ending):
    tempStorage = []
    for baby in child["children"]:
        print("BBY: " + baby)
        path = project.expandPath(baby["content"]) + ending
        if "children" in baby:
            tempStorage.extend(recursiveFileLoading(baby, ending))
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
        print("Loading path:", configPath)
        project.objects.append(getXmlDict(configPath))
        #Check for subdirs
        if "children" in child:
            #recursivly scan for objects
            project.objects.extend(recursiveFileLoading(child, project, ".object.gmx"))

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
input()#hang
