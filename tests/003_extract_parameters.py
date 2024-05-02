import json, traceback
from freegenius import config
import ollama
from ollama import Options


def getDictionaryOutput(messages, **kwargs):
    try:
        completion = ollama.chat(
            #keep_alive=0,
            model=config.ollamaMainModel,
            messages=messages,
            format="json",
            stream=False,
            options=Options(
                temperature=0.0,
                num_ctx=100000,
                num_predict=-1,
            ),
            **kwargs,
        )
        jsonOutput = completion["message"]["content"]
        responseDict = json.loads(jsonOutput)
        print(responseDict)
        return responseDict
    except:
        print(traceback.format_exc())
        return {}

def extractToolParameters(schema: dict, userInput: str, ongoingMessages: list = []) -> dict:
    """
    Extract action parameters
    """
    def getPrompt(template, parameter, parameterDetails):
        return f"""Use the following template to response in JSON format:

{template}

YOU MUST FOLLOW THESE INSTRUCTIONS CAREFULLY.                                        
<instructions>        
1. Based on my input{" and our ongoing conversation" if ongoingMessages else ""}, fill in the value of the key '{parameter}' in the JSON string.
  - description: {parameterDetails['description']}
  - type: {parameterDetails['type']}
2. Return the JSON string to me, without additional notes or explanation
</instructions>

Here is my input:

"""
    template = {}
    for parameter in schema:
        parameterDetails = schema[parameter]
        template[parameter] = "" if parameterDetails['type'] == "string" else []
        messages = [
            *ongoingMessages,
            {"role": "user", "content": f"""{getPrompt(template, parameter, parameterDetails)}{userInput}"""},
        ]
        template = getDictionaryOutput(messages)
    return template

if __name__ == "__main__":
    config.ollamaMainModel = "mistral"
    #parameters = {'code': {'type': 'string', 'description': 'Python code that integrates package pendulum to resolve my query'}}
    #print(extractToolParameters(parameters, "What time is it now?"))
    schema = {'email': {'type': 'string', 'description': "The email application. Return 'gmail' if not given.", 'enum': ['gmail', 'outlook']}, 'recipient': {'type': 'string', 'description': 'The recipient of the email.'}, 'subject': {'type': 'string', 'description': 'Give a title to the email.'}, 'body': {'type': 'string', 'description': 'The body or content of the email.'}}
    parameters = extractToolParameters(schema, "Email an appreciation message to Eliran Wong, whose email is support@letmedoit.ai")

# result
#{'email': 'support@letmedoit.ai'}
#{'email': 'support@letmedoit.ai', 'recipient': 'Eliran Wong'}
#{'email': 'support@letmedoit.ai', 'recipient': 'Eliran Wong', 'subject': 'Appreciation Message'}
#{'email': 'support@letmedoit.ai', 'recipient': 'Eliran Wong', 'subject': 'Appreciation Message', 'body': 'Dear Eliran,\n\nI wanted to take a moment to express my appreciation for your exceptional support and dedication to our project. Your expertise and commitment have been invaluable, and I am grateful for the positive impact you have made on our team.\n\nThank you for your hard work and continued contributions.\n\nBest regards,'}