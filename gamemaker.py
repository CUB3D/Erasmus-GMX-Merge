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

    def correctMistakes(self):
        cases = {
            "spriteNames": self.sprites,
            "objectNames": self.objects,
            "roomNames": self.rooms,
            "backgroundNames": self.backgrounds
        }

        self.renamedFiles = {
            "spriteNames": [],
            "objectNames": [],
            "roomNames": [],
            "backgroundNames": []
        }


        for level in self.renamedFiles:#iterates through higher level of groups
            lst = cases[level]
            for obj in lst:
                name = getBaseName(getTLName(lst[obj]["filename"]))
                new = level[:3]+"_"+self.projectName+"_"+name
                new = new.replace("(","_").replace(")","_").replace(" ","_")
                self.renamedFiles[level].append((new,name))
                print("renamed", name, "to", new)

        self.renamedFiles["scriptNames"] = []

        for obj in self.scripts:
            name = obj
            new = "scr_" + self.projectName + "_" + name
            new = new.replace("(", "_").replace(")", "_").replace(" ", "_")
            self.renamedFiles["scriptNames"].append((new, name))
            print("renamed", name, "to", new)


    def __getitem__(self, name):
        """
        Override for dictionary access that will redirect project[name] to project.project[name]
        :param name: The name of the key in project.project[name]
        :return: The element at project.project[name]
        """
        return self.project[name]
