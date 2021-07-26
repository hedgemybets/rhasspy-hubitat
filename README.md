# Rhasspy-Hubitat Integration

This program provides integration between Rhasspy and Hubitat by listening to the Rhasspy MQTT event service for intents to handle and Hubitat's Maker API app to control the appropriate devices in Hubitat.

The intents to be handled by this application are triggered by voice queries to Rhasspy such as:

* Turn on|off the TV (turns on a virtual switch used by a Hubitat rule to control the TV, AV receiver, and Tivo)
* Set the <fan name> to low|medium low|medium|medium high|high
* Turn on|off the <light_name>
* Set the <light_name> to <number> percent
* Open|close the shades|blinds
* Turn on|off music
* Play some <music genre or playlist>
* Turn on <channel_name>
    
The last three are not yet implemented.

The intents and entities used must first be defined in the sentences.ini configuration in Rhasspy.
The devices you want to control need to be selected in Maker API app in Hubitat.

For initialization, this application makes a call to the Maker API to obtain all device details for later use. This means that the device names used in the Rhasspy sentences.ini config must match although they can be lower case in sentences.ini.

This also supports 2016 and later Samsung TVs that are connected via Ethernet or WiFi. This allows selecting Samsung applications like Prime Video or Plex server, by lookup of the list of installed apps to find the numeric codes required to select an app (future enhancement).

## Installation

The following are basic instructions to set up the environment, configure and install the software:
1. Setup Rhasspy hardware with *good* microphone, computer, and speakers. Instructions are at https://rhasspy.readthedocs.io/en/latest/installation/
2. Using the Rhasspy web interface, edit sentences.ini with the items you want to control in Hubitat. An example configuration is in this repository. Be sure to use the exact device names defined in Hubitat.
3. Test your Rhasspy system using the web interface to be sure that the intents are being recognized and variables are being passed as required.
4. Set up your Python environment to run the integration code. I use pipenv, but you can use venv or just pip to install the necessary modules. There are only two modules to install as the rest are automatically installed as dependencies. The modules are:
    * pyhubitat
    * rhasspy-hermes-app
Optionally, you can install samsungtvws if you have a Samsung TV and want to control it directly.

    
