import datetime
import json
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from discord.ext import commands
from random import Random
from pathlib import Path
from tempfile import gettempdir
import requests
import discord
import time
from colorama import init, Fore, Style

with open("appsettings.json", "r") as f:
    config = json.load(f) 

discord_bot_token = config["DiscordBotToken"]
image_path = config["ImagePath"]
mj_parameters = config["MjParameters"]
prompt_text = config["Prompt"]
server_id = config["ServerId"]
channel_id = config["ChannelId"]

preferences = {"download.default_directory": image_path,
               "download.prompt_for_download": False,
               "directory_upgrade": True}

chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument("--window-size=1480x560")
chromeOptions.add_experimental_option("prefs", preferences)

browser = webdriver.Chrome(options=chromeOptions)
client = commands.Bot(command_prefix="*", intents=discord.Intents.all())

@client.event
async def on_ready():
    os.system("cls")
    log_info("MidJourney bot has started")
    mj_auto_login()
    log_info("Successfuly logged in with discord")
    prompt()

latest_download_paths = []
images_from_job = 0

@client.event
async def on_message(message):
    global images_from_job

    if message.components == []:
        return

    if is_preview(message=message):
        log_operation("Preview received")
        custom_id = get_custom_id(message=message)
        upscale_previews(message_id=message.id, custom_id=custom_id)
    else:
        errors = 0
        try:
            upscaled_url = get_upscaled_url(message=message)
            log_operation("Upscaled image link fetched")
            download_image(upscaled_url)
            log_download("Image downloaded")
            images_from_job = images_from_job + 1
        except:
            errors += 1

        if errors + images_from_job == 4:
            log_operation("Requested new images")
            prompt()
            images_from_job = 0

def prompt():
    prompt_image(prompt=prompt_text, parameter_list=mj_parameters)
    log_operation("Image requested - " + prompt_text)

def is_preview(message):
    isPreview = True
    for component in message.components:
        for child in component.children:
            if child.url != None:
                isPreview = False
    return isPreview

def get_custom_id(message):
    for component in message.components:
        firstButton = component.children[0]
        customId = firstButton.custom_id.split("::")[4]
        return customId
    
def get_upscaled_url(message):
    url = None
    for component in message.components:
        for child in component.children:
            if child.label == "Web":
                url = child.url
    return url

def upscale_previews(custom_id: str, message_id: str):
    for image_number in range(1,5):
        payload = {"type": 3,
                    "guild_id": server_id,
                    "channel_id": channel_id,
                    "message_flags": 0,
                    "message_id": message_id,
                    "application_id": "936929561302675456",
                    "session_id": "45bc04dd4da37141a5f73dfbfaf5bdcf",
                    "data": {"component_type": 2,
                            "custom_id": "MJ::JOB::upsample::{}::{}".format(image_number, custom_id)}
                            }
        header = {
            'authorization' : "MTA5ODk0NTM4NDYxMDU0OTc3MQ.GpZkrh.gIH3KB8zPWG7XNCLWt6WYeIuDLqxGAOF0XiuMo"
        }
        requests.post("https://discord.com/api/v9/interactions", json=payload, headers=header)

def prompt_image(prompt: str, parameter_list):
    parameter = ""
    for param in parameter_list:
        parameter = parameter + param + " "

    parameter = parameter + "-"
    payload ={"type":2,"application_id":"936929561302675456","guild_id": server_id,
            "channel_id": channel_id,"session_id":"2fb980f65e5c9a77c96ca01f2c242cf6",
            "data":{"version":"1077969938624553050","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":prompt + " " + parameter}],
                    "application_command":{"id":"938956540159881230",
                                            "application_id":"936929561302675456",
                                            "version":"1077969938624553050",
                                            "default_permission":True,
                                            "default_member_permissions":None,
                                            "type":1,"nsfw":False,"name":"imagine","description":"Create images with Midjourney",
                                            "dm_permission":True,
                                            "options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":True}]},
            "attachments":[]}}


    header = {
        'authorization' : "MTA5ODk0NTM4NDYxMDU0OTc3MQ.GpZkrh.gIH3KB8zPWG7XNCLWt6WYeIuDLqxGAOF0XiuMo"
    }
    requests.post("https://discord.com/api/v9/interactions", json = payload, headers = header)

def mj_auto_login():
    global browser

    browser.get("https://www.midjourney.com/home")

    wait = WebDriverWait(browser, 10)
    wait.until(EC.title_is("Midjourney"))

    signin_button = browser.find_element(by=By.XPATH, value='//*[@id="__next"]/div[1]/main/div/div[1]/div[1]/div/div[1]/button')
    signin_button.click()

    #   wait = WebDriverWait(browser, 10)
    #   wait.until(EC.title_is("Discord"))

    email_field = None
    while email_field == None:
        try:
            email_field = browser.find_element(by=By.NAME, value='email')  
            email_field.send_keys("strattonoakmontart@gmail.com")
        except:
            time.sleep(1)

    password_fiel = browser.find_element(by=By.NAME, value='password')
    password_fiel.send_keys("MoneyGlitch42069!!")

    submit_button = browser.find_element(by=By.XPATH, value='//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div/div/div/form/div[2]/div/div[1]/div[2]/button[2]')
    submit_button.click()

    wait = WebDriverWait(browser, 10)
    wait.until(EC.title_is("Discord | Autorisiere den Zugang zu deinem Account"))
    time.sleep(1)

    authorize_button = browser.find_element(by=By.XPATH, value='//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div/div/div/div/div[2]/button[2]')
    authorize_button.click()

    wait = WebDriverWait(browser, 10)
    wait.until(EC.title_is("Your Midjourney Profile"))

def download_image(url: str):
    global browser

    time.sleep(1)

    browser.get(url)

    wait = WebDriverWait(browser, 10)
    wait.until(EC.title_contains("Midjourney:"))

    time.sleep(1)

    download_button = None
    while download_button == None:
        try:
            download_button = browser.find_element(by=By.XPATH, value='//*[@id="modalButtons"]/button[1]')
        except:
            log("Image not ready for download")
            log("Retry in 5 seconds...")
            time.sleep(5)
            browser.get(url=url)

    download_button.click()

    time.sleep(2)

def get_time_text():
    return datetime.datetime.now().strftime("[%H:%M:%S]")

def log_info(message: str):
    print(Fore.WHITE + get_time_text() + " " + "[Information]" + " " + message + Style.RESET_ALL)

def log_download(message: str):
    print(Fore.WHITE + get_time_text() + Fore.LIGHTBLUE_EX + " " + "[Download]" + " " + message + Style.RESET_ALL)

def log_operation(message: str):
    print(Fore.WHITE + get_time_text() + Fore.LIGHTCYAN_EX + " " + "[Operation]" + " " + message + Style.RESET_ALL)

def log_warning(message: str):
    print(Fore.WHITE + get_time_text() + Fore.LIGHTYELLOW_EX + " " + "[Operation]" + " " + message + Style.RESET_ALL)

client.run(discord_bot_token)