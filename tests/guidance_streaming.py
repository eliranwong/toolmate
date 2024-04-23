from freegenius import config
from guidance import models, gen, select

# test guidance streaming feature
# https://guidance.readthedocs.io/en/latest/example_notebooks/tutorials/intro_to_guidance.html#Streaming

lm = models.LlamaCpp(config.llamacppChatModel_model_path, echo = False).stream()

lm += f'Q: Do you want a joke or a poem?\nA: A ' + select(['joke', 'poem'], name="choice")

for i in lm:
    choice = i.get("choice", "")
    if choice:
        print(choice, end='', flush=True)

print("")

lm += f"Q: Write a short {choice}:\nA: {gen(name=choice, stop='Q:', max_tokens=4096)}"

for i in lm:
    print("ALL:", i)
    print(i.get(choice, ""), end='', flush=True)

print("")