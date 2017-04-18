import xml.etree.ElementTree as ElementTree
import io


def XMLGetElementDict_Impl(element):
    name = element.tag
    attributes = element.items()
    children = list(element)
    content = element.text

    if content is None:
        # Content should never be none
        content = ""

    dict_ = {
        "name": name,
        "attributes": [],
        "children": [],
        "content": content
    }

    dict_["attributes"].extend(attributes)

    for child in children:
        dict_["children"].append(XMLGetElementDict_Impl(child))

    return dict_


def XMLParser(file):
    with open(file, "r") as handle:
        content = "".join(handle.readlines()).strip()

    root = ElementTree.XML(content)

    xmlTagList = {
        "filename": file
    }
    for element in root:
        subDictionary = XMLGetElementDict_Impl(element)
        xmlTagList[subDictionary["name"]] = subDictionary
    return xmlTagList


def parseAttributes(attributeData):
    attributes = {}
    for attribute in attributeData:
        attributes[attribute[0]] = attribute[1]
    return attributes


def XMLWriter(file, data, rootTagName):
    root = ElementTree.Element(rootTagName)
    root.tail = "\n"
    root.text = "\n"

    for key in data:
        if type(data[key]) is dict:
            XMLWriter_Impl(data[key], root)

    tree = ElementTree.ElementTree(root)
    fakeFile = io.BytesIO()
    # TODO: fix this
    # preface = "<!--This files was created by the spawn of the devil, do not touch or encur their wrath-->\n"
    preface = ""
    tree.write(fakeFile, encoding="utf-8", xml_declaration=True)
    fakeFile.seek(0)
    with open(file, "wb") as handle:
        handle.write(bytes(preface, "utf-8"))
        handle.write(fakeFile.read())


def XMLWriter_Impl(data, rootObject, depth=1, indent="    "):

    if type(data) == dict and "children" in data and len(data["children"]) > 0:
        rootObject.text = "\n" + indent * depth
        subElement = ElementTree.SubElement(rootObject, data["name"])
        subElement.tail = "\n" + (indent * depth)
        subElement.text = "\n" + (indent * (depth + 1))
        subElement.attrib = parseAttributes(data["attributes"]) if "attributes" in data else {}
        for child in data["children"]:
            XMLWriter_Impl(child, subElement, depth + 1, indent)
    else:
        temp = data[0] if type(data) == list else data
        subElement = ElementTree.SubElement(rootObject, temp["name"])
        subElement.tail = "\n" + (indent * depth if depth > 1 else "")
        subElement.text = temp["content"] if "content" in temp else ""
        subElement.attrib = parseAttributes(temp["attributes"]) if "attributes" in temp else {}
