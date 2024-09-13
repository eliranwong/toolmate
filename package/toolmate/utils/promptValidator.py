from toolmate import config, count_tokens_from_messages, count_tokens_from_functions, tokenLimits
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.application import run_in_terminal
import tiktoken
import re

class TokenValidator(Validator):
    def validate(self, document):
        #current_buffer = get_app().current_buffer
        currentInput = document.text
        if not config.dynamicTokenCount or not currentInput or currentInput.lower() in (config.exit_entry, config.cancel_entry, ".new", ".share", ".save"):
            pass
        else:
            try:
                encoding = tiktoken.encoding_for_model(config.chatGPTApiModel)
            except:
                encoding = tiktoken.get_encoding("cl100k_base")
            ''' does not apply for multiple tool cases
            no_function_call_pattern = "\[NO_TOOL\]|\[CHAT\]|\[CHAT_[^\[\]]+?\]"
            #if "[NO_TOOL]" in currentInput:
            if re.search(no_function_call_pattern, currentInput):
                availableFunctionTokens = 0
                #currentInput = currentInput.replace("[NO_TOOL]", "")
                currentInput = re.sub(no_function_call_pattern, "", currentInput)
            else:
                availableFunctionTokens = count_tokens_from_functions(config.toolFunctionSchemas)
            '''
            availableFunctionTokens = count_tokens_from_functions(config.toolFunctionSchemas)
            currentInputTokens = len(encoding.encode(config.fineTuneUserInput(currentInput)))
            loadedMessageTokens = count_tokens_from_messages(config.currentMessages)
            selectedModelLimit = tokenLimits[config.chatGPTApiModel]
            #estimatedAvailableTokens = selectedModelLimit - availableFunctionTokens - loadedMessageTokens - currentInputTokens

            config.dynamicToolBarText = f""" Tokens: {(availableFunctionTokens + loadedMessageTokens + currentInputTokens)}/{selectedModelLimit} {str(config.hotkey_display_key_combo).replace("'", "")} shortcuts """
            #if config.conversationStarted:
            #    config.dynamicToolBarText = config.dynamicToolBarText + " [ctrl+n] new"
            if selectedModelLimit - (availableFunctionTokens + loadedMessageTokens + currentInputTokens) >= config.chatGPTApiMinTokens:
                pass
            else:
                run_in_terminal(lambda: print(f"""Press '{str(config.hotkey_new).replace("'", "")[1:-1]}' to start a new chat!"""))
                raise ValidationError(message='Token limit reached!', cursor_position=document.cursor_position)

class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        elif text and not text.isdigit():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This entry accepts numbers only!', cursor_position=i)


class FloatValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        try:
            float(text)
        except:
            raise ValidationError(message='This entry accepts floating point numbers only!', cursor_position=0)


class NoAlphaValidator(Validator):
    def validate(self, document):
        text = document.text

        if text.lower() in (config.exit_entry, config.cancel_entry):
            pass
        elif text and text.isalpha():
            i = 0

            # Get index of first non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if c.isalpha():
                    break

            raise ValidationError(message='This entry does not accept alphabet letters!', cursor_position=i)