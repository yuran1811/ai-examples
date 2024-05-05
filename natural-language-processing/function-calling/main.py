import google.generativeai as gen_ai
import google.ai.generativelanguage as glm

from funcs import *

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
FUNCS = {
    "multiply": multiply,
    "plus": plus,
    "power": power,
    "sqr": sqr,
}
MODEL_NAME = "gemini-1.0-pro"

gen_ai.configure(api_key=GOOGLE_API_KEY)

glm_tools = glm.Tool(
    function_declarations=[
        glm.FunctionDeclaration(
            name="multiply",
            description="return the product of two numbers",
            parameters=glm.Schema(
                type=glm.Type.OBJECT,
                properties={
                    "a": glm.Schema(type=glm.Type.NUMBER),
                    "b": glm.Schema(type=glm.Type.NUMBER),
                },
                required=["a", "b"],
            ),
        ),
        glm.FunctionDeclaration(
            name="plus",
            description="return the sum of two numbers",
            parameters=glm.Schema(
                type=glm.Type.OBJECT,
                properties={
                    "a": glm.Schema(type=glm.Type.NUMBER),
                    "b": glm.Schema(type=glm.Type.NUMBER),
                },
                required=["a", "b"],
            ),
        ),
        glm.FunctionDeclaration(
            name="power",
            description="return the power of a number",
            parameters=glm.Schema(
                type=glm.Type.OBJECT,
                properties={
                    "a": glm.Schema(type=glm.Type.NUMBER),
                    "b": glm.Schema(type=glm.Type.NUMBER),
                },
                required=["a", "b"],
            ),
        ),
        glm.FunctionDeclaration(
            name="sqr",
            description="return the square of a number",
            parameters=glm.Schema(
                type=glm.Type.OBJECT,
                properties={
                    "a": glm.Schema(type=glm.Type.NUMBER),
                },
                required=["a"],
            ),
        ),
    ]
)

model = gen_ai.GenerativeModel(model_name=MODEL_NAME, tools=glm_tools)
chat = model.start_chat()

while True:
    chat_msg = input("You: ")
    if chat_msg == "exit":
        print("Goodbye! See you next time!")
        break

    response = chat.send_message(chat_msg)

    fc = response.candidates[0].content.parts[0].function_call
    name = fc.name

    if (name is None) or (name not in FUNCS):
        print("There is no matched function to call.")
        continue

    args = fc.args
    args_keys = args.keys()

    a = int(args["a"]) if "a" in args_keys else None
    b = int(args["b"]) if "b" in args_keys else None

    result = None

    if name == "multiply":
        if (a is None) or (b is None):
            print("Missing a or b arguments")
            continue
        print(f"Bot: Calling {name} with a={a}, b={b}...")
        result = multiply(a, b)
    elif name == "plus":
        if (a is None) or (b is None):
            print("Missing a or b arguments")
            continue
        print(f"Bot: Calling {name} with a={a}, b={b}...")
        result = plus(a, b)
    elif name == "power":
        if (a is None) or (b is None):
            print("Missing a or b arguments")
            continue
        print(f"Bot: Calling {name} with a={a}, b={b}...")
        result = power(a, b)
    elif name == "sqr":
        if a is None:
            print("Missing a argument")
            continue
        print(f"Bot: Calling {name} with a={a}...")
        result = sqr(a)
    else:
        print("There is no matched function to call.")
        continue

    if result is None:
        print("There is no matched function to call or no result to show.")
    else:
        print(f"Bot: Result is {result}")

    # response = chat.send_message(
    #     glm.Content(
    #         parts=[
    #             glm.Part(function_response=glm.FunctionResponse(
    #                 name=name, response={"result": result}
    #             ))
    #         ]
    #     )
    # )
