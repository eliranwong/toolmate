"""
ToolMate AI Plugin - ask sqlite

Ask SQLite file. To retrieve information from or make changes in a sqlite file, e.g. fetch data, update records, etc.

[TOOL_CALL]
"""

from toolmate import config, showErrors
from toolmate import print2
from toolmate.utils.call_llm import CallLLM
import os, sqlite3, json

def search_sqlite(function_args):
    db = function_args.get("path") # required
    request = function_args.get("request") # required
    if not os.path.isfile(db):
        return "[INVALID]"
    try:
        info = {}
        print2("Reading table information ...")
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            rows = cursor.fetchall()
            columns = [i[1] for i in rows]
            #cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            #example = cursor.fetchone()
            info[table_name] = {
                "name": table_name,
                "schema": rows,
                "columns labels": columns,
            }
            """if example:
                info[table_name] = {
                    "table name": table_name,
                    "table schema": rows,
                    "data row example": dict(zip(columns, example)),
                }
            else:
                info[table_name] = {
                    "table name": table_name,
                    "table schema": rows,
                }"""
        #if config.developer:
        #    print2("# Table information")
        #    pprint.pprint(info)
        info = json.dumps(info)

        if "describe tables" in request.lower():
            return info

        userInput = f"""Connect this sqlite file: sqlite file: {db}

And run python code to resolve my request: {request}

Please consider individual table information below for code generation:
{info}"""
        _, function_call_response = CallLLM.getSingleFunctionCallResponse(userInput, "task")
        return function_call_response
    except:
        showErrors()
        return "[INVALID]"

functionSignature = {
    "examples": [
        "connect SQLite",
        "search SQLite",
    ],
    "name": "search_sqlite",
    "description": f'''Search or manage SQLite file, e.g. fetch data, update records, etc. Remember, use this function ONLY IF I provide you with a sqlite file path.''',
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path of the sqlite file",
            },
            "request": {
                "type": "string",
                "description": "The request about fetching data or making changes in the sqlite file, including all available supplementary information in detail, if any.  If there is no specific request apart from connection or query about table schema / information, return 'Describe tables' without extra comment or information.",
            },
        },
        "required": ["path", "request"],
    },
}

config.addToolCall(signature=functionSignature, method=search_sqlite)

config.inputSuggestions.append("""@search_sqlite Connect the following SQLite file and tell me about the tables that it contains:
\n""")
