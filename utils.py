import json
from openai import OpenAI
client = OpenAI()

def ask_question(question, keys, *,identity="", containKey=True):
    response = client.chat.completions.create(
      model="gpt-4-turbo",
      response_format={ "type": "json_object" },
      messages=[
        {"role": "system", "content": f"You are a helpful assistant designed to output JSON. {identity}{containKey and f"Respond with only keys from the following list: [{keys}]"}"},
        {"role": "user", "content": question}
      ]
    )
    return json.loads(response.choices[0].message.content)

def completed_objective(objective):
    return ask_question(f'Is the following objective for you as an agent meant to execute tasks on the web clear? """{objective}""" Return true or false.', "clear")

def ask_for_more(objective):
    return ask_question(f'Given the following objective for you as an agent meant to execute tasks on the web """{objective}""", ask a question which would help you clear up what you need to do.', "question")

def combine(objective, objective2):
    return ask_question(f'Given the two following pieces of instruction- combine into a clear objective for you as an agent to execute tasks on the web ("""{objective}""" and """{objective2}""")', "objective")

def gather_objective():
    objective = input("What is the objective? ")
    while not completed_objective(objective)['clear']:
        question = ask_for_more(objective)['question']
        additional_context = input(f"{question} " )
        objective = combine(objective, f"Answer to '{question}' is '{additional_context}'")['objective']
    return objective


# Typing
def image_task_gather(objective, encoded_screenshot, typing=False):

        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"You need to choose which action to take to help a user do this task: {objective}. {agent_setup_typing if typing else agent_setup}",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_screenshot}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=100,
        )
        return response


agent_setup_typing = """
    You can type.
    Please respond with the message to write.
    You must respond in JSON only with no other fluff or bad things will happen.
    Do not return the JSON inside a code block. 
    The JSON keys MUST ONLY be ONE of type.
    """


agent_setup = """
    Your options are navigate, press, or done. 
    Navigate should take you to the specified URL. 
    Press takes strings where if you want to press on an object, 
    return the string with the yellow character sequence you want to press on.
    For presss, please only respond with the 1-2 letter sequence in the yellow box,
    and if there are multiple valid options choose the one you think a user would select. 
    When the page seems satisfactory, return done as a key with no value. 
    You must respond in JSON only with no other fluff or bad things will happen.
    Do not return the JSON inside a code block. 
    The JSON keys MUST ONLY be ONE of navigate, press, or done (and optionally, typing). 
    If you are pressing on an input box that you'll want to type into, also return 'typing' as a key with no value, but otherwise only return ONE key. 
    """



import logging

class LogLevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        # Only logs the specified level and above are passed.
        return record.levelno == self.level

# Creating a single logger
logger = logging.getLogger('custom_logger')
logger.setLevel(logging.DEBUG)  # Set the lowest level you want to capture

# Handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler('actions.log')
file_handler.setLevel(logging.DEBUG)

# Attaching filters
# Console handler will handle INFO level specifically for 'process'
process_filter = LogLevelFilter(logging.INFO)
console_handler.addFilter(process_filter)

# File handler will handle DEBUG level specifically for 'actions'
action_filter = LogLevelFilter(logging.DEBUG)
file_handler.addFilter(action_filter)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setting formatter to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adding handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)





import functools

def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Using the custom logger to log method calls
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        # logger.info(f"{func.__name__} returned: {result}")
        return result
    return wrapper

