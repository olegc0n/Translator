import json
import codecs
import xml.etree.ElementTree as ET
from googletrans import Translator

def doTranslation(initialStrings: list, language: str, verbose: bool = False) -> list:
    translatedLines = []
    translator = Translator()
    res = translator.translate(initialStrings, dest=language)
    for translated in res:
        translatedLines.append(translated.text)
    if verbose:
        for key, value in zip(initialStrings, translatedLines):
            print(f"{key} -> {value}")
        print(f"Initial size {len(initialStrings)}, translated size {len(translatedLines)}")
    return translatedLines

def getDataFromXMLFile(filePath: str, excludeFromTranslation: list = []) -> list:
    # open file and create dictionary
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(filePath, parser=parser)
    root = tree.getroot()
    initialDatabase = {}
    for elem in root:
        if elem.tag is not ET.Comment:
            initialDatabase[elem.attrib['name']] = elem.text
    # extract all strings from json 
    initialStrings = []
    def extractAllKeys(dataDict):
        for key, value in dataDict.items():
            if type(value) is dict:
                extractAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    initialStrings.append(value)
    extractAllKeys(initialDatabase)
    
    return initialStrings

def getDataFromJSONFile(filePath: str, excludeFromTranslation: list = []) -> list:
     # open file and read as json
    with open(filePath, 'r') as openfile:
        initialDatabase = json.load(openfile)
    # extract all strings from json 
    initialStrings = []
    def extractAllKeys(dataDict):
        for key, value in dataDict.items():
            if type(value) is dict:
                extractAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    initialStrings.append(value)
    extractAllKeys(initialDatabase)
    return initialStrings

def getDataFromRESXFile(filePath: str, excludeFromTranslation: list = []) -> list:
     # open file and create dictionary
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(filePath, parser=parser)
    root = tree.getroot()
    initialDatabase = {}
    for elem in root:
        if elem.tag is not ET.Comment and 'data' == elem.tag:
            for subelem in elem:
                if 'value' == subelem.tag:
                    initialDatabase[elem.attrib['name']] = subelem.text
    
    # extract all strings from json 
    initialStrings = []
    def extractAllKeys(dataDict):
        for key, value in dataDict.items():
            if type(value) is dict:
                extractAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    initialStrings.append(value)
    extractAllKeys(initialDatabase)
    return initialStrings

def processXMLFile(filePath:str, translatedLines:list, fileToWrite:str, excludeFromTranslation: list = []) -> None:
    # open file and create dictionary
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(filePath, parser=parser)
    root = tree.getroot()
    initialDatabase = {}
    for elem in root:
        if elem.tag is not ET.Comment:
            initialDatabase[elem.attrib['name']] = elem.text
    
    # do replacement in the same order
    global counter
    counter = 0
    def overwriteAllKeys(dataDict):
        global counter
        for key, value in dataDict.items():
            if type(value) is dict:
                overwriteAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    dataDict[key] = translatedLines[counter]
                    counter += 1
    tmpDatabase = initialDatabase.copy()
    overwriteAllKeys(tmpDatabase)

    #save to new file
    for elem in root:
        if elem.tag is not ET.Comment:
            elem.text = tmpDatabase[elem.attrib['name']]
    with open(fileToWrite, 'wb') as outfile:
    #with codecs.open(fileToWrite, "wb") as outfile:
        tree.write(outfile, encoding='utf-8')

def processJsonFile(filePath:str, translatedLines:list, fileToWrite:str, excludeFromTranslation: list = []):
    # open file and read as json
    with open(filePath, 'r') as openfile:
        initialDatabase = json.load(openfile)

    # do replacement in the same order
    global counter
    counter = 0
    def overwriteAllKeys(dataDict):
        global counter
        for key, value in dataDict.items():
            if type(value) is dict:
                overwriteAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    dataDict[key] = translatedLines[counter]
                    counter += 1
    tmpDatabase = initialDatabase.copy()
    overwriteAllKeys(tmpDatabase)

    #save to new file
    with codecs.open(fileToWrite, "w", encoding='utf-8') as outfile:
        json.dump(tmpDatabase, outfile, sort_keys=False, indent=4, ensure_ascii=False)

def processResxFile(filePath:str, translatedLines:list, fileToWrite:str, excludeFromTranslation:list = []):
    # open file and create dictionary
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(filePath, parser=parser)
    root = tree.getroot()
    initialDatabase = {}
    for elem in root:
        if elem.tag is not ET.Comment and 'data' == elem.tag:
            for subelem in elem:
                if 'value' == subelem.tag:
                    initialDatabase[elem.attrib['name']] = subelem.text

    # do replacement in the same order
    global counter
    counter = 0
    def overwriteAllKeys(dataDict):
        global counter
        for key, value in dataDict.items():
            if type(value) is dict:
                overwriteAllKeys(value)
            else:
                if value not in excludeFromTranslation:
                    dataDict[key] = translatedLines[counter]
                    counter += 1
    tmpDatabase = initialDatabase.copy()
    overwriteAllKeys(tmpDatabase)

    #save to new file
    for elem in root:
        if elem.tag is not ET.Comment and 'data' == elem.tag:
            for subelem in elem:
                if 'value' == subelem.tag:
                    subelem.text = tmpDatabase[elem.attrib['name']]

    with open(fileToWrite, 'wb') as outfile:
        tree.write(outfile, encoding='utf-8')
