"""
ToolMate AI Plugin - character analysis

add contexts for character analysis

"""

from toolmate import config

config.predefinedContexts["Character - Close Reading"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Close Reading' to analyze the character given in my input. (Remember, Close Reading involves analyzing the text carefully to gather information about the character. It focuses on examining the character's actions, dialogue, thoughts, and interactions with other characters.)
Below is my input:
"""

config.predefinedContexts["Character - Character Analysis"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Character Analysis' to analyze the character given in my input. (Remember, Character Analysis involves examining the character's traits, motivations, and development throughout the narrative. It may include analyzing the character's background, relationships, and conflicts.)
Below is my input:
"""

config.predefinedContexts["Character - Archetypal Analysis"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Archetypal Analysis' to analyze the character given in my input. (Remember, Archetypal Analysis involves identifying and analyzing the character's archetype or symbolic role in the narrative. It explores how the character embodies certain universal themes or patterns.)
Below is my input:
"""

config.predefinedContexts["Character - Psychological Analysis"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Psychological Analysis' to analyze the character given in my input. (Remember, Psychological Analysis involves applying psychological theories and concepts to understand the character's behavior and motivations. It may involve exploring the character's personality, desires, fears, and conflicts.)
Below is my input:
"""

config.predefinedContexts["Character - Historical and Cultural Analysis"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Historical and Cultural Analysis' to analyze the character given in my input. (Remember, Historical and Cultural Analysis involves examining the character in the context of the historical and cultural setting of the narrative. It explores how the character's actions and beliefs may be influenced by their social, political, or cultural environment.)
Below is my input:
"""

config.predefinedContexts["Character - Comparative Analysis"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply 'Comparative Analysis' to analyze the character given in my input. (Remember, Comparative Analysis involves comparing the character to other characters in the narrative or to characters from other texts. It may focus on similarities and differences in their traits, roles, or thematic significance.)
Below is my input:
"""

config.predefinedContexts["Character - Narrative Therapy 1"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply the principles of narrative therapy to analyze the character given in my input. Please explore the character's narrative, beliefs, values, and the meanings they attribute to their experiences. Please also give insights into their identity, relationships, struggles, and potential for growth or change.
Below is my input:
"""

config.predefinedContexts["Character - Narrative Therapy 2"] = """@chat Use the following step-by-step instructions to respond to my inputs.
Step 1: Give me a brief summary of the narrative.
Step 2: Apply principles of Narrative Therapy, that are 1) Externalizing Problems, 2) Re-authoring Stories, 3) Deconstructing Dominant Discourses, 4) Encouraging Unique Outcomes, 5) Externalizing and Privileging Alternative Stories, to analyze the given character in my input.
Below is my input:
"""

config.predefinedContexts["Character - Narrative Therapy 3"] = """@chat Apply narrative therapy to analyze this character below:
"""

"""
The key principles of narrative therapy include:

1. Externalizing Problems: Instead of seeing problems as inherent to the individual, narrative therapy views them as separate entities that can be examined and addressed objectively.

2. Re-authoring Stories: Individuals are encouraged to reframe their narratives and create new meanings and understandings of their experiences. This can help shift focus from problems to strengths and resources.

3. Deconstructing Dominant Discourses: The therapy aims to challenge societal and cultural narratives that may contribute to individuals feeling marginalized or oppressed. By questioning these dominant discourses, individuals can gain a sense of agency and empowerment.

4. Encouraging Unique Outcomes: Narrative therapy seeks to identify and amplify unique outcomes or instances in which the individual has exhibited resilience or problem-solving skills. This helps to counterbalance the dominant problem-focused narratives.

5. Externalizing and Privileging Alternative Stories: The therapist collaborates with the individual to explore alternative stories or narratives that challenge the dominant problem-saturated ones. These alternative stories highlight the individual's strengths, values, and preferred ways of being.

These principles guide the practice of narrative therapy and help individuals to explore and transform their stories in ways that promote healing and growth.
"""