import os


def getTLName(path):
    """
    Returns the name of the file or directory at the top level of a path

    :param path: The full path to a file or directory
    :return: The name of the file or directory at the top of the path
    """
    return path.replace("\\", "/").split("/")[-1]


def getBaseName(name):
    """
    Removes file endings from files

    :param name: A file name with a file ending
    :return: The name of the file with the file ending removed
    """
    return name.split(".")[0]


def fixPaths(file):
    """
    Replaces all a\b paths with a/b paths in a project
    :param file: The folder to work with
    """
    allowedFiles = ["background", "sprite", "config", "project", "sprite"]

    for root, directory, files in os.walk(file):
        for file in files:
            if file.split(".")[-2] in allowedFiles:
                path = os.path.join(root, file)
                if not os.path.isdir(path):
                    print("Fixing:", path)
                    output = ""
                    with open(path, "r") as fileHandle:
                        content = fileHandle.read()

                    # replace any / with \ if they aren't part of a xml tag
                    for i in range(len(content)):
                        changed = False
                        char = content[i]
                        if char == "/":
                            # check previous character and next character
                            if i-1 >= 0 and i + 1 <= len(content):
                                if content[i - 1] != "<" and content[i + 1] != ">":
                                    output += "\\"
                                    changed = True
                        if not changed:
                            output += char

                    with open(path, "w") as fileHandle:
                        fileHandle.write(output)


def getReplacementName(project, originalName, nameTableReference):
    """
    Gets the replacement name for an item in the project

    :param project: The project reference
    :param originalName: The original name of the item 
    :param nameTableReference: The key for the project.renamedFiles dictionary
    :return: The new name for the item
    """
    for newName, oldName in project.renamedFiles[nameTableReference]:
        if oldName == originalName:
            return newName
