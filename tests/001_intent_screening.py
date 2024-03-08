import ollama
from ollama import Options

promptPrefix = """Answer either {"answer": "YES"} or {"answer": "NO"} in JSON format, to tell weather you can resolve my request. 
Answer {"answer": "NO"} if you are not provided with adequate context or knowledge base to answer my request.
Answer {"answer": "NO"} if my request requires access to real-time or device information that you are not provided with.
Answer {"answer": "NO"} if you don't have ability to execute the requested task.
Answer {"answer": "YES"} if you have adequate provided context or knowledge base to provide a direct answer. 

REMEMBER: 
Response with a JSON string that contains a single key only, i.e. "answer", and its value must be either "YES" or "NO". Therefore, your reponse can ONLY be either {"answer": "YES"} or {"answer": "NO"}, without the actual answer or extra information. 
 
HERE IS MY REQUEST:

"""

prompt = """
What time is it now?
"""

def test():
    completion = ollama.chat(
        #keep_alive=0,
        model="llama2",
        messages=[
            #{
            #    "role": "system",
            #    "content": "Current time: 16:05",
            #},
            {
                "role": "user",
                "content": promptPrefix + prompt,
            },
        ],
        format="json",
        stream=False,
        options=Options(
            temperature=0.0,
            num_ctx=100000,
            num_predict=10,
        ),
    )
    print(completion["message"]["content"])

test()

# Notes:
# Cases mistaken as "NO"：
# 1. greeting
# 2. translation
# 3. simple calculation