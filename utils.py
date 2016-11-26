
"""
Returns the name of the file or directory at the top level of a path

:param path: The full path to a file or directory
:return: The name of the file or directory at the top of the path
"""
def getTLName(path):
    return path.replace("\\", "/").split("/")[-1]
