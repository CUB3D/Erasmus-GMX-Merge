
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