import xml.etree.ElementTree as ElementTree
from pprint import pprint
import io

def _XMLGetElementDict(element):
    name = element.tag
    attributes = element.items()
    children = list(element)
    content = element.text

    if content is None:
        # Content should never be none
        content = ""

    #print("Found element", name, "with", len(attributes), "attributes, and", len(children), "children")

    dict_ = {
        "name": name,
        "attributes": [],
        "children": [],
        "content": content
    }

    dict_["attributes"].extend(attributes)

    for child in children:
        dict_["children"].append(_XMLGetElementDict(child))

    return dict_

def XMLParser(file):
    with open(file, "r") as handle:
        content = "".join(handle.readlines()).strip()

    root = ElementTree.XML(content)

    xmlTagList = {
        "filename":file    
    }
    for element in root:
        subdict = _XMLGetElementDict(element)
        xmlTagList[subdict["name"]] = subdict
    return xmlTagList

def parseAttributes(attributeData):
    attributes = {}
    for attribute in attributeData:
        attributes[attribute[0]] = attribute[1]
    return attributes

def NXMLWriter(file, data, rootname):
    root = ElementTree.Element(rootname)
    root.tail = "\n"
    root.text = "\n"

    for key in data:
        if type(data[key]) is dict:
            __NXMLWriter(data[key], root)

    tree = ElementTree.ElementTree(root)
    fakeFile = io.BytesIO()
    preface = "<!--This files was created by the spawn of the devil, do not touch or encur their wrath-->\n"
    preface = ""
    tree.write(fakeFile, encoding="utf-8", xml_declaration=True)
    fakeFile.seek(0)
    with open(file, "wb") as handle:
        handle.write(bytes(preface, "utf-8"))
        handle.write(fakeFile.read())

def __NXMLWriter(data, rootobj, depth=1, indent="    "):

    if type(data) == dict and "children" in data and len(data["children"]) > 0:
        rootobj.text = "\n" + indent * depth
        subElement = ElementTree.SubElement(rootobj, data["name"])
        subElement.tail = "\n" + (indent * depth)
        subElement.text = "\n" + (indent * (depth + 1))
        subElement.attrib = parseAttributes(data["attributes"]) if "attributes" in data else {}
        for child in data["children"]:
            __NXMLWriter(child, subElement, depth + 1, indent)
    else:
        temp = data[0] if type(data) == list else data
        subElement = ElementTree.SubElement(rootobj, temp["name"])
        subElement.tail = "\n" + (indent * depth if depth > 1 else "")
        subElement.text = temp["content"] if "content" in temp else ""
        subElement.attrib = parseAttributes(temp["attributes"]) if "attributes" in temp else {}

