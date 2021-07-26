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
1. Setup Rhasspy hardware with a **good** microphone, computer and speakers. Instructions are at https://rhasspy.readthedocs.io/en/latest/installation/
2. A key configuration for Rhasspy is that its MQTT event broker's IP port has to be available on your network so the Python code can listen for intent events. If you are using docker (**highly recommended**), I have included two docker commands in this repo that set this up (at least for Linux). The only difference between the two is that start-rhasspy.sh is for interactive use where the docker messages come to the console. The other, start-rhasspy-d.sh starts docker as a background process. The latter will likely be how to set up Rhasspy to run whenever your computer boots or restarts.
3. Using the Rhasspy web interface, edit sentences.ini with the items you want to control in Hubitat. An example configuration is in this repository. Be sure to use the exact device names defined in Hubitat.
4. Test your Rhasspy system using the web interface to be sure that the intents are being recognized and variables are being passed as required.
5. Install the Maker API app on your Hubitat hub and configure the devices you want to make available for Rhasspy to control or check status on.
4. Set up your Python environment to run the integration code. This can be on the same computer that runs Rhasspy. I use pipenv to manage this in a virtual environment, but you can use venv or just pip to install the necessary modules. There are only two modules to install as the rest are automatically installed as dependencies or built-in to Python. The modules are:
    * pyhubitat
    * rhasspy-hermes-app

Optionally, you can install samsungtvws if you have a Samsung TV and want to control it directly.

Next are the steps to download and configure the Python components:
    
1. If you have git installed, you can clone the software to a local directory on the Rhasspy computer.
2. Create a file called config.py and enter the IP Address and Hub token for Maker API in the format shown in the comments of porcupine.py.
3. You should then be able to launch the Python code with the following:
    
    python3 ./porcupine.py --host localhost --port 12183
    
This assumes that porcupine is running on the same computer and the MQTT event broker port is set to the default 12183.
Note that you may have to open up the firewall for Rhasspy to expose this port to the Python code.
    

    

    


    
