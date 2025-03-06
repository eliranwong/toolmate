from agentmake import agentmake, DEFAULT_AI_BACKEND
import argparse

def lite():
    main(agent="auto_tool_selection")

def main(agent="super"):
    # Create the parser
    parser = argparse.ArgumentParser(description = """ToolMate AI cli options""")
    # Add arguments for running `agentmake` function
    parser.add_argument("default", nargs="+", default=None, help="user prompt")
    parser.add_argument("-b", "--backend", action="store", dest="backend", help="AI backend")
    parser.add_argument("-m", "--model", action="store", dest="model", help="AI model")
    parser.add_argument("-mka", "--model_keep_alive", action="store", dest="model_keep_alive", help="time to keep the model loaded in memory; applicable to ollama only")
    parser.add_argument("-tem", "--temperature", action='store', dest="temperature", type=float, help="temperature for sampling")
    parser.add_argument("-mt", "--max_tokens", action='store', dest="max_tokens", type=int, help="maximum number of tokens to generate")
    parser.add_argument("-cw", "--context_window", action='store', dest="context_window", type=int, help="context window size; applicable to ollama only")
    parser.add_argument("-bs", "--batch_size", action='store', dest="batch_size", type=int, help="batch size; applicable to ollama only")
    parser.add_argument("-pre", "--prefill", action='append', dest="prefill", help="prefill of assistant message; applicable to deepseek, mistral, ollama and groq only")
    parser.add_argument("-sto", "--stop", action='append', dest="stop", help="stop sequences")
    parser.add_argument("-key", "--api_key", action="store", dest="api_key", help="API key")
    parser.add_argument("-end", "--api_endpoint", action="store", dest="api_endpoint", help="API endpoint")
    parser.add_argument("-pi", "--api_project_id", action="store", dest="api_project_id", help="project id; applicable to Vertex AI only")
    parser.add_argument("-sl", "--api_service_location", action="store", dest="api_service_location", help="cloud service location; applicable to Vertex AI only")
    parser.add_argument("-tim", "--api_timeout", action="store", dest="api_timeout", type=float, help="timeout for API request")
    parser.add_argument("-ww", "--word_wrap", action="store_true", dest="word_wrap", help="wrap output text according to current terminal width")
    #parser.add_argument("-p", "--prompts", action="store_true", dest="prompts", help="enable mult-turn prompts for the user interface")
    #parser.add_argument("-u", "--upgrade", action="store_true", dest="upgrade", help="upgrade `agentmake` pip package")
    # Parse arguments
    args = parser.parse_args()

    user_prompt = " ".join(args.default) if args.default is not None else ""
    if user_prompt:
        agentmake(
            messages=user_prompt,
            backend=args.backend if args.backend else DEFAULT_AI_BACKEND,
            model=args.model,
            model_keep_alive=args.model_keep_alive,
            agent=agent,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            context_window=args.context_window,
            batch_size=args.batch_size,
            prefill=args.prefill,
            stop=args.stop,
            api_key=args.api_key,
            api_endpoint=args.api_endpoint,
            api_project_id=args.api_project_id,
            api_service_location=args.api_service_location,
            api_timeout=int(args.api_timeout) if args.api_timeout and args.backend and args.backend in ("cohere", "mistral", "genai", "vertexai") else args.api_timeout,
            word_wrap=args.word_wrap,
            stream=True,
            print_on_terminal=True,
        )

if __name__ == "__main__":
    test = main()