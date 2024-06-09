import base64
import json
import os
from io import BytesIO

import openai

from dotenv import load_dotenv
from PIL import Image

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
IMG_RES = 1080

from utils import ask_question, image_task_gather, logger, log_function_call



import time
from io import BytesIO
from openai import OpenAI

from PIL import Image
from playwright.sync_api import sync_playwright

vimium_path = "./vimium-master"


class Friend:
    def __init__(self, headless=False):
        print("initializing")
        self.context = (
            sync_playwright()
            .start()
            .chromium.launch_persistent_context(
                "",
                # Use this or someting similar if you want chrome history "/Users/vicky/Library/Application Support/Google/Chrome",
                headless=False,
                channel= 'chrome' ,
                args=[
                        '--new-instance',
                    f"--disable-extensions-except={vimium_path}",
                    f"--load-extension={vimium_path}",
                ],
                ignore_https_errors=True,
            )
        )
        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1080, "height": 720})
        self.client = OpenAI()

    #@log_function_call
    def act(self, action):
        print(action)
        # logger.info(action)

        if "done" in action:
            return True
        
        if "press" in action and "type" in action:
            self.click(action["press"])
            self.type(action["type"])
        
        if "navigate" in action:
            self.navigate(action["navigate"])

        elif "type" in action:
            self.type(action["type"])

        elif "press" in action:
            self.click(action["press"])


    #@log_function_call
    def navigate(self, url):
        self.page.goto(url=url if "://" in url else "https://" + url, timeout=60000)

    #@log_function_call
    def type(self, text):

        self.page.keyboard.type(text)
        self.page.keyboard.press("Enter")

    #@log_function_call
    def click(self, text):
        # print("right here")
        # time.sleep(10)
        # print(text)

        self.page.keyboard.type(text)
        # print("right then")
        # time.sleep(10)

    #@log_function_call
    def capture(self):
        self.page.keyboard.press("Escape")
        self.page.keyboard.type("f")
        time.sleep(2)

        screenshot = Image.open(BytesIO(self.page.screenshot())).convert("RGB")
        return screenshot

    #@log_function_call
    def next_action(self, screenshot, objective,typing=False):
        encoded_screenshot = self.encode_and_resize(screenshot)
        
        response = image_task_gather(f"{objective}. {typing and "You have already pressed on the text bar. Now just type what you need to type."}" , encoded_screenshot, typing=typing)

        try:
            json_response = json.loads(response.choices[0].message.content)

        except json.JSONDecodeError:
            print("Error: Invalid JSON response")
            cleaned_response = self.fix_json_response(response)


            try:
                cleaned_json_response = json.loads(cleaned_response.choices[0].message.content)
            
            except json.JSONDecodeError:
                print("Error: Invalid JSON response")
                return {}
            return cleaned_json_response
        return json_response

    # Function to encode the image
    #@log_function_call
    def encode_and_resize(self, image):
        W, H = image.size
        image = image.resize((IMG_RES, int(IMG_RES * H / W)))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return encoded_image

    #@log_function_call
    def fix_json_response(self, response):
        cleaned_response = ask_question(f"The invalid JSON response is: {response.choices[0].message.content}", "You need to fix the invalid JSON response to be valid JSON. You must respond in JSON only with no other fluff or bad things will happen. Do not return the JSON inside a code block", keys=False)
        # print(cleaned_response)
        return cleaned_response


