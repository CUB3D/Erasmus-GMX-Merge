import xml.etree.ElementTree as ElementTree

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
