from shutil import rmtree,copy2,copytree

from gamemaker import *
from xmlstuff import XMLParser, XMLWriter, NXMLWriter


def getXmlDict(file):
    xmlDict = XMLParser(file)
    #pprint(xmlDict)
    return xmlDict

def recursiveFileLoading_Impl(child, project, ending, callback):
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
            tempStorage.extend(recursiveFileLoading_Impl(baby, project, ending, callback))
        tempStorage.append(callback(path))
    return tempStorage

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
    content = []
    for child in project[dictKey]["children"]:
        configPath = project.expandPath(child["content"]) + ending
        # If the element has children then it has no "useful" content (All whitespace)
        if len(child["children"]) > 0:
            #recursive scan
            print("Found subdir:", child["attributes"][0][1])
            content.extend(recursiveFileLoading_Impl(child, project, ending, callback))
        else:
            print("Loading path:", configPath)
            content.append(callback(configPath))
    return content

def XMLGeneratorCallback(path):
    return getXmlDict(path)


def loadConfigFiles(project):
    """
    Loads the data from the config files into the project
    :param project: The project object
    """
    project.configs = recursiveFileLoading(project, "Configs", ".config.gmx", XMLGeneratorCallback)

def loadObjectFiles(project):
    """
    Loads the data from the object files into the project
    :param project: The project object
    """
    project.objects = recursiveFileLoading(project, "objects", ".object.gmx", XMLGeneratorCallback)

def loadScriptFiles(project):
    """
    Loads the data from the scripts into a list of script objects in the project
    :param project: The project object
    """
    project.scripts = recursiveFileLoading(project, "scripts", "", lambda path: Script(path))

def loadRoomFiles(project):
    """
    Loads the data from the room files into the project
    :param project: The project object
    """
    project.rooms = recursiveFileLoading(project, "rooms", ".room.gmx", XMLGeneratorCallback)

def loadSpriteFiles(project):
    """
    Loads sprite data from the sprite files into the project
    :param project: The project object
    """
    project.sprites = recursiveFileLoading(project, "sprites", ".sprite.gmx", XMLGeneratorCallback)

def nameChanger(projects):
    """
    A method to use the names of the collision and then simply rename them using the common structure of the game maker profile
    :param projects: a list of all projects to be compiled
    """
    #NOTE we could elect to rename all files
    for project in projects:
        project.correctMistakes() #changes all objects to turples

def createFolderStructure(projects,startDir):
    """
    A method to generate the folder structure in a new directory, for the final merged project
    Will create subdirectories for each of the projects being merged
    :param projects: a list of all the different gameMakerProject types
    :param startDir: a location for the new merged project to be located
    """
    cases = ["objects","Output","rooms","script","sprites"]
    print("Making merge directory")
    if os.path.exists(startDir):
        if input("Output directory already exists, remove? (y/n)").lower() == "y":
            print("Removing")
            rmtree(startDir)
            os.makedirs(startDir)
            copytree(projects[0].rootPath + "/Configs",startDir + "/Configs")
            for case in cases:
                basePath = os.path.abspath(os.path.join(startDir, case))
                for project in projects:
                    projectSubDir = os.path.join(basePath, project.projectName) 
                    print("Making", projectSubDir, "directory")
                    os.makedirs(projectSubDir)
        else:
            print("Aborting")
            exit(0)
            
def renameSpriteImages(projects,baseDir):
    for project in projects: #iterates through all projects
        if not os.path.exists(baseDir +"/sprites/"+project.projectName+"/images/"):
            os.makedirs(baseDir +"/sprites/"+project.projectName+"/images/")
        for sprite in project.renamedFiles["spriteNames"]:
            #sprites could have no collisions or could have collisions the only way to check is against the renamedFiles
            count = 0
            while True:
                try:
                    cp = (baseDir + "/sprites/" + project.projectName + "/images/" + sprite[0] + "_" + str(count) + ".png")
                    src =(project.rootPath + "/sprites/images/"+sprite[1]+"_"+str(count)+".png")
                    copy2(src,cp)
                    count += 1
                except :
                    if count == 0: #if the program wasnt event able to copy one file it means the image isnt in the desired location
                        print("unable to copy",project.rootPath + "/sprites/images/"+sprite[1]+"_"+str(count)+".png This could be that the sprite has no image")
                     #exits out of loop if it cant copy file, as it will have prexisted, what if the file is not not there
                    break
            project.renamedFiles["spriteNames"][project.renamedFiles["spriteNames"].index(sprite)] += (count,)

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

def getRenameTable(project, key, tagName, pathbase):
    """
    Builds a table of all the names of each object after the rename operation
    :param project:
    :param key:
    :param tagName:
    :return:
    """
    data = []
    for object_ in project.resolutionTable[key]:
        name = object_
        data.append([tagName, os.path.join(pathbase, project.projectName, name[0])])
    return data


def generateNewProjectFiles(projects, path):
    """
    Generates all of the XML files required by a project
    :param project: The project to generate files for
    :param path: The path to the new root directory of the project
    """
    newName = os.path.join(path, getTLName(path) + ".project.gmx")
    print("New project name:", newName)

    dict_ = {}

    dict_["configs"] = {"name": "Configs", "attributes": [("name", "configs")], "children": [{"name": "Config", "content": "Configs\Default"}]}
    dict_["NewExtensions"] = {"name": "NewExtensions"}
    dict_["sounds"] = {"name": "sounds", "content": "", "attributes": [("name", "sound")]}
    dict_["sprites"] = {"name": "sprites", "content": "", "attributes": [("name", "sprites")], "children": []}
    dict_["help"] = {"name":"help", "children": [{"name":"rtf", "content":"help.rtf"}]}
    dict_["TutorialState"] = {"name": "TutorialState", "children": [{"name": "isTutorial", "content": "0"}, {"name": "TutorialName"}, {"name": "TutorialPage", "content": "0"}]}
    dict_["paths"] = {"name": "paths", "attributes": [("name", "paths")]}
    dict_["scripts"] = {"name": "scripts", "attributes": [("name", "scripts")], "children": []}
    dict_["objects"] = {"name": "objects", "attributes": [("name", "objects")], "children":[]}
    dict_["rooms"] = {"name": "rooms", "attributes": [("name", "rooms")], "children": []}

    
    spriteDir = os.path.join(path, "sprites/")
    scriptDir = os.path.join(path, "script/")
    objectDir = os.path.join(path, "objects/")
    roomDir = os.path.join(path, "rooms/")
    
    for project in projects:
        writeSpriteFiles(project, spriteDir)
        writeGMLFiles(project, scriptDir)
        writeObjectFiles(project, objectDir)
        writeRoomFiles(project, roomDir)
        
        baseSpriteDirectory = os.path.join(path, "sprites", project.projectName)
        baseScriptDirectory = os.path.join(path, "script", project.projectName)
        baseObjectDirectory = os.path.join(path, "objects", project.projectName)
        baseRoomDirecotry = os.path.join(path, "rooms", project.projectName)

        for file in os.listdir(baseSpriteDirectory):
            if not os.path.isdir(os.path.join(baseSpriteDirectory, file)):
                relativePath = "sprites/" + project.projectName + "/" + getBaseName(file)
                newDict = {"name": "sprite", "content": relativePath}
                dict_["sprites"]["children"].append(newDict)

        for file in os.listdir(baseScriptDirectory):
            if not os.path.isdir(os.path.join(baseScriptDirectory, file)):
                relativePath = "script/" + project.projectName + "/" + getBaseName(file)
                newDict = {"name": "script", "content": relativePath}
                dict_["scripts"]["children"].append(newDict)

        for file in os.listdir(baseObjectDirectory):
            if not os.path.isdir(os.path.join(baseObjectDirectory, file)):
                relativePath = "objects/" + project.projectName + "/" + getBaseName(file)
                newDict = {"name": "object", "content": relativePath}
                dict_["objects"]["children"].append(newDict)

        for file in os.listdir(baseRoomDirecotry):
            if not os.path.isdir(os.path.join(baseRoomDirecotry, file)):
                relativePath = "rooms/" + project.projectName + "/" + getBaseName(file)
                newDict = {"name": "room", "content": relativePath}
                dict_["rooms"]["children"].append(newDict)




    #pprint(dict_)

    NXMLWriter(newName, dict_, "assets")

def writeRoomFiles(project, path):
    for newName, oldName in project.renamedFiles["roomNames"]:
        roomXML = getXmlDict(os.path.join(project.rootPath, "rooms", oldName + ".room.gmx"))

        for child in roomXML["instances"]["children"]:
            for i in range(len(child["attributes"])):
                name = child["attributes"][i][0]
                value = child["attributes"][i][0]
                if name == "objName":
                    for newObjName, oldObjName in project.renamedFiles["objectNames"]:
                        if oldName == value:
                            child["attributes"][i] = (name, newName)


        newFile = os.path.join(path, project.projectName, newName + ".room.gmx")
        print("Generating", newFile)
        NXMLWriter(newFile, roomXML, "room")

def writeSpriteFiles(project, path):
    for sprite in project.renamedFiles["spriteNames"]:
        ###parse the xml###
        activeDict = getXmlDict(project.rootPath + "/sprites/" + sprite[1] +".sprite.gmx")#parses the xml from the original
        if sprite[2] != 0:
            activeDict["frames"]["children"][0]["content"] = project.projectName +"\images\\" + sprite[0]+"_0.png" #renames the frame content to the location of the new image
            for frame in range(1,sprite[2] -1):
                activeDict["frames"]["children"][frame]["content"] = project.projectName + "\images\\" + sprite[0]+"_"+str(frame)+".png" # appends a new frame
        newFile = path + project.projectName +"/"+ sprite[0] +".sprite.gmx" #renames the file to the new location
        print("Generating", newFile)
        NXMLWriter(newFile,activeDict,"sprite")

def writeGMLFiles(project, path):
    #TODO Script loading is no longer needed at the beginning
    for code in project.renamedFiles["scriptNames"]:
        script = Script(project.rootPath + "/scripts/" + code[1] + ".gml")

        for objects in project.renamedFiles["objectNames"]:
            for i in range(0, len(script.content)):
                line = script.content[i]
                if objects[1] in line:
                    print("Replaced reference to", objects[1], "in", script.name)
                    script.content[i] = line.replace(objects[1], objects[0])

        path_ = path + project.projectName + "/" + code[0] + ".gml"
        print("Generating:", path)
        script.write(path_)

def writeObjectFiles(project, path):
    for obj in project.renamedFiles["objectNames"]:
        #This xml is too complicated to generate the standard way
        objPath = os.path.join(project.rootPath, "objects", obj[1] + ".object.gmx")
        objectXML = getXmlDict(objPath)
        events = objectXML["events"]
        for child in events["children"]:
            #the children of events "event" always have one child, an "action"

            for i in range(len(child["attributes"])):
                attributeName = child["attributes"][i][0]
                attributeValue = child["attributes"][i][1]
                if attributeName == "ename":
                    for newName, oldName in project.renamedFiles["objectNames"]:
                        if oldName == attributeValue:
                            child["attributes"][i] = (attributeName, newName)

            action = child["children"][0]
            #This appears to indicate how the event should be called
            #0 Seems to mean a pre-made event, 2 seems to be a script
            exeType = "0"
            arguments = {}
            for baby in action["children"]:
                if baby["name"] == "exetype":
                    exeType = baby["content"]
                if baby["name"] == "arguments":
                    arguments = baby

            kind = ""
            data = ""
            for argument in arguments["children"]:
                for argumentChild in argument["children"]:
                    if argumentChild["name"] == "kind":
                        kind = argumentChild["content"]
                    # Extend this to support all data types
                    if argumentChild["name"] == "string":
                        data = argumentChild["content"]
            if exeType == "2":
                #Ignore everything that is not a script for now
                print("found exetype", exeType)
                print("Running replace")

                for newName, oldName in project.renamedFiles["objectNames"]:
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
        NXMLWriter(newPath, objectXML, "object")

project1 = parseProjectData("./Examples/Erasmus.gmx")#Start using the file Erasmus in the example
project2 = parseProjectData("./Examples/FireWorldScales.gmx")#throws error as not finding file
projectList = [project1,project2]
#collisionList, passList = checkCollision(projectList)
createFolderStructure([project1,project2],"./Examples/Merge")
nameChanger(projectList)
renameSpriteImages([project1,project2],"./Examples/Merge")
generateNewProjectFiles([project1, project2], "./Examples/Merge")
print("finished")
input()#hang
