from shutil import rmtree, copy2, copytree

from gamemaker import *
from xmlstuff import XMLParser, XMLWriter
from utils import getReplacementName


# That exception will never happen in a situation other than a corrupt project
# noinspection PyBroadException
def recursiveFileLoading_Impl(child, project, ending, callback):
    """
    Recursively scans a child node to find the names of all items in the tree
    :param child: The element in the tree that acts as a directory
    :param project: the project instance
    :param ending: The file ending of that project file (e.g. ".object.gmx" for object files)
    :param callback: Will be called with every file found and the return value will be stored mapped to the name
    :return: A list containing the names of all items in the tree
    """
    # Note this function ignores the actual names of the subdirectories which be needed later when the new project is
    # built (Unless we are just going to ignore them and create a folder for each project's files)
    tempStorage = {}
    for baby in child["children"]:
        path = project.expandPath(baby["content"]) + ending
        print("Loading: ", path)
        if len(child["children"]) > 0:
            tempStorage.update(recursiveFileLoading_Impl(baby, project, ending, callback))
        try:
            tempStorage[getTLName(getBaseName(baby["content"]))] = callback(path)
        except:
            print("ERROR: unable to load file")
    return tempStorage


# That exception will never happen in a situation other than a corrupt project
# noinspection PyBroadException
def recursiveFileLoading(project, dictKey, ending, callback):
    """
    Recursively scans a xml dictionary to find the names of elements in gmx files

    :param project: The project object
    :param dictKey: The key to scan for in the base dictionary (e.g. objects)
    :param ending: The file ending to be appended to the name of each file
    :param callback: This function will be called with the path and the project as arguments and the return value will
    be stored in the final list
    :return: A list of objects generated by running callback for the path of each item in the dictionary
    """
    content = {}
    if "children" in project[dictKey]:
        for child in project[dictKey]["children"]:
            configPath = project.expandPath(child["content"]) + ending
            # If the element has children then it has no "useful" content (All whitespace)
            if len(child["children"]) > 0:
                print("Found subdir:", child["attributes"][0][1])
                content.update(recursiveFileLoading_Impl(child, project, ending, callback))
            else:
                print("Loading path:", configPath)
                try:
                    content[getTLName(getBaseName(child["content"]))] = callback(configPath)
                except:
                    print("ERROR: Unable to load file")
    return content


def XMLGeneratorCallback(path):
    return XMLParser(path)


def nameChanger(projects):
    """
    A method to use the names of the collision and then simply rename them,
     using the common structure of the game maker profile
    :param projects: a list of all projects to be compiled
    """
    # NOTE we could elect to rename all files
    for project in projects:
        # changes all objects to tuples
        project.correctMistakes()


def createFolderStructure(projects, startDir, force):
    """
    A method to generate the folder structure in a new directory, for the final merged project
    Will create subdirectories for each of the projects being merged
    :param projects: a list of all the different gameMakerProject types
    :param startDir: a location for the new merged project to be located
    :param force: If true then the old directory is removed without asking permission
    """
    cases = ["objects", "rooms", "scripts"]
    print("Making merge directory")
    if os.path.exists(startDir):
        if force or input("Output directory already exists, remove? (y/n)").lower() == "y":
            print("Removing old output directory")
            rmtree(startDir)
        else:
            print("Aborting")
            exit(0)

    os.makedirs(startDir)
    copytree(os.path.join(projects[0].rootPath, "Configs"), os.path.join(startDir, "Configs"))
    copy2(os.path.join(projects[0].rootPath, "help.rtf"), startDir)
    for case in cases:
        basePath = os.path.abspath(os.path.join(startDir, case))
        for project in projects:
            projectSubDir = os.path.join(basePath, project.projectName)
            print("Making", projectSubDir, "directory")
            os.makedirs(projectSubDir)  
    os.makedirs(os.path.join(startDir, "Output"))
    os.makedirs(os.path.join(startDir, "sprites/images"))
    os.makedirs(os.path.join(startDir, "background/images"))


def renameSpriteImages(projects, baseDir):
    for project in projects:
        projectBasePath = os.path.join(baseDir, "sprites", "images")

        if not os.path.exists(projectBasePath):
            os.makedirs(projectBasePath)

        baseSpriteDir = os.path.join(project.rootPath, "sprites", "images")

        for i in range(len(project.renamedFiles["spriteNames"])):
            newSpriteName, oldSpriteName = project.renamedFiles["spriteNames"][i]
            count = 0
            # Have to check for collisions against all renamed files as they may or may not exists
            while True:
                src = os.path.join(baseSpriteDir, oldSpriteName + "_" + str(count) + ".png")
                if not os.path.exists(src):
                    break
                cp = os.path.join(baseSpriteDir, newSpriteName + "_" + str(count) + ".png")
                copy2(src, cp)
                count += 1

            project.renamedFiles["spriteNames"][i] += (count,)


def copyBGImageFiles(project, baseDir):
    print("copying backgrounds for", project.projectName)
    for newBackgroundName, oldBackgroundName in project.renamedFiles["backgroundNames"]:
        src = os.path.join(project.rootPath, "background", "images", oldBackgroundName + ".png")
        destination = os.path.join(baseDir, "images", newBackgroundName + ".png")
        print("Copied from", src, "to", destination)
        copy2(src, destination)


def parseProjectData(file):
    """
    Loads the data from the project into a project object and builds
    resolution tables from this data
    :param file: The path to the root diretory in the project
    """

    # Create an instance of the game maker project type using the passed file location as the root
    project = gameMakerProject(file)
    # concatenate ".project.gmx" using the Expand path function and then parse it using the XML parser from "xmlstuff"
    project.project = XMLParser(project.expandPath(project.projectName + ".project.gmx"))
    project.project["scripts"] = {} if "scripts" not in project.project else project.project["scripts"]
    project.project["background"] = {} if "scripts" not in project.project else project.project["scripts"]

    print("Parsing configs")
    project.configs = recursiveFileLoading(project, "Configs", ".config.gmx", XMLGeneratorCallback)
    print("Loading object files")
    project.objects = recursiveFileLoading(project, "objects", ".object.gmx", XMLGeneratorCallback)
    print("Parsing scripts")
    project.scripts = recursiveFileLoading(project, "scripts", "", lambda path: Script(path))
    print("Loading room data")
    project.rooms = recursiveFileLoading(project, "rooms", ".room.gmx", XMLGeneratorCallback)
    print("Loading sprite data")
    project.sprites = recursiveFileLoading(project, "sprites", ".sprite.gmx", XMLGeneratorCallback)
    print("Loading background data")
    project.backgrounds = recursiveFileLoading(project, "backgrounds", ".background.gmx", XMLGeneratorCallback)
    return project


def generateNewProjectFiles(projects, path):
    """
    Generates all of the XML files required by a project
    :param projects: The project to generate files for
    :param path: The path to the new root directory of the project
    """
    newName = os.path.join(path, getTLName(path) + ".project.gmx")
    print("New project name:", newName)

    dict_ = {"configs": {"name": "Configs", "attributes": [("name", "configs")],
                         "children": [{"name": "Config", "content": "Configs\Default"}]},
             "NewExtensions": {"name": "NewExtensions"},
             "sounds": {"name": "sounds", "content": "", "attributes": [("name", "sound")]},
             "sprites": {"name": "sprites", "content": "", "attributes": [("name", "sprites")], "children": []},
             "help": {"name": "help", "children": [{"name": "rtf", "content": "help.rtf"}]},
             "TutorialState": {"name": "TutorialState",
                               "children": [{"name": "isTutorial", "content": "0"}, {"name": "TutorialName"},
                                            {"name": "TutorialPage", "content": "0"}]},
             "paths": {"name": "paths", "attributes": [("name", "paths")]},
             "scripts": {"name": "scripts", "attributes": [("name", "scripts")], "children": []},
             "objects": {"name": "objects", "attributes": [("name", "objects")], "children": []},
             "rooms": {"name": "rooms", "attributes": [("name", "rooms")], "children": []},
             "backgrounds": {"name": "backgrounds", "attributes": [("name", "background")], "children": []}}

    spriteDir = os.path.join(path, "sprites/")
    scriptDir = os.path.join(path, "scripts/")
    objectDir = os.path.join(path, "objects/")
    roomDir = os.path.join(path, "rooms/")
    backgroundDir = os.path.join(path, "background")

    for project in projects:
        copyBGImageFiles(project, backgroundDir)
        writeSpriteFiles(project, spriteDir)
        writeGMLFiles(project, scriptDir)
        writeObjectFiles(project, objectDir)
        writeRoomFiles(project, roomDir)
        writeBackgroundFiles(project, backgroundDir)

        baseScriptDirectory = os.path.join(path, "scripts", project.projectName)
        baseObjectDirectory = os.path.join(path, "objects", project.projectName)
        baseRoomDirectory = os.path.join(path, "rooms", project.projectName)

        for file in os.listdir(baseScriptDirectory):
            if not os.path.isdir(os.path.join(baseScriptDirectory, file)):
                # No get base name because, why have a consistent format
                relativePath = os.path.join("scripts", project.projectName, file)
                newDict = {"name": "script", "content": relativePath}
                dict_["scripts"]["children"].append(newDict)

        for file in os.listdir(baseObjectDirectory):
            if not os.path.isdir(os.path.join(baseObjectDirectory, file)):
                relativePath = os.path.join("objects", project.projectName, getBaseName(file))
                newDict = {"name": "object", "content": relativePath}
                dict_["objects"]["children"].append(newDict)

        for file in os.listdir(baseRoomDirectory):
            if not os.path.isdir(os.path.join(baseRoomDirectory, file)):
                relativePath = os.path.join("rooms", project.projectName, getBaseName(file))
                newDict = {"name": "room", "content": relativePath}
                dict_["rooms"]["children"].append(newDict)

    baseSpriteDirectory = os.path.join(path, "sprites")
    baseBackgroundsDirectory = os.path.join(path, "background")

    for file in os.listdir(baseSpriteDirectory):
        if not os.path.isdir(os.path.join(baseSpriteDirectory, file)):
            relativePath = os.path.join("sprites", getBaseName(file))
            newDict = {"name": "sprite", "content": relativePath}
            print("Adding:", file)
            dict_["sprites"]["children"].append(newDict)

    for file in os.listdir(baseBackgroundsDirectory):
        if not os.path.isdir(os.path.join(baseBackgroundsDirectory, file)):
            relativePath = os.path.join("background", getBaseName(file))
            newDict = {"name": "background", "content": relativePath}
            print("Adding:", file)
            dict_["backgrounds"]["children"].append(newDict)

    XMLWriter(newName, dict_, "assets")


def writeBackgroundFiles(project, path):
    for newBackgroundName, oldBackgroundName in project.renamedFiles["backgroundNames"]:
        activeDict = project.backgrounds[oldBackgroundName]

        activeDict["data"]["content"] = os.path.join("images", newBackgroundName + ".png")

        newFile = os.path.join(path, newBackgroundName + ".background.gmx")
        print("Generating:", newFile)
        XMLWriter(newFile, activeDict, "background")


def writeRoomFiles_renameObjectReferences(project, roomXML, subtag, tagname, nameTableReference):
    for child in roomXML[subtag]["children"]:
        for i in range(len(child["attributes"])):
            name = child["attributes"][i][0]
            value = child["attributes"][i][1]
            # If the value is blank then it is an item that has no name (Seems to be possible for backgrounds sometimes)
            if name == tagname and value != "":
                child["attributes"][i] = (name, getReplacementName(project, value, nameTableReference))


def writeRoomFiles(project, path):
    for newName, oldName in project.renamedFiles["roomNames"]:
        # roomXML = XMLParser(os.path.join(project.rootPath, "rooms", oldName + ".room.gmx"))
        roomXML = project.rooms[oldName]
        # Rename objects referenced from scripts

        writeRoomFiles_renameObjectReferences(project, roomXML, "instances", "objName", "objectNames")
        writeRoomFiles_renameObjectReferences(project, roomXML, "backgrounds", "name", "backgroundNames")

        newFile = os.path.join(path, project.projectName, newName + ".room.gmx")
        print("Generating", newFile)
        XMLWriter(newFile, roomXML, "room")


def writeSpriteFiles(project, path):
    for sprite in project.renamedFiles["spriteNames"]:
        activeDict = project.sprites[sprite[1]]
        if sprite[2] != 0:
            # renames the frame content to the location of the new image
            activeDict["frames"]["children"][0]["content"] = os.path.join("images", sprite[0] + "_0.png")
            for frame in range(1, sprite[2] - 1):
                # appends a new frame
                frameName = os.path.join("images", sprite[0] + "_" + str(frame) + ".png")
                activeDict["frames"]["children"][frame]["content"] = frameName
        newFile = os.path.join(path, sprite[0] + ".sprite.gmx")
        print("Generating", newFile)
        XMLWriter(newFile, activeDict, "sprite")


def writeGMLFiles(project, path):
    for code in project.renamedFiles["scriptNames"]:
        script = project.scripts[code[1]]

        for i in range(0, len(script.content)):
            line = script.content[i]
            # TODO: Should this also support sprites and rooms??? (Test this)
            # Replace references to objects
            for objectOldName, objectNewName in project.renamedFiles["objectNames"]:
                if objectOldName in line:
                    print("Replaced reference to", objectOldName, "in", script.name)
                    script.content[i] = line.replace(objectOldName, objectNewName)
            # Replace script references (used as functions in gml)
            for newName, oldName in project.renamedFiles["scriptNames"]:
                if oldName in line:
                    print("Replaced changed reference to", oldName, "in", script.name)
                    script.content[i] = line.replace(oldName, newName)
        newFile = os.path.join(path, project.projectName, code[0] + ".gml")
        print("Generating:", newFile)
        script.write(newFile)


def writeObjectFiles(project, path):
    for obj in project.renamedFiles["objectNames"]:
        # This xml is too complicated to generate the standard way
        # TODO: break this up into functions
        objPath = os.path.join(project.rootPath, "objects", obj[1] + ".object.gmx")
        objectXML = project.objects[obj[1]]
        for sprite in project.renamedFiles["spriteNames"]:
            if objectXML["spriteName"]["content"] == sprite[1]:
                objectXML["spriteName"]["content"] = sprite[0]
        events = objectXML["events"]
        for child in events["children"]:
            # The children of events "event" always have one child, an "action"

            for i in range(len(child["attributes"])):
                attributeName = child["attributes"][i][0]
                attributeValue = child["attributes"][i][1]
                if attributeName == "ename":
                    for newName, oldName in project.renamedFiles["objectNames"]:
                        if oldName == attributeValue:
                            child["attributes"][i] = (attributeName, newName)

            action = child["children"][0]
            # This appears to indicate how the event should be called
            # 0 Seems to mean a pre-made event, 2 seems to be a script
            exeType = "0"
            arguments = {}
            for baby in action["children"]:
                if baby["name"] == "exetype":
                    exeType = baby["content"]
                if baby["name"] == "arguments":
                    arguments = baby

            data = ""
            for argument in arguments["children"]:
                for argumentChild in argument["children"]:
                    # Extend this to support all data types
                    if argumentChild["name"] == "string":
                        data = argumentChild["content"]
            if exeType == "2":
                # Ignore everything that is not a script for now

                # Replace object references
                for newName, oldName in project.renamedFiles["objectNames"]:
                    if oldName in data:
                        print("Replaced changed reference to", oldName, "in", objPath)
                        data = data.replace(oldName, newName)

                # Replace script references
                for newName, oldName in project.renamedFiles["scriptNames"]:
                    if oldName in data:
                        print("Replaced changed reference to", oldName, "in", objPath)
                        data = data.replace(oldName, newName)

                print("Rebuilding XML")

                for argument in arguments["children"]:
                    for argumentChild in argument["children"]:
                        # Extend this to support all data types
                        if argumentChild["name"] == "string":
                            argumentChild["content"] = data
        
        newPath = os.path.join(path, project.projectName, obj[0] + ".object.gmx")
        print("Generating", newPath)
        XMLWriter(newPath, objectXML, "object")


def performMerge(project1, project2, output, force=False):
    project1 = parseProjectData(project1)
    project2 = parseProjectData(project2)
    projectList = [project1, project2]
    createFolderStructure(projectList, output, force)
    nameChanger(projectList)
    renameSpriteImages(projectList, output)
    generateNewProjectFiles(projectList, output)

# performMerge("./Examples/Erasmus.gmx", "./Examples/FireWorldScale.gmx", "./Examples/Merge", True)
