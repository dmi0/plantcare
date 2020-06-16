# PlantCare: Xiaomi Mi Flora Plant Sensor telegram notifier
A monitoring tool to read Xiaomi Mi Flora sensors and to send notifications via Telegram if readings are out of configured boundaries.

As the official Xiaomi app doesn't always meet our expectation, this tool can help to look after your plant if you have a spare home server (or whatsoever with docker inside) with Bluetooth. 

### Supported parameters
Parameter|alias
---------|-----
Soil moisture|moisture
Light intensity|light
Soil fertility|conductivity
Temperature|temperature
Battery charge|battery


## Set up
### 1. Create a telegram bot
Follow instructions here: https://core.telegram.org/bots#3-how-do-i-create-a-bot

A _bot token_ will be used for configuration later.

Then you need to add the bot to a telegram channel and get a _channel id_. The easiest way to know what is the _channel id_ is to check bot's status updates:
`https://api.telegram.org/bot<BotToken>/getUpdates` 
Look at the response json. The _channel id_ will be in "id" field of the "chat" object.

### 2. Build
```
docker build -t plantcare .
```

### 3. Create a configuration json
The full configuration json is as follows:
```
{
  "loglevel": "INFO",
  "telegram": {
    "token": "3059511111:ZZZZ-ZZZZZZZZZZZZZZZZZZZZZZ-AAAAAAA",
    "channel": "-321012345",
    "message": {
      "parse_mode": "MarkdownV2",
      "moisture": "*{plant}*\nMoisture is out of the boundaries*: {boundaries}\n*Current value*: {value}",
      "light": "*{plant}*\nLight is out of the boundaries*: {boundaries}\n*Current value*: {value}",
      "temperature": "*{plant}*\nTemperature is out of the boundaries*: {boundaries}\n*Current value*: {value}",
      "battery": "*{plant}*\nBattery level is out of the boundaries*: {boundaries}\n*Current value*: {value}",
      "conductivity": "*{plant}*\nFertility is out of the boundaries*: {boundaries}\n*Current value*: {value}"
    }
  },
  "adapter": "hci0",
  "max_attempts": 5,
  "sensors": {
    "Rose": {
      "mac": "10:EA:BA:58:10:B8",
      "wellbeing_range": {
        "moisture": {
          "min": 40,
          "max": 50
        },
        "conductivity": {
          "min": 19
        }
      }
    }
  }
}
```
Where `wellbeing_range` in the `sensors` section can have boundaries for multiple parameters.

**loglevel** (optional, default is "INFO")\
Logging level for `docker log` output. 

**telegram : token** (required)\
Telegram _bot token_ 

**telegram : channel** (required)\
Telegram _channel id_ 

**telegram : message : parse_mode** (optional, default is "MarkdownV2")\
See https://core.telegram.org/bots/api#formatting-options

**telegram : message : {moisture|light|battery|temperature|conductivity}** (optional, defaults is "{plant}: '_PARAM_' parameter is out of boundaries '{boundaries}'")\
Notification templates for messages sent via telegram in case of readings are out of configured boundaries. You can overwrite none, one, or all of them in your config json.

A message template for a parameter (moisture, light, battery, temperature, or conductivity) may contain the following template placeholders:
- `{plant}` - a plant name (see `sensors` bellow) 
- `{boundaries}` - configured boundaries for the sensor parameter. Depending on a `wellbeing_range` configuration (see `sensors` bellow), it can be `[min, max]` (if both `min` and `max` are configured), or `≥ min`, or `≤ max`)
- `{value}` - a parameter value 

A template formatting should follow Telegram formatting rules for a chosen `parse_mode`: https://core.telegram.org/bots/api#formatting-options

Don't forget escaping. 

**adapter** (optional, default is "hci0")\
In most cases the adapter name is "hci0". You can check it (or what other adapters you have in your system) by running this command: 
```
docker run --rm plantcare ls /sys/class/bluetooth/
```

**max_attempts** (optional, default is 5)
How many times it will try to connect to and to read from each sensor before giving up.

**sensor** (required)\
A collection of objects where keys are sensors'/plants' names. They will be used for the `{pant}` placeholder in the message templates.

**sensor : {plant} : mac** (required)\
Sensor's mac address. Run this command to see all bluetooth devices nearby (make sure you are close enough to the sensor):
```
docker run --net=host --privileged -it --rm plantcare blescan -a
```

And see device(s) which has "Complete Local Name: 'Flower care'" in the output.

**sensor : {plant} : wellbeing_range** (required)\
A collection of objects where keys are parameter aliases (see above) and values are intervals. Intervals can have both `min` and `max`, or only one `min`/`max`. A notification regarding a parameter will not be sent while the parameter value is within `wellbeing_range`.

A minimal configuration json can be like this: 

```
{
  "telegram": {
    "token": "3059511111:ZZZZ-ZZZZZZZZZZZZZZZZZZZZZZ-AAAAAAA",
    "channel": "-321012345",
    "message": {
      "moisture": "*{plant}* need to be watered"
    }
  },
  "sensors": {
    "Rose": {
      "mac": "10:EA:BA:58:10:B8",
      "wellbeing_range": {
        "moisture": {
          "min": 40
        }
      }
    }
  }
}
```
### 4. Run it
`CONFIG` environment variable should be passed with the configuration json (using --env or --env-file).

```
docker run --net host --rm --env CONFIG='{"telegram":{"token":"3059511111:ZZZZ-ZZZZZZZZZZZZZZZZZZZZZZ-AAAAAAA","channel":"-321012345","message":{"moisture":"*{plant}* need to be watered"}},"sensors":{"Rose":{"mac":"10:EA:BA:58:10:B8","wellbeing_range":{"moisture":{"min":40}}}}}' plantcare 
```
PlantCare app doesn't work in a daemon mode. However you can schedule periodical checks by crontab or  [willfarrell/crontab](https://hub.docker.com/r/willfarrell/crontab)