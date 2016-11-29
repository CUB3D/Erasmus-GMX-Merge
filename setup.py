import os
import urllib.request
import tarfile
import hashlib

def downloadFile(url, outFile):
    with urllib.request.urlopen(url) as request, open(outFile, "wb") as file:
        file.write(request.read())

def extractTar(path):
    tar = tarfile.open(path, "r", )
    tar.extractall("./Examples/")

def getFileHash(path):
    with open(path, "rb") as file:
        hash_ = hashlib.sha512(file.read()).hexdigest()
    return hash_

if os.path.exists("./Examples/Erasmus.gmx") and os.path.exists("./Eamples/FireWorldScales.gmx"):
    print("Installation already done")
    input()
    exit(0)
else:
    print("Creating directorys")
    os.makedirs("./Examples")
    print("Downloading Eramus.gmx")
    downloadFile("https://discoveryschoolncl-my.sharepoint.com/personal/callum_thomson_discoveryschool_org_uk/_layouts/15/guestaccess.aspx?guestaccesstoken=34e8%2bQwClzFdFNthH2mmOYkA265giZ5dIqgF%2fV2%2fHfg%3d&docid=0d44e0a7faaa4416da6f15af4ace3e6d3&rev=1", "Examples/Erasmus.tar")
    print("Verifying")
    if getFileHash("./Examples/Erasmus.tar") == "ccee5c174fd6db7d5e397c9280fd3d8889d8d9866cc33493ce6f9dc4e3816fd5f6d57dbc841bcae94c2a884bef8d774aa430b4c8632fd87bec1424df69ee3636":
        print("Hash verification pass")
        print("Extracting")
        extractTar("./Examples/Erasmus.tar")
    else:
        print("Hash verification failed")
    os.remove("./Examples/Erasmus.tar")
    print("Done Installing Eramus.gmx")
    print("Downloading FireWorldScales.gmx")
    downloadFile("https://discoveryschoolncl-my.sharepoint.com/personal/scott_harwood_discoveryschool_org_uk/_layouts/15/guestaccess.aspx?guestaccesstoken=PGEIBGnEzYyPrj6EOJQDc31%2bJrbHa5vfDrUKYeCByys%3d&docid=160d6f839589747e2811c2e6c0c331213&rev=1", "Examples/FireWorldScales.tar")
    print("Verifying")
    if getFileHash("./Examples/FireWorldScales.tar") == "7558f97591afd1fcc754dce3cd05e093c028a3efe0439476cf3fff2242b6018f7691ea26c6303e98f694b386899acade8fec03170a8deec30d0e776f7fee3fb1":
        print("Hash verification pass")
        print("Extracting")
        extractTar("./Examples/FireWorldScales.tar")
    else:
        print("Hash verification failed")
    os.remove("./Examples/FireWorldScales.tar")
    print("Done Installing FireWorldScales.gmx")
