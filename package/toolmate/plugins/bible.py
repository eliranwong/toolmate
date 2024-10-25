"""
This plugin works with optional module `bible`, install it by:

> pip install toolmate[bible]
"""

try:
    from uniquebible.util.ConfigUtil import ConfigUtil
    ConfigUtil.setup(noQt=True, runMode="terminal")
    from uniquebible.util.BibleBooks import BibleBooks
    from uniquebible.util.CrossPlatform import CrossPlatform
    from uniquebible.util.BibleVerseParser import BibleVerseParser
    from uniquebible.util.LocalCliHandler import LocalCliHandler
    from uniquebible.db.BiblesSqlite import Bible
    from uniquebible.db.ToolsSqlite import Commentary
    from uniquebible import config as bibleconfig
    from toolmate import config, print1, print2, print3, removeDuplicatedListItems, stopSpinning
    from toolmate.utils.text_utils import TextUtil
    from toolmate.utils.regex_search import RegexSearch
    from flashtext import KeywordProcessor
    import traceback, re
    import importlib.resources

    config.uniquebible_path = str(importlib.resources.files("uniquebible"))
    # load resources information
    cwd = os.getcwd()
    os.chdir(config.uniquebible_path)
    config.uniquebible_platform = CrossPlatform()
    config.uniquebible_platform.setupResourceLists()
    config.uniquebible_localCliHandler = LocalCliHandler()
    os.chdir(cwd)

    """ available resources:
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
        stopSpinning()
        content = config.currentMessages[-1]["content"]
        config.toolTextOutput = BibleVerseParser(False).extractAllReferencesReadable(content)
        print2("\n```references")
        print1(config.toolTextOutput if config.toolTextOutput else "[not found]")
        print2("```")
        return ""
    functionSignature = {
        "examples": [],
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
        stopSpinning()
        def displayBibleVerses(verseList, text=None, searchString=""):
            bible = Bible(text=text)
            if searchString and not verseList:
                # perform a plain text search if no bible reference is found
                # use tools @search_bible or @search_bible_paragraphs for more advanced searches
                query = "SELECT Book, Chapter, Verse FROM Verses WHERE (Scripture LIKE ?)"
                binding = (f"%{searchString}%",)
                fullVerseList = bible.getSearchVerses(query, binding)
            else:
                # include all verses within a range
                fullVerseList = bible.getEverySingleVerseList(verseList)
            for verse in fullVerseList:
                b, c, v, verseText = bible.readTextVerse(*verse, noAudioTag=True)
                verseText = re.sub("<[^<>]*?>", "", verseText)
                verseText = f"({parser.bcvToVerseReference(b, c, v)}) {verseText}"
                try:
                    print1(verseText)
                except:
                    print(verseText)
                config.toolTextOutput += f"{verseText}\n"

        # change to uniquebible app directory temporarily
        cwd = os.getcwd()
        os.chdir(config.uniquebible_path)

        # display verses
        config.toolTextOutput = ""
        content = config.currentMessages[-1]["content"]
        content = re.sub("([0-9]) (:[0-9])", r"\1\2", content)
        parser = BibleVerseParser(True)
        verseList = parser.extractAllReferences(content)

        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_list([f"`{i}`" for i in config.uniquebible_platform.textList])
        bibles = removeDuplicatedListItems(keyword_processor.extract_keywords(content))
        if not bibles:
            bibles = [f"`{bibleconfig.mainText}`"]
        if not verseList:
            content = re.sub("|".join(bibles), "", content)
            content = re.sub(" [ ]+?([^ ])", r" \1", content).rstrip()
        for i in bibles:
            i = i[1:-1]
            heading = f"# Bible: {i}"
            config.toolTextOutput += f"\n{heading}\n\n"
            print()
            print2(heading)
            displayBibleVerses(verseList, text=i, searchString="" if verseList else content)

        config.toolTextOutput = config.toolTextOutput.strip()

        # change back to previous directory
        os.chdir(cwd)
        return ""
    functionSignature = {
        "examples": [
            "John 3:16-18", # provide a single reference; use default bible version if bible version is not given
            "`NIV` John 3:16-18; Deu 6:4", # specify a bible version and multiple references
            "`NIV` `ESV` John 3:16-18; Deu 6:4", # specify multiple bible versions and multiple references
            "Jesus love", # perform a plain text search
            "`NET` apostle of Christ", # search for 'apostle of Christ' in NET bible
        ],
        "name": "bible",
        "description": "Retrieve Bible verses based on given references or perform a plain text search",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
    config.addFunctionCall(signature=functionSignature, method=bible)
    config.inputSuggestions.append("Show bible verses: ")

    # input suggestions
    standardBibleBooks = []
    bookSuggestions = {}
    abbrev = BibleBooks.abbrev["eng"]
    for i in range(1, 67):
        abb, fullName = abbrev[str(i)]
        standardBibleBooks.append(abb)
        standardBibleBooks.append(fullName)
        chapters = BibleBooks.chapters[i]
        bookSuggestions[abb] = {str(ii): {f":{iii}": None for iii in range(1, BibleBooks.verses[i][ii]+1)} for ii in range(1, chapters+1)}
        bookSuggestions[fullName] = {str(ii): {f":{iii}": None for iii in range(1, BibleBooks.verses[i][ii]+1)} for ii in range(1, chapters+1)}
    config.inputSuggestions.append(bookSuggestions)
    bibleSuggestions = {}
    for i in config.uniquebible_platform.textList:
        bibleSuggestions[f"`{i}`"] = bookSuggestions
    for i in standardBibleBooks:
        bibleSuggestions[i] = bookSuggestions[i]
    config.inputSuggestions.append({"@bible": bibleSuggestions})

    # Tool: @uniquebible @uba
    def uniquebible(function_args):
        stopSpinning()
        command = config.currentMessages[-1]["content"].replace('"', '\\"')
        config.toolTextOutput = subprocess.run(f'''uniquebible stream "{command}"''', shell=True, capture_output=True, text=True).stdout.strip()
        print2("\n```UniqueBible App")
        print1(config.toolTextOutput)
        print2("```")
        return ""
    functionSignature = {
        "examples": [],
        "name": "uniquebible",
        "description": "Run UniqueBible App commands to retrieve bible data",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }
    config.addFunctionCall(signature=functionSignature, method=uniquebible)
    config.inputSuggestions.append("Extract Bible references: ")
    config.aliases["@uba "] = "@uniquebible "
    config.builtinTools["uba"] = "Retrieve bible data with UniqueBible App commands"

    textCommandSuggestion = [key + ":::" for key in config.uniquebible_localCliHandler.textCommandParser.interpreters.keys()]
    commandCompleterSuggestions = config.uniquebible_localCliHandler.getCommandCompleterSuggestions(textCommandSuggestion=textCommandSuggestion)
    config.inputSuggestions.append({"@uniquebible": commandCompleterSuggestions})
    config.inputSuggestions.append({"@uba": commandCompleterSuggestions})

    # Tool: @bible_commentary
    if config.uniquebible_platform.commentaryList:
        def bible_commentary(function_args):
            stopSpinning()
            def getCommentaryContent(module, verse):
                content = ""
                commentary = Commentary(module)
                b, c, v, *_ = verse
                query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=?"
                commentary.cursor.execute(query, verse[0:2])
                chapterCommentary = commentary.cursor.fetchone()[0]
                if chapterCommentary:
                    pattern = '(<vid id="v[0-9]+?.[0-9]+?.[0-9]+?"></vid>)<hr>'
                    searchReplaceItems = ((pattern, r"<hr>\1"),)
                    chapterCommentary = RegexSearch.deepReplace(chapterCommentary, pattern, searchReplaceItems)
                    verseCommentaries = chapterCommentary.split("<hr>")
                    for i in verseCommentaries:
                        if f'<vid id="v{b}.{c}.{v}"' in i:
                            content = i
                            break
                return content

            # change to uniquebible app directory temporarily
            cwd = os.getcwd()
            os.chdir(config.uniquebible_path)
            # display verses
            config.toolTextOutput = ""
            content = config.currentMessages[-1]["content"]
            content = re.sub("([0-9]) (:[0-9])", r"\1\2", content)
            parser = BibleVerseParser(True)
            verseList = parser.extractAllReferences(content)
            bible = Bible(text="KJV")
            fullVerseList = bible.getEverySingleVerseList(verseList)

            keyword_processor = KeywordProcessor()
            keyword_processor.add_keywords_from_list([f"`{i}`" for i in config.uniquebible_platform.commentaryList])
            commentaries = removeDuplicatedListItems(keyword_processor.extract_keywords(content))
            if not commentaries:
                commentaries = [f"`{bibleconfig.commentaryText}`"]

            for i in commentaries:
                loaded = []
                i = i[1:-1]
                for ii in fullVerseList:
                    content = getCommentaryContent(i, ii)
                    if content and not content in loaded:
                        loaded.append(content)
                        heading = f"# Commentary: {i} - {parser.bcvToVerseReference(*ii)}"
                        config.toolTextOutput += f"\n{heading}\n\n"
                        print()
                        print2(heading)
                        content = TextUtil.htmlToPlainText(content)
                        config.toolTextOutput += f"{content}\n"
                        try:
                            print1(content)
                        except:
                            print(content)

            config.toolTextOutput = config.toolTextOutput.strip()

            # change back to previous directory
            os.chdir(cwd)
            return ""
        functionSignature = {
            "examples": [],
            "name": "bible_commentary",
            "description": "Retrieve bible commentary",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        config.addFunctionCall(signature=functionSignature, method=bible_commentary)
        config.inputSuggestions.append("Read bible commentary: ")

        commentarySuggestions = {}
        for i in config.uniquebible_platform.commentaryList:
            commentarySuggestions[f"`{i}`"] = bookSuggestions
        for i in standardBibleBooks:
            commentarySuggestions[i] = bookSuggestions[i]
        config.inputSuggestions.append({"@bible_commentary": commentarySuggestions})

    # searchbible.ai
    try:
        config.searchbible_path = str(importlib.resources.files("searchbible"))
        config.searchbible_path = re.sub(r"MultiplexedPath\('(.*?)'\)$", r"\1", config.searchbible_path)
        cwd = os.getcwd()
        os.chdir(config.searchbible_path)
        from searchbible.searchbible import search
        os.chdir(cwd)
    except:
        config.searchbible_path = ""

    if config.searchbible_path:
        # Tool: @search_bible
        def search_bible(function_args):
            stopSpinning()
            content = config.currentMessages[-1]["content"]
            print2("\n```search_bible")
            config.toolTextOutput = "```search_bible\n" + search(simpleSearch="" if content == "[NONE]" else content) + "\n```"
            print2("```")
            return ""
        functionSignature = {
            "examples": [
                "@search_bible David fled", # perform a simple similarity search for 'David fled'
                "@search_bible", # when search item is not specified, users are prompted to customise available search parameters.
            ],
            "name": "search_bible",
            "description": "Perform similarity search for verses in the bible",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        config.addFunctionCall(signature=functionSignature, method=search_bible)

        # Tool: @search_bible_paragraphs
        def search_bible_paragraphs(function_args):
            stopSpinning()
            content = config.currentMessages[-1]["content"]
            print2("\n```search_bible_paragraphs")
            config.toolTextOutput = "```search_bible_paragraphs\n" + search(simpleSearch="" if content == "[NONE]" else content) + "\n```"
            print2("```")
            return ""
        functionSignature = {
            "examples": [],
            "name": "search_bible_paragraphs",
            "description": "Perform similarity search for paragraphs in the bible",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        config.addFunctionCall(signature=functionSignature, method=search_bible_paragraphs)

except:
    #print(traceback.format_exc())
    config.uniquebible_path = ""

"""
Notes about alternate options via API:

CUV Bible
Reference: https://bible.fhl.net/json
cuv = requests.get("https://bible.fhl.net/json/qb.php?gb=0&chap=3&sec=6&chineses=出")
cuv.text.encode().decode('unicode_escape')

NET Bible
Reference: https://labs.bible.org/
https://labs.bible.org/api/?passage=John+3:16-17;%20Deut%206:4
"""