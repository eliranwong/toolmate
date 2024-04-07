import ollama
from ollama import Options
from freegenius import config


def screen_user_request(user_request: str, model="mistral") -> None:
    """
    Check if the applied model is able to resolve user request directly or not.
    Assistant delivers a direct answer if the model is capable to resolve the request.
    Look further to extend assistant's capabilities if the requested task exceeds the model's limits.
    """
    if user_request:

        prompt_prefix = """Answer either {"answer": "YES"} or {"answer": "NO"} in JSON format, to tell weather you can resolve my request. 
Answer {"answer": "NO"} if you are not provided with adequate context or knowledge base to answer my request.
Answer {"answer": "NO"} if my request requires access to real-time or device information that you are not provided with.
Answer {"answer": "NO"} if you don't have ability to execute the requested task.
Answer {"answer": "YES"} if you have adequate provided context or knowledge base to provide a direct answer. 

REMEMBER: 
Response with a JSON string that contains a single key only, i.e. "answer", and its value must be either "YES" or "NO". Therefore, your reponse can ONLY be either {"answer": "YES"} or {"answer": "NO"}, without the actual answer or extra information. 

HERE IS MY REQUEST:

"""

        completion = ollama.chat(
            #keep_alive=0,
            model=model,
            messages=[
                #{
                #    "role": "system",
                #    "content": "Current time: 16:05",
                #},
                {
                    "role": "user",
                    "content": prompt_prefix + user_request,
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

if __name__ == "__main__":
    config.ollamaMainModel = "mistral"
    user_request = """What time is it now?"""
    screen_user_request(user_request)

# Notes:
# Tested model: llama2
# Cases mistaken as "NO":
# 1. greeting
# 2. translation
# 3. simple calculation