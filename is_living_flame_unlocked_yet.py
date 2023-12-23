#!/usr/bin/python3

# requirements: requests, pygame, plyers
import os
import pprint
pp = pprint.PrettyPrinter(indent=2)
import time

import requests
from requests.auth import HTTPBasicAuth
import pygame # Play sound mp3
from plyer import notification # Send desktop notification
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_access_token():
    try:
        # Make a POST request to the token endpoint to obtain an access token
        response = requests.post(
            "https://eu.battle.net/oauth/token",
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
            data={"grant_type": "client_credentials"}
        )

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Error getting access token: {response.status_code} - {response.text}")
            return None

    except requests.ConnectionError as e:
        print(f"Connection error: {e}")
        return None

def get_locked_status_living_flame(access_token):
    try:
        # Make a GET request to the WoW realm index endpoint with the access token
        # 5827 Living Flame
        # 5828 Crusader Strike
        response = requests.get("https://eu.api.blizzard.com/data/wow/connected-realm/5827",
            params={"access_token": access_token,
                    "namespace": "dynamic-classic1x-eu",
                    "locale": "en_GB",
                    "region": "eu"
            })

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response = response.json()
            try:
                type = response['population']['type']
            except KeyError:
                print("KeyError:\n")
                pp.pprint(response)
                return None, response
            if type == "LOCKED":
                return True, response
            else:
                return False, response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None, None
    except requests.ConnectionError as e:
        print(f"Connection error: {e}")
        return None, None

def play_sound():
    pygame.mixer.init()
    pygame.mixer.music.load("alert_sound.mp3")
    pygame.mixer.music.play(loops=3)

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon=None,
        timeout=5,  # seconds
    )

if __name__ == "__main__":
    access_token = get_access_token()
    if access_token:
        count = 0
        start_time = time.time()  # Record the start time
        while True:
            count+=1
            elapsed_time = time.time() - start_time
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            print(f"Checking if unlocked.. elapsed_time: {formatted_time} requests: {count:,}", end="\r")

            is_locked_for_new_characters, response = get_locked_status_living_flame(access_token)
            if is_locked_for_new_characters is not None and is_locked_for_new_characters is False:
                pp.pprint(response)
                play_sound()
                while True:
                    show_notification("🔥Living Flame🔥", "Realm is not LOCKED!")
                    time.sleep(5)
            time.sleep(2)

