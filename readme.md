# Washer Notifier

> Source code accompanying the videos 
> Part 1 (hardware, esphome etc) : <https://www.youtube.com/watch?v=atD7VcXrfWY>
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

## Additional info

_WIP_

## Links:

* [Schematic](http://bit.ly/2rf4BGa)

### Aliexpress:
* [Female Micro USB Connector](http://s.click.aliexpress.com/e/CWPZ2ZrS)
* [Small Box](http://s.click.aliexpress.com/e/BXgpWTYM)
* [MPU6050](http://s.click.aliexpress.com/e/qs81hpFa)
* [ESP-01](http://s.click.aliexpress.com/e/5LVC1OKM)
* [ESP-01 Programmer](http://s.click.aliexpress.com/e/qNMsgQBm)
* [3.3V regulator](http://s.click.aliexpress.com/e/DyoqPbhW)
* [Veroboard](http://s.click.aliexpress.com/e/FnTQdduy)

## TODO
- [ ] HA - custom components installation instructions - readme
- [ ] update this readme file with part II details