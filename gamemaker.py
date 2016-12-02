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

    def __init__(self, path, project):
        #Get the name of the script with no file extension, as this is how the name is stored in the project files
        self.name = getBaseName(getTLName(path))
        with open(project.expandPath(path), "r") as handle:
            self.content = handle.readlines()


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
    # List of all of the sprites in the project
    sprites = []

    def __init__(self, rootPath):
        """
        :param rootPath: The location of the root of the project
        """
        self.rootPath = posixpath.abspath(rootPath)
        #Names of the project is the name of the root folder with ".gmx" removed
        self.projectName = getBaseName(getTLName(rootPath))

    def expandPath(self, path):
        """
        Returns the full path to a file or directory inside of the project structure

        :param path: The relative path to a file in the project
        :return: The full path to the file
        """
        return posixpath.join(self.rootPath, path).replace("\\", "/")

    def buildResolutionTable(self):
        """
        Retuns a listg of the names of all objects in the project, This is used to find objects which have names that will cause collisions
        so that whey can be renamed before preforming the mergei

        :return: A list of all of the names of every named object in the project
        """
        self.resolutionTable = {
            "spriteNames": [],
            "objectNames":[],
            "roomNames":[],
            "scriptNames":[]
        }
        # Append the names of the players sprites
        for sprite in self.sprites:
            self.resolutionTable["spriteNames"].append(getBaseName(getTLName(sprite["filename"])))

        for object in self.objects:
            self.resolutionTable["objectNames"].append(getBaseName(getTLName(object["filename"])))

        for room in self.rooms:
            self.resolutionTable["roomNames"].append(getBaseName(getTLName(room["filename"])))

        for script in self.scripts:
            self.resolutionTable["scriptNames"].append(script.name)

        pprint(self.resolutionTable)
        
    def __getitem__(self, name):
        """
        Override for dictionary access that will redirect project[name] to project.project[name]
        :param name: The name of the key in project.project[name]
        :return: The element at project.project[name]
        """
        return self.project[name]
