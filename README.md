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


