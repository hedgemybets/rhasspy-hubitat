"""
Rhasspy Intent Event Handler for Hubitat

    This program provides integration between Rhasspy and Hubitat by listening to the Rhasspy MQTT event service for intents to handle and Hubitat's Maker API app to control the appropriate devices in Hubitat.

    The intents to be handled by this application are triggered by voice queries to Rhasspy such as:

    -Turn on|off the TV (turns on a virtual switch used by a Hubitat rule to control the TV, AV receiver, and Tivo)
    -Set the <fan name> to low|medium low|medium|medium high|high
    -Turn on|off the <light_name>
    -Set the <light_name> to <number> percent
    -Open|close the shades|blinds
    -Turn on|off music
    -Play some <music genre or playlist>
    -Change the channel to <tv_channel>

    The intents and entities used must first be defined in the sentences.ini configuration in Rhasspy.
    The devices you want to control need to be selected in Maker API app in Hubitat.

    For initialization, this application makes a call to the Maker API to obtain all device details for later use. This means that the device names used in the Rhasspy sentences.ini config must match although they can be lower case in sentences.ini.

    Future Enhancement: This also supports 2016 and later Samsung TVs that are connected via Ethernet or WiFi. This allows selecting Samsung applications like Prime Video or Plex server, by lookup of the list of installed apps to find the numeric codes required to select an app.

Release notes:

    0.4     9-24-21     Supports "Change the channel to <tv_channel>
    0.3     8-15-21     Clean up dialogue responses and add support for shade group "west side shades"
    0.2     7-26-21     Logging added

    0.1     7-14-21     Supports the following "skills":
                            -What time is it?
                            -What's the weather? (from Dark Sky API)
                            -Turn on/off TV power
                            -Turn on/off lights
                            -Set fan speed
                            -Open/close shade or shade groups
                        To do:
                            -Select TV apps on Samsung TV (Prime Video, Plex)
                            -Select TV channels using Tivo (ABC, CBS, NBC, PBS, etc.)
                            -Switch HDMI input
                            -Get the temperature from weather station

"""
# LIBRARY IMPORTS

import sys
import os
import pprint
import logging
import time
from datetime import datetime
import json
import random
import requests

from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession, HermesApp

from pyhubitat import MakerAPI

# Below are only needed if you have a Samsung TV
import samsungtvws
# import wakeonlan # Add this only if you have TV connected via WiFi
sys.path.append('../')
from samsungtvws import SamsungTVWS

# Constants

import config
# The following are defined in config.py which is in .gitignore to hide these from the Github repo:
# HUBITAT_IP = 'ip_address' # Enter the IP address or hub's DNS entry
# HUB_TOKEN = 'hub_token' # Use the token shown in the Maker API app on your Hubitat hub
# DARK_SKY_KEY = 'key' # Use the token for Dark Sky API
# LAT_LONG = 'lat,long' # Location for the weather query (use '-' in front of number if lat is S, and '-' if long is W)
# TV_IP = 'ip_address' # Samsung TV IP address, if used

# The following confirmations are randomly selected to provide a variety of responses
CONFIRMATION = ['All set','OK','Done','Confirmed','Absolutely','Sure']
# The following is used to select the proper verb for the voice response
VERB = {'plural':'are','singular':'is'}

# Functions
    
def send_command(name, state):
    # Find the device ID by searching for dictionary matching the label in list
    res = next((item for item in devices if item['label'].lower() == name), None)
    # Look up device id from name, send command to Hubitat, then return message
    if res != None:
        logging.info("Changing state, device ID is %s", res["id"])
        ph.send_command(res["id"], state)
        if name[-1] == 's':
            verb = VERB['plural']
        else:
            verb = VERB['singular']
        # Now we check if shades are being controlled, if so, change dialogue state to be accurate. (This is something Siri can't do!)
        if 'shade' in name and state == 'on':
            state = 'opening'
        elif 'shade' in name and state == 'off':
            state = 'closing'
        elif 'shade' in name and state == 'open':
            state = 'opening'
        elif 'shade' in name and state == 'close':
            state = 'closing'
        dialogue = CONFIRMATION[random.randint(0,5)] + ", " + name + " " + verb + " now " + state
        logging.info('Dialogue message is: ' + dialogue)
    else:
        logging.error("Can't change state, error finding device ID")
        dialogue = "Sorry, I can't find the device named " + name
    return dialogue


# INITIALIZATION
# Configure logging
# Increase debug level
logging.basicConfig(filename="rhasspy.log", format='%(asctime)s %(message)s',level=logging.DEBUG)

# Get Hubitat Device list
logging.info('Reading devices from Hubitat Maker API:')
ph = MakerAPI(config.HUB_TOKEN, 'http://'+config.HUBITAT_IP+'/apps/api/73') # Gathers all device details for later use.
devices = ph.list_devices_detailed()

for item in devices:
  label_name = item["label"]
  id_num = item["id"]
  logging.debug(id_num + '    ' + label_name)

# Get Samsung TV app codes

# Turn on the TV and wait

# ph.send_command(195,'on')
# time.sleep(5)

# Increase debug level
# Autosave token to file
token_file = './tv-token.txt' # The first time you run this program the TV will provide an on-screen prompt to allow/deny the remote access. If allowed, it provides the token which is written to the file.
# tv = SamsungTVWS(host=config.TV_IP, port=8002, token_file=token_file)
logging.info("Connected to TV, pulling TV app list")
# tv_apps = tv.app_list()

# pprint.pprint(tv_apps)

# START MONITORING INTENTS

logging.info("Starting to monitor intents")

# _LOGGER = logging.getLogger("IntentMonitorApp")

app = HermesApp("IntentMonitorApp")

@app.on_intent("GetTime")
async def get_time(intent: NluIntent):
    """Tell the time."""
    now = datetime.now().strftime("%H %M")
    logging.info("Telling the time")
    return EndSession(f"The current time is {now}")
    
@app.on_intent("GetWeather")
async def get_weather(intent: NluIntent):
    """Provide temperature and forecast precip."""
    r = requests.get('https://api.darksky.net/forecast/' + config.DARK_SKY_KEY + '/' + config.LAT_LONG,timeout = 30)
    forecast = json.loads(r.text)
    temp = round(forecast['currently']['temperature'])
    summary = forecast['hourly']['summary']
    logging.info("Providing Weather")
    return EndSession(f"The current temperature is {temp} and the forecast is {summary}")

@app.on_intent("GetGarageState")
async def get_garage_status(intent: NluIntent):
    """Gets status of garage doors."""
    door1=ph.device_status(42)
    door2=ph.device_status(43)
    door3=ph.device_status(44)
    doors =[door1,door2,door3]
    # pprint.pprint(doors)
    state = 'closed'
    count = 0
    verb = 'are'
    garage = 'doors '
    for door in doors:
        if state == 'open':
            pass
        if door['contact']['currentValue'] == 'open':
            state = 'open'
            count = count + 1
        if count == 0:
            count = 3
        elif count == 1:
            verb = 'is'
            garage = 'door '
    dialogue = 'There ' + verb + ' ' + str(count) + ' garage ' + garage + state
    logging.info('Dialogue message is: ' + dialogue)
    logging.info("Garage state is %s and count is %d",state,count)
    return EndSession(dialogue)

@app.on_intent("ChangeTVState")
async def tv_power(intent: NluIntent):
    """Turn the TV on or off."""
    intent_info = json.loads(intent.payload())
    state = intent_info["slots"][0]["value"]["value"]
    name = "tv power"
    # Now change the TV virtual switch in Hubitat
    dialogue = send_command(name,state)
    return EndSession(dialogue)
    
@app.on_intent("ChangeTVChannel")
async def tv_channel(intent: NluIntent):
    """Change the TV channel."""
    intent_info = json.loads(intent.payload())
    slots = intent_info["slots"]
    for slot in slots:
        if slot["entity"] == 'name':
            name = slot["value"]["value"]
        else:
            tv_channel = slot["value"]["value"]
    logging.info("Setting channel to %s", tv_channel)
    # Look up the channel from config.py in config.lkup dictionary
    # update the values like this example: lkup = {'ABC':'708','CBS':'706','NBC':'712','PBS':'704'}
    channel = config.lkup[tv_channel]
    # Now change the TV channel in Hubitat
    ph.send_command(194, 'setCH', channel)
    return EndSession(f"The TV channel is now {channel}")

@app.on_intent("ChangeLightState")
async def set_lights(intent: NluIntent):
    """Sets the light state on or off"""
    intent_info = json.loads(intent.payload())
    logging.debug(intent_info)
    slots = intent_info["slots"]
    for slot in slots:
        if slot["entity"] == 'name':
            name = slot["value"]["value"]
        else:
            state = slot["value"]["value"]
    # Now set the light state for the Hubitat device
    dialogue = send_command(name,state)
    return EndSession(dialogue)

@app.on_intent("ChangeFanSpeed")
async def set_fanspeed(intent: NluIntent):
    """Sets the fan speed"""
    intent_info = json.loads(intent.payload())
    logging.debug(intent_info)
    slots = intent_info["slots"]
    for slot in slots:
        if slot["entity"] == 'name':
            fan_name = slot["value"]["value"]
        else:
            fan_speed = slot["value"]["value"]
    logging.info("Setting %s speed to %s", fan_name,fan_speed)

    # Now set the fan speed for the Hubitat fan device
    # Since the Haiku fan child driver names all fans "Haiku fan" we hard-code the device ID
    if fan_name == 'great room fan':
        fan_id = 199
    else:
        fan_id = 201
    # Now set the light state for the Hubitat device
    logging.info("Setting fan speed, device ID is %s", fan_id)
    ph.send_command(fan_id, 'setSpeed', fan_speed)

    return EndSession(f"The {fan_name} is set to {fan_speed}")

@app.on_intent("ChangeShadeState")
async def set_shade(intent: NluIntent):
    """Sets the shade state"""
    intent_info = json.loads(intent.payload())
    logging.debug(intent_info)
    slots = intent_info["slots"]
    for slot in slots:
        if slot["entity"] == 'name':
            name = slot["value"]["value"]
        else:
            state = slot["value"]["value"]
    # "All Shades" and "West Side Shades" are set up as a group dimmer in Hubitat since there isn't group shade support. So we swap commands 'open' and 'close' for 'on' and 'off' respectively
    if name == 'all shades' or name == 'west side shades':
        if state == 'close':
            state = 'off'
        else:
            state = 'on'
    # Now set the shade state for the Hubitat device
    dialogue = send_command(name,state)
    return EndSession(dialogue)

app.run()

