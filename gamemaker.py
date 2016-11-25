import os
from pprint import pprint
#Use linux path handling
import posixpath

class Script:
    # The name of the script
    name = ""
    # The content of the script
    content = []

    def __init__(self, path, project):
        self.name = "".join(path.split("\\")[-1:]).replace(".gml", "")
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
        self.rootPath = os.path.abspath(rootPath)
        #Names of the project is the name of the root folder with ".gmx" removed
        self.projectName = rootPath.split("/")[-1].replace(".gmx", "")

    '''
    Returns the full path to a file or directory inside of the project
    path - The file to get the path for
    '''
    def expandPath(self, path):
        a= posixpath.join(self.rootPath, path).replace("\\", "/")
        pprint(a)
        return a

    '''
    Returns a list of the names of all objects in the project, This is used to find objects which have names that will
    cause collisions so that they can be renamed before preforming the merge
    '''
    def buildResolutionTable(self):
        pprint(self.sprites[0])
        resolutionTable = []  # TODO: Should this be a dict
        # Append the names of the players sprites
        for sprite in self.sprites:
            resolutionTable.append("".join(sprite["filename"].split("/")[-1:]).replace(".sprite.gmx", ""))
        # Append the object names into the sprite
        pprint(resolutionTable)

    '''
    Override for dictionary access that will redirect project[name] to project.project[name]
    name - The key to return
    '''
    def __getitem__(self, name):
        return self.project[name]