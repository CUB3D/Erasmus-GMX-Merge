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

    '''
    rootPath - The location of the root of the project
    '''
    def __init__(self, rootPath):
        self.rootPath = posixpath.abspath(rootPath)
        #Names of the project is the name of the root folder with ".gmx" removed
        self.projectName = getBaseName(getTLName(rootPath))

    '''
    Returns the full path to a file or directory inside of the project
    path - The file to get the path for
    '''
    def expandPath(self, path):
        return posixpath.join(self.rootPath, path).replace("\\\\", "/")

    '''
    Returns a list of the names of all objects in the project, This is used to find objects which have names that will
    cause collisions so that they can be renamed before preforming the merge
    '''
    def buildResolutionTable(self):
        resolutionTable = {
            "spriteNames": []
        }
        # Append the names of the players sprites
        for sprite in self.sprites:
            resolutionTable["spriteNames"].append(getBaseName(getTLName(sprite["filename"])))
        # Append the object names into the sprite
        pprint(resolutionTable)

    '''
    Override for dictionary access that will redirect project[name] to project.project[name]
    name - The key to return
    '''
    def __getitem__(self, name):
        return self.project[name]