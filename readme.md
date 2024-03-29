# Washer Notifier

> Source code and configuration accompanying the videos <br />
> Part 1 (hardware, esphome etc) : <https://www.youtube.com/watch?v=atD7VcXrfWY>  <br/>
> Part 2 (home assistant automation, appdaemon etc) : <https://youtu.be/t5eoUQmB4SA>

Leaving the clothes in the washer for too long? Need a way to detect when the washer is done?
In this video I walk you through the process I went through to create such a device and the
related automation code.

I build a little sensor using an ESP-01 and an accelerometer (MPU6050) that send off data to my
home assistant instance. The programming was done using [ESPHome](https://esphome.io/). A
[Home Assistant](https://www.home-assistant.io/) automation then takes these readings and detects
when the washer is complete and announces over Amazon Echo and Google Home devices in the home.

In part I,  I wrote a little [python script](http://bit.ly/36YOT1f)
to read the sensor readings from ESPHome and dump it into a CSV file. Using a
[Jupyter notebook](https://jupyter.org/), I then load this CSV file and plot the 
sensor values. This made it easy to try out various algorithms to identify the washer cycles.
I also explain (briefly) the process of converting this algorithm into
 a custom filter that acts on the sensor readings in ESPHome.

In part II, I walk you through the design and implementation of a state machine in Home Assistant using [AppDaemon](https://www.home-assistant.io/docs/ecosystem/appdaemon/) to identify the state of the washer from the vibration sensor values. When the automation detects that the washer is done, it send notifications (as broadcasted messages) over Google Home and Amazon Echo/Alexa.

All the code, configurations and schematics are in the repository. 

## State Diagram

![State Diagram](state-diagram.png)

[dot diagram viewer](https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20%7B%0A%20%20%20%20graph%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%5D%3B%0A%20%20%20%20node%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%2C%20fillcolor%3D%22%23EEEEEE%3B0%3A%23D8D8D8%3B1.0%22%2C%20style%3Dfilled%2C%20gradientangle%3D270%5D%3B%0A%20%20%20%20edge%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%5D%3B%0A%20%20%20%20IDLE-%3EMAYBE_WASHING%5Blabel%3D%22wash%2C%20spin%22%5D%3B%0A%20%20%20%20ERROR-%3EMAYBE_WASHING%5Blabel%3D%22wash%5Cn%20%20spin%22%5D%3B%0A%20%20%20%20DONE-%3EMAYBE_WASHING%5Blabel%3D%22%20%20%20wash%2C%20spin%22%5D%3B%0A%20%20%20%20MAYBE_WASHING-%3EWASHING%5Blabel%3D%22timeout%201%20min%22%5D%3B%0A%20%20%20%20MAYBE_WASHING-%3EMAYBE_IDLE%5Blabel%3D%22idle%22%5D%3B%0A%20%20%20%20MAYBE_IDLE-%3EIDLE%5Blabel%3D%22timeout%205%20min%22%5D%3B%0A%20%20%20%20MAYBE_IDLE-%3EMAYBE_WASHING%5Blabel%3D%22wash%5Cn%20spin%22%5D%3B%0A%20%20%20%20WASHING-%3ESPINNING%5Blabel%3D%22%20%20spin%22%5D%3B%0A%20%20%20%20WASHING-%3EMAYBE_ERROR%5Blabel%3D%22idle%22%5D%3B%0A%20%20%20%20SPINNING-%3EMAYBE_DONE%5Blabel%3D%22%20idle%20%20%22%5D%3B%0A%20%20%20%20SPINNING-%3EWASHING%5Blabel%3D%22%5Cn%5Cn%20%20wash%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3EWASHING%5Blabel%3D%22%20%20wash%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3ESPINNING%5Blabel%3D%22%5Cn%5Cn%20%20spin%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3EDONE%5Blabel%3D%22timeout%208%20min%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3EWASHING%5Blabel%3D%22wash%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3ESPINNING%5Blabel%3D%22spin%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3EERROR%5Blabel%3D%22%5Cn%5Cntimeout%2030%20min%22%5D%3B%0A%7D)

### Graphviz Diagram
```
digraph G {
    graph [fontname = "DigitalStrip BB"];
    node [fontname = "DigitalStrip BB", fillcolor="#EEEEEE;0:#D8D8D8;1.0", style=filled, gradientangle=270];
    edge [fontname = "DigitalStrip BB"];
    IDLE->MAYBE_WASHING[label="wash, spin"];
    ERROR->MAYBE_WASHING[label="wash\n  spin"];
    DONE->MAYBE_WASHING[label="   wash, spin"];
    MAYBE_WASHING->WASHING[label="timeout 1 min"];
    MAYBE_WASHING->MAYBE_IDLE[label="idle"];
    MAYBE_IDLE->IDLE[label="timeout 5 min"];
    MAYBE_IDLE->MAYBE_WASHING[label="wash\n spin"];
    WASHING->SPINNING[label="  spin"];
    WASHING->MAYBE_ERROR[label="idle"];
    SPINNING->MAYBE_DONE[label=" idle  "];
    SPINNING->WASHING[label="\n\n  wash"];
    MAYBE_DONE->WASHING[label="  wash"];
    MAYBE_DONE->SPINNING[label="\n\n  spin"];
    MAYBE_DONE->DONE[label="timeout 8 min"];
    MAYBE_ERROR->WASHING[label="wash"];
    MAYBE_ERROR->SPINNING[label="spin"];
    MAYBE_ERROR->ERROR[label="\n\ntimeout 75 min"];
}
```

## Additional info

In case you are planning to build this, here are a few things to help you along the way. 

1. The vibration levels and the timeouts between the various states is highly dependent on the washer, how you place the sensor and other factors. So you will need to tweak it based on actual readings from the washer. 
2. Configure influxdb and grafana with home assistant and setup a (dashboard for the washer)[grafana-washer-dashboard.png] related sensors. It was a tremendous help for me to tweak the thresholds and timeouts. [Json export of my dashboard](grafana-washer-dashboard.json). 
3. Stick with it for a couple of days while you tweak the values. Try different types of wash cycles (hot, cold, cotton, whatever else you use in your home) and tweak the values. It was helpful for me to configure the notifications to just come to me (I used the telegram integration) while I was working on it. Once it is setup properly, it is zero maintenance and works beautifully. 
4. For the privacy conscious amoung us, use a different notification mechanism that is more privacy friendly like a buzzer or even an offline text to speech based one. Drop me a note if you are interested seeing a build video for one. I have some plans for such a device in my notes. 

## Improvements

You could add a door open sensor using one of those reed switches or something similar and wire it to the ESP-01. Modify the state machine to take this into account and have a "pending_clearance" 😊 or something similar and send out notifications periodically until the washer is emptied.

## Links:

* [Schematic](http://bit.ly/2rf4BGa)
* [State Diagram](https://github.com/lostinthebuild/S01E02-state-machine-washer-notifier-II/blob/master/state-diagram.png)
*  [Home Assistant - Google Assistant Integration using Assistant Relay](https://community.home-assistant.io/t/component-to-send-commands-to-google-assistant/134156)
*  [Home Assistant - Alexa Integration](https://github.com/custom-components/alexa_media_player)
*  [Home Assistant Configuration](https://github.com/lostinthebuild/S01E02-state-machine-washer-notifier-II/tree/master/homeassistant)
*  [AppDaemon Automation Apps](https://github.com/lostinthebuild/S01E02-state-machine-washer-notifier-II/tree/master/appdaemon/apps) 
* [EspHome Configuration](https://github.com/lostinthebuild/S01E02-state-machine-washer-notifier-II/blob/master/washer.yaml)

### Aliexpress:
* [Female Micro USB Connector](http://s.click.aliexpress.com/e/CWPZ2ZrS)
* [Small Box](http://s.click.aliexpress.com/e/BXgpWTYM)
* [MPU6050](http://s.click.aliexpress.com/e/qs81hpFa)
* [ESP-01](http://s.click.aliexpress.com/e/5LVC1OKM)
* [ESP-01 Programmer](http://s.click.aliexpress.com/e/qNMsgQBm)
* [3.3V regulator](http://s.click.aliexpress.com/e/DyoqPbhW)
* [Veroboard](http://s.click.aliexpress.com/e/FnTQdduy)
