import os
from llm import ask
import json
import re
import pylitex
from clipboard import read_clipboard, write_clipboard
import time

def extract_litex_code(proof_text):
    pattern = r'```litex\s*\n(.*?)\n```'
    matches = re.findall(pattern, proof_text, re.DOTALL)
    if matches:
        return matches[-1].strip()
    return ""

def load_prompt(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find file {filepath}")
        return ""
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def tui_choice(choices: list[str], prompt: str = "Enter your choice: ", error_msg: str = "Invalid choice. Please try again.") -> str:
    print(f"\n\033[32m{time.strftime('%Y-%m-%d %H:%M:%S')}\033[0m\nPlease choose one of the following options:")
    if len(choices) == 0:
        print("No choices available. Please try again.")
        return ""
    for i, choice in enumerate(choices):
        print(f"{i+1}. {choice}")
    while True:
        try:
            choice = int(input(prompt))
            if choice < 1 or choice > len(choices):
                print(error_msg)
                continue
            return choices[choice-1]
        except (ValueError, IndexError):
            print(error_msg)
    
def main(model: str = "deepseek-r1-250528"):
    topic = input("Enter the top of standard library: ")

    tutor = load_prompt('../prompt/tutor.txt')
    examples = load_prompt('../prompt/examples.txt')
    documentation = f"Tutorial:\n{tutor}\nHere's some examples:{examples}\n"

    prompt = f"""
Here's a machine proof language. Hereby's its documentation. Note that you must wrap your code with ```litex and ``` code block.
Notice that in Litex we don't have grammar like |a| for absolute value of a, we don't provide sin function, we don't use non-ascii letters like θ, Σ.
Now you'll cooperate with litex standard library. I'll give you the current standard library and some advices on how to add new functions to the library.
You will assist writing {topic} to the standard library. You should writing very carefully and detailed, because the Litex engine is simple and strict.
You can never use mathematical language. You should always be careful when using Litex Grammar. If you failed to follow the grammar, you'll get pubished.
User will give a request to add some new functions, you should only print the new functions, do not repeat the existing functions.
The Documentation is: {documentation}
""".strip()

    current_library = ""

    while True:
        step = tui_choice([
            "Import code from clipboard",
            "Copy code to clipboard",
            "Clear code",
            "Verify code",
            "Ask LLM to generate code",
            "Exit"
        ])
        if step == "Import code from clipboard":
            code = read_clipboard()
            if code == "":
                print("No code in clipboard. Please try again.")
                continue
            current_library += f"\n{code}"
        elif step == "Copy code to clipboard":
            write_clipboard(current_library)
            print("Code copied to clipboard.")
        elif step == "Clear code":
            current_library = ""
        elif step == "Verify code":
            result = pylitex.run(current_library)
            if result["success"]:
                print("Code verified \033[32mSUCCESSFULLY.\033[0m")
            else:
                print("Code verification \033[31mFAILED.\033[0m")
                op = input("Type 'y' to view the error message: ")
                if op == "y":
                    print("\n".join(result["message"].split("\n")[-50:]))
                else:
                    continue
        elif step == "Ask LLM to generate code":
            user_prompt = input("Enter your prompt: ")
            full_prompt = f"{prompt}\nCurrent library: {current_library}\nUser prompt: {user_prompt}"
            try:
                resp = ask(full_prompt, model=model)
                litex_code = extract_litex_code(resp)
                new_library = current_library + f"\n{litex_code}"
                result = pylitex.run(new_library)
                if result["success"]:
                    print("The LLM generated code verified \033[32mSUCCESSFULLY.\033[0m")
                    print("\033[32m===== begin =====\033[0m")
                    print(resp)
                    print("\033[32m====== end ======\033[0m")
                    user_op = input("Type 'y' to add the code to the library: ")
                    if user_op == "y":
                        current_library = new_library
                    else:
                        continue
                else:
                    print("The LLM generated code verification \033[31mFAILED.\033[0m")
                    print("\033[31m===== begin =====\033[0m")
                    print(resp)
                    print("\033[31m====== end ======\033[0m")
                    op = input("Type 'y' to view the error message: ")
                    if op == "y":
                        print("\n".join(result["message"].split("\n")[-50:]))
                    else:
                        continue

            except Exception as e:
                print(f"Error asking LLM: {e}")
                continue
        elif step == "Exit":
            break

if __name__ == "__main__":
    main()