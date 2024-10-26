from toolmate import config

if config.uniquebible_path:
    # Predefined Contexts

    config.predefinedContexts["Bible Topic"] = """Write about the following topic in reference to the Bible.
In addition, explain the significance of the topic in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.

# Bible topic
"""

    config.predefinedContexts["Bible Place"] = """I will provide you with a location name.
Give me comprehensive information on this location in the bible.
If this singular name is used to denote various different locations in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this location in the bible.

# Bible location
"""

    config.predefinedContexts["Bible Person"] = """I will provide you with a person name.
Give me comprehensive information on this person in the bible.
If this singular name is used to denote various different characters in the Bible, kindly provide separate descriptions for each one.
Explain the significance of this person in the bible.

# Bible preson name
"""

    # Translation
    config.predefinedContexts["Bible Hebrew Verse Translation"] = """I would like to request your assistance as a bible translator.
I will provide you with a Hebrew bible verse text.
First, give me transliteration of the text.
Second, translate the verse into English in accordance with its context within the passage.
Remember, translate from the Hebrew text that I give you, do not copy an existing translation, as I want a completely new translation.
Third, map each Hebrew word with corresponding translation.
In mapping section, do include transliteration of each Hebrew word, so that each mapping are formatted in pattern this pattern: word | transliteration | corresponding translation.
Use "Transliteration:", "Translation:" and "Mapping:" as the section titles.
Remember, do not give parsing information, explanation or repeat the bible reference that I give you.

I am giving you the Hebrew verse text below:

    # Hebrew verse
"""

    config.predefinedContexts["Bible Greek Verse Translation"] = """I would like to request your assistance as a bible translator.
I will provide you with a Greek bible verse text.
First, give me transliteration of the text.
Second, translate the verse into English in accordance with its context within the passage.
Remember, translate from the Greek text that I give you, do not copy an existing translation, as I want a completely new translation.
Third, map each Greek word with corresponding translation.
In mapping section, do include transliteration of each Greek word, so that each mapping are formatted in pattern this pattern: word | transliteration | corresponding translation.
Use "Transliteration:", "Translation:" and "Mapping:" as the section titles.
Remember, do not give parsing information, explanation or repeat the bible reference that I give you.

I am giving you the Greek verse text below:

    # Greek verse
"""

    # Book Features
    config.predefinedContexts["Bible Book Introduction"] = """Write a detailed introduction on a book in the bible, considering all the following questions:
1. Who is the author or attributed author of the book?
2. What is the date or time period when the book was written?
3. What is the main theme or purpose of the book?
4. What are the significant historical events or context surrounding the book?
5. Are there any key characters or figures in the book?
6. What are some well-known or significant passages from the book?
7. How does the book fit into the overall structure and narrative of the Bible?
8. What lessons or messages can be learned from the book?
9. What is the literary form or genre of the book (e.g. historical, prophetic, poetic, epistle, etc.)?
10. Are there any unique features or controversies surrounding the book?
I want the introduction to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the introduction, pertaining to the following bible book.

    # Bible book name
"""

    config.predefinedContexts["Bible Outline"] = """I am currently studying the following bible book and chapters and would appreciate it if you could provide me with a detailed outline for it.
I want an outline for all chapters of the bible book and chapters I am giving you.
Please divide it into several main sections and under each section, divide it into different passages.
Break down the passages into the smallest ones possible, as I am looking for a highly detailed outline.
Additionally, kindly provide a title for each passage.
Remember, use your own analysis based on the bible text instead of copying a published outline.
If chapters are not specified, provide an outline to cover all chapters of the bible book given.

    # Bible reference
"""

    # Chapter Features
    config.predefinedContexts["Bible Chapter Summary"] = """Write a detailed interpretation on a bible chapter, considering all the following questions:
1. What is the overview of the chapter?
2. How are the verses in this chapter structured or organized?
3. Are there any key verses or passages in the chapter?
4. Are there any significant characters, events, or symbols in the chapter?
5. What is the main themes or messages of the chapter?
6. What historical or cultural context is important to understand the chapter?
7. How have theologians, scholars, or religious leaders interpreted this chapter?
8. Are there any popular interpretations or controversies related to this chapter?
9. How does this chapter relate to other chapters, books, or themes in the Bible?
10. What lessons or morals can be taken from the chapter?
I want your interpretation to be comprehensive and informative.
When you explain, quote specific words or phases from relevant bible verses, if any.
Answer all these relevant questions mentioned above, in the interpretation, pertaining to the following bible chapter.

    # Bible chapter
"""

    # Verse Features
    config.predefinedContexts["Bible OT Verse Interpretation"] = """Interpret the following verse in the light of its context, together with insights of biblical Hebrew studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content.

    # Bible verse
"""

    config.predefinedContexts["Bible NT Verse Interpretation"] = """Interpret the following verse in the light of its context, together with insights of biblical Greek studies.
I want your interpretation to be comprehensive and informative.  When you explain, quote specific words or phases from the verse.
However, remember, I want you not to quote the whole verse word by word, especially in the beginning of your response, as I already know its content.

    # Bible verse
"""

    config.predefinedContexts["Bible Insights"] = """Give me exegetical insights in detail on the following bible verses:

    # Verses
"""

    # Studies
    config.predefinedContexts["Bible Perspective"] = """Tell me how we should understand the content given below, according to biblical perspectives and principles:

    # Content
"""

    config.predefinedContexts["Bible Meaning"] = """Explain the meaning of the content given below in reference to the Bible:

    # Content
"""

    config.predefinedContexts["Bible Summary"] = """Write a summary on the content given below in reference to the Bible:

    # Content
"""

    config.predefinedContexts["Bible OT Highlights"] = """Bible Highlights in an Old Testament passage in the bible.
Can you give me a detailed summary of this passage?
How can the meaning of the biblical Hebrew words in this passage provide insights that aid our understanding? Explain the insights with examples.
What are the key words and phrases used in this passage, and how do they contribute to its meaning?
How does this passage relate to other passages in the Bible, both within the same book and in other books?
Please answer all relevant questions pertaining to the following passage.
You don't need to provide all the verses from the passage, as I am already familiar with it. 
I want your response focus on my questions.  However, do not repeat my questions word by word in your answer.

Please write in detail pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible NT Highlights"] = """Bible Highlights in a New Testament passage in the bible.
Can you give me a detailed summary of this passage?
How can the meaning of the biblical Greek words in this passage provide insights that aid our understanding? Explain the insights with examples.
What are the key words and phrases used in this passage, and how do they contribute to its meaning?
How does this passage relate to other passages in the Bible, both within the same book and in other books?
Please answer all relevant questions pertaining to the following passage.
You don't need to provide all the verses from the passage, as I am already familiar with it. 
I want your response focus on my questions.  However, do not repeat my questions word by word in your answer.

Please write in detail pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible OT Historical Context"] = """Bible Historical Context of an Old Testament passage in the bible.
In what ways does this passage speak to the struggles that Old Testament People faced in the time of its writing, and how does an understanding of its historical and cultural context help us to better interpret its meaning?
In what ways does a deeper comprehension of the culture of the Ancient Near East aid in our understanding of the passage? Give examples based on the content of the given passage.
How does comprehending the social, political, and religious environment of the Old Testament era, along with the distinct obstacles that the people of that time may have encountered in their daily lives, contribute to our interpretation of the given passage? Give examples based on the content of the given passage.
Please answer all relevant questions pertaining to the following passage.
Do not give me general message of the passage, as I am seeking specific insights as I am seeking specific insights about Old Testament People stugglings in view of historical context.
I already know the content of the passage.  Please do not repeat.  
Do not give me summary of the passage that is not relevant to the struggling or historical context.

Please write in detail pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible NT Historical Context"] = """Bible Historical Context of a New Testament passage in the bible.
In what ways does this passage speak to the struggles that early Christians faced in the time of its writing, and how does an understanding of its historical and cultural context help us to better interpret its meaning?
In what ways does a deeper comprehension of the Jewish culture aid in our understanding of the passage? Give examples based on the content of the given passage.
How does comprehending the social, political, and religious environment of the New Testament era, along with the distinct obstacles that the people of that time may have encountered in their daily lives, contribute to our interpretation of the given passage? Give examples based on the content of the given passage.
Please answer all relevant questions pertaining to the following passage.
Do not give me general message of the passage, as I am seeking specific insights as I am seeking specific insights about Christian stugglings in view of historical context.
I already know the content of the passage.  Please do not repeat.  
Do not give me summary of the passage that is not relevant to the struggling or historical context.

Please write in detail pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Themes"] = """Bible Themes in bible passage.
What are the key themes expressed in this passage?  Please elaborate on each theme in details.  
Explain how biblical Hebrew studies help us understand each theme.  Povide illustration that aid our understanding, if possible.
What are the theological implications of this passage, and how does it contribute to our understanding of God's character and plan for humanity?
How does other passages in the bible contribute to our comprehension of this passage? Give examples and quote related passages.
How does the message conveyed in this passage impact our connection with God?
Please answer all relevant questions pertaining to the following passage.
Do not give me historical context of the passage, as I already know them. 
Do not give me general information about the passage, as I am seeking specific themes, theological implications and connection with God.

Please answer all relevant questions pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible OT Themes"] = """Bible Themes in an Old Testament passage.
What are the key themes expressed in this passage?  Please elaborate on each theme in details.  
Explain how biblical Hebrew studies help us understand each theme.  Povide illustration that aid our understanding, if possible.
What are the theological implications of this passage, and how does it contribute to our understanding of God's character and plan for humanity?
How does the New Testament contribute to our comprehension of this Old Testament passage? Give examples and quote related New Testament passages.
How does the message conveyed in this passage impact our connection with God?
Please answer all relevant questions pertaining to the following passage.
Do not give me historical context of the passage, as I already know them. 
Do not give me general information about the passage, as I am seeking specific themes, theological implications and connection with God.

Please answer all relevant questions pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible NT Themes"] = """Bible Themes in a New Testament passage.
What are the key themes expressed in this passage?  Please elaborate on each theme in details.  
Explain how biblical Greek studies help us understand each theme.  Povide illustration that aid our understanding, if possible.
What are the theological implications of this passage, and how does it contribute to our understanding of God's character and plan for humanity?
How does the Old Testament contribute to our comprehension of this New Testament passage? Give examples and quote related Old Testament passages.
How does the message conveyed in this passage impact our connection with God?
Please answer all relevant questions pertaining to the following passage.
Do not give me historical context of the passage, as I already know them. 
Do not give me general information about the passage, as I am seeking specific themes, theological implications and connection with God.

Please answer all relevant questions pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Application"] = """Provide detailed applications of a bible passages, without general introduction or summary.

Please address the following questions in your answer:
How can I relate this passage to my own daily life and personal circumstances?
How can I apply the principles and teachings of this passage to my relationships with God and others?
What can I do to apply the lessons from this passage in my daily life?
Are there any practical steps or behaviors that I can develop or change based on this passage?

Please answer all relevant questions pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Sermon"] = """Write a sermon with the following questions in mind:
1. What is the context of the passage? Who wrote it, to whom was it written, and what historical or cultural background is important to know?
2. What is the main message or theme of the passage? How does it relate to the overall message of the Bible?
3. What is the message or lesson that you want the congregation to take away from the sermon?
4. How can I make the sermon relevant and applicable to the lives of the congregation members?
5. What are some relevant stories, personal experiences, or examples that can be used to illustrate the main points of the sermon?
6. What are some potential challenges or objections that someone might have to the message of the sermon, and how can those be addressed?
7. Are there any important theological or doctrinal principles that need to be emphasized or clarified in relation to the passage?

Please write pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Devotion"] = """Write a devotion on a bible passage, based on the following guidance:
1. Get a full understanding of its meaning and context.
2. Reflect on how the passage applies to your own life and experiences.
3. Consider what message or lesson God may be trying to communicate through the passage.
4. Decide on a specific theme or topic you want to focus on in your devotion, based on the Bible passage.
5. Use personal anecdotes, relevant scripture references, and practical applications to help illustrate and reinforce your message.
6. End your devotion with a call to action or a prayer that encourages readers to apply the lesson to their own lives.
7. Edit and revise your devotion to ensure that it is clear, concise, and impactful.
I am already familiar with the contents of the passage, please refrain from providing general introduction or summary.
I want deep insights about devotions.

Please write pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Prayer"] = """Write a prayer pertaining to the following content in reference to the Bible:

    # Content
"""

    config.predefinedContexts["Bible Short Prayer"] = """Write a prayer pertaining to the following content in reference to the Bible.
(Keep the prayer short and do not make it longer than a paragraph.)

    # Content
"""

    config.predefinedContexts["Bible Review Questions"] = """Assist me to prepare materials for leading a bible study group.
I'm looking for specific questions that focus on a particular passage, rather than general bible study questions. Could you help me with that?
I'm hoping to facilitate a meaningful discussion and deeper understanding of this passage through targeted questions. Could you guide me in creating those questions?
Remember, I am already familiar with the contents of the passage, please refrain from providing me with general information or summary. Please give me review questions for bible studies directly.

Please answer all relevant questions pertaining to the following passage:

    # Passage
"""

    config.predefinedContexts["Bible Key Words"] = """Identify key words in the content given below.
Elaborate on their importance in comprehending the context and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.

    # Content
"""

    config.predefinedContexts["Bible Key Themes"] = """Identify key themes or key messages in the content given below.
Elaborate on their importance in comprehending the content given below and the bible as a whole.
I want your elaboration to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.

    # Content
"""

    config.predefinedContexts["Bible Theology"] = """Please write the theological messages conveyed in the content given below, in reference to the Bible.
In addition, explain the significance of the theological messages in the bible.
I want your writing to be comprehensive and informative.
Remember, in your writing, please provide me with concrete examples from the Bible and the bible references from the text you are citing.

    # Content
"""

    config.predefinedContexts["Bible Promises"] = """Quote relevant Bible promises in relation to the content given below.
Explain how these promises are meant to provide comfort, hope, and guidance in my life.

    # Content
"""

    config.predefinedContexts["Bible Passages"] = """Quote relevant Bible passages in relation to the content given below given below. Explain how these passages are related to the given content.

    # Content
"""

    config.predefinedContexts["Bible Thought Progression"] = """Bible Thought Progression of a bible book / chapter / passage.
Provide a detailed overview of the author's thought progression in effectively conveying the key messages of the following book / chapter / passage:

    # Book / Chapter / Passage
"""

    config.predefinedContexts["Bible Canonical Context"] = """Bible Canonical Context of a bible book / chapter / passage.
How is this book / chapter / passage connected or linked with other books in the Bible?
What is the canonical context of this given book / chapter / passage in light of the whole canon of the bible?
How does this book / chapter / passage fit into the larger Biblical story in light of the whole canon of the bible?
                               
Please answer all relevant questions pertaining to the following book / chapter / passage with concrete examples:

    # Book / Chapter / Passage
"""

    # Predefined System Messages
    config.predefinedChatSystemMessages["Pastor Prayers"] = "I would like you to pray like the best church pastor. Please ensure that your responses to all my requests for prayer are always in the first person, so I can pray them directly."

    config.predefinedChatSystemMessages["Bible Quotes"] = "You always quote multiple bible verses that are relevant to my inputs."

    config.predefinedChatSystemMessages["Bible Translator"] = """I want you to act as an biblical translator. I will speak to you in english and you will translate it and answer in the corrected and improved version of my text, in a biblical dialect. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, biblical words and sentences. Keep the meaning same. I want you to only reply the correction, the improvements and nothing else, do not write explanations."""

    config.predefinedChatSystemMessages["Bible Professor"] = """I would like you to communicate with me in the manner of a distinguished Oxford University professor specializing in biblical studies. Please engage with me accordingly."""

    config.predefinedChatSystemMessages["Bible Theologian"] = """I would like you to communicate with me in the manner of a distinguished Cambridge University professor and theologian specializing in biblical theology. Please engage with me accordingly."""

    config.predefinedChatSystemMessages["Billy Graham"] = """I want you to speak like Billy Graham, the Amercian evangelist. Please incorporate his speaking style, values, and thoughts in our interaction."""
