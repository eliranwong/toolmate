import openai, json

client = openai.OpenAI(
    base_url="http://localhost:8000/v1", # "http://<Your api-server IP>:port"
    api_key = "freegenius"
)

completion = client.chat.completions.create(
    model="freegenius",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that outputs in JSON."},
        {"role": "user", "content": "Who won the world series in 2020"},
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {"team_name": {"type": "string"}},
            "required": ["team_name"],
        },
    },
)

output = completion.choices[0].message.content

print(json.loads(output)["team_name"])