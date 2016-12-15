import xml.etree.ElementTree as ElementTree
from pprint import pprint

def _XMLGetElementDict(element):
    name = element.tag
    attributes = element.items()
    children = list(element)
    content = element.text

    #print("Found element", name, "with", len(attributes), "attributes, and", len(children), "children")

    dict_ = {
        "name": name,
        "attributes": [],
        "children": [],
        "content": content
    }

    for attrib in attributes:
        dict_["attributes"].append(attrib)

    for child in children:
        dict_["children"].append(_XMLGetElementDict(child))

    return dict_

def XMLParser(file):
    with open(file, "r") as handle:
        content = "".join([x.replace("\n", "").replace("\t", "") for x in handle.readlines()])
    root = ElementTree.XML(content)
    xmlTagList = {
        "filename":file    
    }
    for element in root:
        subdict = _XMLGetElementDict(element)
        xmlTagList[subdict["name"]] = subdict
    return xmlTagList

def __XMLWriter(data, rootobj, depth=1, indent="    "):
    for child in data:
        name = child[0]
        arguments = {}
        for argument in child[1:-1]:
            temp = "".join(argument).split("=")
            arguments[temp[0]] = temp[1]
        data = child[-1]
        if type(data) == list:
            rootobj.text = "\n" + indent * depth
            subElement = ElementTree.SubElement(rootobj, name)
            subElement.tail = "\n" + (indent * depth)
            subElement.text = "\n" + (indent * (depth + 1))
            subElement.attrib = arguments
            __XMLWriter(data, subElement, depth+1, indent)
        else:
            subElement = ElementTree.SubElement(rootobj, name)
            subElement.tail = "\n" + (indent * depth if depth > 1 else "")
            subElement.text = data
            subElement.attrib = arguments

def parseAttributes(attributeData):
    attributes = {}
    pprint(attributeData)
    for attribute in attributeData:
        attributes[attribute[0]] = attribute[1]
    return attributes

def NXMLWriter(file, data, rootname):
    print("START IN")
    pprint(data)
    print("END IN")
    root = ElementTree.Element(rootname)
    root.tail = "\n"
    root.text = "\n"

    for key in data:
        if type(data[key]) is dict:
            print("Loading data for", key)
            __NXMLWriter(data[key], root)

    tree = ElementTree.ElementTree(root)
    tree.write(file, xml_declaration=True, encoding="utf-8")

def __NXMLWriter(data, rootobj, depth=1, indent="    "):
    print("AAAType:", type(data))
    pprint(data)
    #TODO Temporary
    subData = data

    print("SubData:", subData)
    if type(data) == dict and len(subData["children"]) > 0:
        rootobj.text = "\n" + indent * depth
        subElement = ElementTree.SubElement(rootobj, subData["name"])
        subElement.tail = "\n" + (indent * depth)
        subElement.text = "\n" + (indent * (depth + 1))
        subElement.attrib = parseAttributes(subData["attributes"])
        __NXMLWriter(subData["children"], subElement, depth + 1, indent)
    else:
        temp = data[0] if type(data) == list else data
        subElement = ElementTree.SubElement(rootobj, temp["name"])
        subElement.tail = "\n" + (indent * depth if depth > 1 else "")
        subElement.text = temp["content"]
        subElement.attrib = parseAttributes(temp["attributes"])


def XMLWriter(file, dict_, rootname):
    """
    Writes a dictionary to a file in the XML format
    :param file: The name of the file to write
    :param dict_: The dictionary to output
    :param rootname: The name of the root node of the tree
    """
    root = ElementTree.Element(rootname)
    root.tail = "\n"
    root.text = "\n"
    __XMLWriter(dict_, root)
    tree = ElementTree.ElementTree(root)
    tree.write(file, xml_declaration=True, encoding="utf-8")

