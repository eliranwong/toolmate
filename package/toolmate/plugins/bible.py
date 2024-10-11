"""
This plugin works with optional module `bible`, install it by:

> pip install toolmate[bible]

Notes about alternate options via API:

CUV Bible
Reference: https://bible.fhl.net/json
cuv = requests.get("https://bible.fhl.net/json/qb.php?gb=0&chap=3&sec=6&chineses=出")
cuv.text.encode().decode('unicode_escape')

NET Bible
Reference: https://labs.bible.org/
https://labs.bible.org/api/?passage=John+3:16-17;%20Deut%206:4
"""

try:
    from uniquebible.util.ConfigUtil import ConfigUtil
    ConfigUtil.setup(noQt=False)
    from uniquebible.util.CrossPlatform import CrossPlatform
    from uniquebible.util.BibleVerseParser import BibleVerseParser
    from uniquebible.db.BiblesSqlite import Bible
    from toolmate import config, print1, print2, print3, removeDuplicatedListItems
    from flashtext import KeywordProcessor
    import traceback
    import importlib.resources

    config.uniquebible_path = str(importlib.resources.path(package="uniquebible", resource=""))
    # load resources information
    cwd = os.getcwd()
    os.chdir(config.uniquebible_path)
    config.uniquebible_platform = CrossPlatform()
    config.uniquebible_platform.setupResourceLists()
    os.chdir(cwd)

    """ available resource:
    config.uniquebible_platform.textList
    config.uniquebible_platform.textFullNameList
    config.uniquebible_platform.strongBibles
    config.uniquebible_platform.commentaryList
    config.uniquebible_platform.commentaryFullNameList
    config.uniquebible_platform.referenceBookList
    config.uniquebible_platform.topicListAbb
    config.uniquebible_platform.topicList
    config.uniquebible_platform.lexiconList
    config.uniquebible_platform.dictionaryListAbb
    config.uniquebible_platform.dictionaryList
    config.uniquebible_platform.encyclopediaListAbb
    config.uniquebible_platform.encyclopediaList
    config.uniquebible_platform.thirdPartyDictionaryList
    config.uniquebible_platform.pdfList
    config.uniquebible_platform.epubList
    config.uniquebible_platform.docxList
    """

    # Tool: @extract_bible_references
    def extract_bible_references(function_args):
        content = config.currentMessages[-1]["content"]
        config.toolTextOutput = BibleVerseParser(False).extractAllReferencesReadable(content)
        print2("\n```references")
        print1(config.toolTextOutput if config.toolTextOutput else "[not found]")
        print2("```")
        return ""
    functionSignature = {
        "examples": [
            "Extract Bible references",
        ],
        "name": "extract_bible_references",
        "description": "Extract Bible references from a block of text",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
    config.addFunctionCall(signature=functionSignature, method=extract_bible_references)
    config.inputSuggestions.append("Extract Bible references: ")

    # Tool: @bible
    def bible(function_args):

        def displayBibleVerses(verseList, text=None):
            bible = Bible(text=text)
            fullVerseList = bible.getEverySingleVerseList(verseList)
            for verse in fullVerseList:
                b, c, v, verseText = bible.readTextVerse(*verse, noAudioTag=True)
                verseText = f"({parser.bcvToVerseReference(b, c, v)}) {verseText}"
                try:
                    print1(verseText)
                except:
                    print(verseText)
                config.toolTextOutput += f"{verseText}\n"

        # change to uniquebible app directory temporarily
        uniquebible = str(importlib.resources.path(package="uniquebible", resource=""))
        cwd = os.getcwd()
        os.chdir(config.uniquebible_path)
        # display verses
        config.toolTextOutput = ""
        content = config.currentMessages[-1]["content"]
        parser = BibleVerseParser(True)
        verseList = parser.extractAllReferences(content)

        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_list([f"`{i}`" for i in config.uniquebible_platform.textList])
        bibles = removeDuplicatedListItems(keyword_processor.extract_keywords(content))

        if bibles:
            for i in bibles:
                i = i[1:-1]
                heading = f"# Bible: {i}"
                config.toolTextOutput += f"\n{heading}\n\n"
                print()
                print2(heading)
                displayBibleVerses(verseList, text=i)
        else:
            heading = "# Bible"
            config.toolTextOutput += f"\n{heading}\n\n"
            displayBibleVerses(verseList)

        config.toolTextOutput = config.toolTextOutput.strip()

        # change back to previous directory
        os.chdir(cwd)
        return ""
    functionSignature = {
        "examples": [
            "Show bible verses",
        ],
        "name": "bible",
        "description": "Show bible verses content",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
    config.addFunctionCall(signature=functionSignature, method=bible)
    config.inputSuggestions.append("Show bible verses: ")

except:
    #print(traceback.format_exc())
    pass