import argparse
import time

# from whisper_mic import WhisperMic


from FriendlyAgent import Friend

import json
from utils import gather_objective, logger


def main():
    print("Creating ...")
    driver = Friend()

    driver.navigate("https://www.google.com")


    objective, action, typing = gather_objective(), None, False
    print(f"Understood. Objective is {objective}")  

    count = 0
    while True:

        typing = action is not None and "typing" in action 
        if not typing:         
            logger.info("capture photo")
            screenshot = driver.capture()

        if typing:
            count+=1
        else: 
            count=0
        if count==2:
            typing = False
            count = 0

        logger.debug("Getting actions for the given objective...")
        action = driver.next_action(screenshot, objective, typing=typing)
        
        response =  driver.act(action)
        if (response):
            print(f"Response is {action['done']}")
            return



if __name__ == "__main__":
    main()