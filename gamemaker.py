import os
from pprint import pprint
#Use linux path handling
import posixpath
from utils import getTLName, getBaseName

class Script:
    # The name of the script
    name = ""
    # The content of the script
    content = []

    def __init__(self, path):
        #Get the name of the script with no file extension, as this is how the name is stored in the project files
        self.name = getBaseName(getTLName(path))
        with open(path, "r") as handle:
            self.content = handle.readlines()

    def write(self, path):
        with open(path, "w") as handle:
            handle.writelines(self.content)


class gameMakerProject:
    # The path to the root of the project (The directory with the project.gmx in it)
    rootPath = ""
    # The name of the project
    projectName = ""
    # The project main project data stored in the name.project.gmx file
    project = []
    # The list of all configs in the project
    configs = []
    # List of all of the objects in the project
    objects = []
    # List of all of the scripts in the project
    scripts = []
    # List of all of the rooms in the project
    rooms = []
    # List of all of the backgrounds in the project
    backgrounds = []
    # List of all of the sprites in the project
    sprites = []
    # Dictionary containing all of the changed names of items in the project
    renamedFiles = []
    # Table containing the names of all elements of the project
    resolutionTable = []

    def __init__(self, rootPath):
        """
        :param rootPath: The location of the root of the project
        """
        self.rootPath = posixpath.abspath(rootPath)
        #Names of the project is the name of the root folder with ".gmx" removed
        self.projectName = getBaseName(getTLName(rootPath))

        self.project = {
            "configs": {},
            "objects": {},
            "scripts": {},
            "rooms": {},
            "backgrounds:": {},
            "sprites": {}
        }

    def expandPath(self, path):
        """
        Returns the full path to a file or directory inside of the project structure

        :param path: The relative path to a file in the project
        :return: The full path to the file
        """
        return posixpath.join(self.rootPath, path).replace("\\", "/")

    def buildResolutionTable(self):
        """
        Retuns a list of the names of all objects in the project, This is used to find objects which have names that will cause collisions
        so that whey can be renamed before preforming the mergei

        :return: A list of all of the names of every named object in the project
        """
        self.resolutionTable = {
            "spriteNames": [],
            "objectNames": [],
            "roomNames": [],
            "scriptNames": [],
            "backgroundNames": []
        }
        # Append the names of the players sprites
        for sprite in self.sprites:
            self.resolutionTable["spriteNames"].append(getBaseName(getTLName(self.sprites[sprite]["filename"])))

        for object in self.objects:
            self.resolutionTable["objectNames"].append(getBaseName(getTLName(self.objects[object]["filename"])))

        for room in self.rooms:
            self.resolutionTable["roomNames"].append(getBaseName(getTLName(self.rooms[room]["filename"])))

        for script in self.scripts:
            self.resolutionTable["scriptNames"].append(self.scripts[script].name)

        for room in self.rooms:
            self.resolutionTable["roomNames"].append(getBaseName(getTLName(self.rooms[room]["filename"])))

        for background in self.backgrounds:
            self.resolutionTable["backgroundNames"].append(getBaseName(getTLName(self.backgrounds[background]["filename"])))

    def correctMistakes(self):
        self.renamedFiles = {
            "spriteNames": [],
            "objectNames": [],
            "roomNames": [],
            "scriptNames": [],
            "backgroundNames": []
        }

        for level in self.renamedFiles:#iterates through higher level of groups
            for name in self.resolutionTable[level]:#iterate through all objects
                new = level[:3]+"_"+self.projectName+"_"+name
                new = new.replace("(","_").replace(")","_").replace(" ","_")
                self.renamedFiles[level].append((new,name))
                print("renamed", name, "to", new)
            

        #pprint(self.renamedFiles)

    def __getitem__(self, name):
        """
        Override for dictionary access that will redirect project[name] to project.project[name]
        :param name: The name of the key in project.project[name]
        :return: The element at project.project[name]
        """
        return self.project[name]
