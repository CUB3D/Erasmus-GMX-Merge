from pprint import pprint
import os
from xmlstuff import XMLParser

class Script:
    #The name of the script
    name = ""
    #The content of the script
    content = []

    def __init__(self, path, project):
        self.name = "".join(path.split("\\")[-1:]).replace(".gml", "")
        with open(project.expandPath(path), "r") as handle:
            self.content = handle.readlines()

class gamemakerProject:
    #The path to the root of the project (The file with the project.gmx in it)
    rootPath = ""
    #The name of the project
    projectName = ""
    #The project main project data stored in the name.project.gmx file
    project = []
    #The list of all configs in the project
    configs = []
    #List of all of the objects in the project
    objects = []
    #List of all of the scripts in the project
    scripts = []
    #List of all of the rooms in the project
    rooms = []
    #List of all of the sprites in the project
    sprites = []

    def __init__(self, rootPath):
        self.rootPath = os.path.abspath(rootPath)
        self.projectName = "".join(rootPath.split("/")[-1:]).replace(".gmx", "")

    def expandPath(self, path):
        return os.path.join(self.rootPath, path).replace("\\", "/")

    def buildResolutionTable(self):
        pprint(self.sprites[0])
        resolutionTable = []#TODO: Should this be a dict
        #Append the names of the players sprites
        for sprite in self.sprites:
            resolutionTable.append("".join(sprite["filename"].split("/")[-1:]).replace(".sprite.gmx", ""))

        #Append the object names into the sprite
            
        pprint(resolutionTable)
        


    def getTag(self, name):
        return self.project[name]

    def __getitem__(self, item):
        return self.getTag(item)

def getXmlDict(file):
    xmlDict = XMLParser(file)
    pprint(xmlDict)
    return xmlDict


def loadConfigFiles(project):
    for child in project["Configs"]["children"]:
        configPath = project.expandPath(child["content"]) + ".config.gmx"
        print("Loading path:", configPath)
        project.configs.append(getXmlDict(configPath))

def loadObjectFiles(project):
    for child in project["objects"]["children"]:
        configPath = project.expandPath(child["content"]) + ".object.gmx"
        print("Loading path:", configPath)
        project.objects.append(getXmlDict(configPath))

def loadScriptFiles(project):
    for child in project["scripts"]["children"]:
        configPath = project.expandPath(child["content"]) + ".gml"
        print("Loading path:", configPath)
        project.scripts.append(Script(child["content"], project))

def loadRoomFiles(project):
    for child in project["rooms"]["children"]:
        configPath = project.expandPath(child["content"]) + ".room.gmx"
        print("Loading path:", configPath)
        project.rooms.append(getXmlDict(configPath))

def loadSpriteFiles(project):
    for child in project["sprites"]["children"]:
        configPath = project.expandPath(child["content"]) + ".sprite.gmx"
        print("Loading path:", configPath)
        project.sprites.append(getXmlDict(configPath))

def parseProjectData(file):
    project = gamemakerProject(file)
    project.project = getXmlDict(project.expandPath(project.projectName + ".project.gmx"))
    print("Loading and parsing config")
    loadConfigFiles(project)
    print("Loading object files")
    loadObjectFiles(project)
    print("Parsing scripts")
    loadScriptFiles(project)
    print("Loading room data")
    loadRoomFiles(project)
    print("Loading sprite data")
    loadSpriteFiles(project)
    project.buildResolutionTable()

parseProjectData("Erasmus.gmx")
