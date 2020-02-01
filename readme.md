# Washer Notifier

## TODO
- [ ] HA - custom components installation instructions - readme
- [ ] schmitt trigger - get the nomenclature - correct
- [ ] update this readme file with part II details

[dot diagram](https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20%7B%0A%20%20%20%20graph%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%5D%3B%0A%20%20%20%20node%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%2C%20fillcolor%3D%22%23EEEEEE%3B0%3A%23D8D8D8%3B1.0%22%2C%20style%3Dfilled%2C%20gradientangle%3D270%5D%3B%0A%20%20%20%20edge%20%5Bfontname%20%3D%20%22DigitalStrip%20BB%22%5D%3B%0A%20%20%20%20IDLE-%3EMAYBE_WASHING%5Blabel%3D%22wash%2C%20spin%22%5D%3B%0A%20%20%20%20ERROR-%3EMAYBE_WASHING%5Blabel%3D%22wash%5Cn%20%20spin%22%5D%3B%0A%20%20%20%20DONE-%3EMAYBE_WASHING%5Blabel%3D%22%20%20%20wash%2C%20spin%22%5D%3B%0A%20%20%20%20MAYBE_WASHING-%3EWASHING%5Blabel%3D%22timeout%201%20min%22%5D%3B%0A%20%20%20%20MAYBE_WASHING-%3EMAYBE_IDLE%5Blabel%3D%22idle%22%5D%3B%0A%20%20%20%20MAYBE_IDLE-%3EIDLE%5Blabel%3D%22timeout%205%20min%22%5D%3B%0A%20%20%20%20MAYBE_IDLE-%3EMAYBE_WASHING%5Blabel%3D%22wash%5Cn%20spin%22%5D%3B%0A%20%20%20%20WASHING-%3ESPINNING%5Blabel%3D%22%20%20spin%22%5D%3B%0A%20%20%20%20WASHING-%3EMAYBE_ERROR%5Blabel%3D%22idle%22%5D%3B%0A%20%20%20%20SPINNING-%3EMAYBE_DONE%5Blabel%3D%22%20idle%20%20%22%5D%3B%0A%20%20%20%20SPINNING-%3EWASHING%5Blabel%3D%22%5Cn%5Cn%20%20wash%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3EWASHING%5Blabel%3D%22%20%20wash%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3ESPINNING%5Blabel%3D%22%5Cn%5Cn%20%20spin%22%5D%3B%0A%20%20%20%20MAYBE_DONE-%3EDONE%5Blabel%3D%22timeout%208%20min%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3EWASHING%5Blabel%3D%22wash%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3ESPINNING%5Blabel%3D%22spin%22%5D%3B%0A%20%20%20%20MAYBE_ERROR-%3EERROR%5Blabel%3D%22%5Cn%5Cntimeout%2030%20min%22%5D%3B%0A%7D)

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

-------


> Source code accompanying the video at <https://www.youtube.com/watch?v=atD7VcXrfWY>

Leaving the clothes in the washer for too long? Need a way to detect when the washer is done?
In this video I walk you through the process I went through to create such a device and the
related automation code.

I build a little sensor using an ESP-01 and an accelerometer (MPU6050) that send off data to my
home assistant instance. The programming was done using [ESPHome](https://esphome.io/). A
[home assistant] (https://www.home-assistant.io/) automation then takes these readings and detects
when the washer is complete and announces over Amazon Echo and Google Home devices in the home.

This is part 1 of the project. In this part I wrote a little [python script](http://bit.ly/36YOT1f)
to read the sensor readings from ESPHome and dump it into a CSV file. Using a
[Jupyter notebook] (https://jupyter.org/),
I then load this CSV file and plot the sensor values. This made it easy to try out various
algorithms to identify the washer cycles.  I also explain (briefly) the process of writing custom
 code to convert this algorithm into a custom filter that acts on the sensor readings in ESPHome.

## Links:

* [Schematic](http://bit.ly/2rf4BGa)

### Aliexpress:
* [Female Micro USB Connector](http://s.click.aliexpress.com/e/CWPZ2ZrS)
* [Small Box](http://s.click.aliexpress.com/e/BXgpWTYM)
* [MPU6050](http://s.click.aliexpress.com/e/qs81hpFa)
* [ESP-01](http://s.click.aliexpress.com/e/5LVC1OKM)
* [ESP-01 Programmer](http://s.click.aliexpress.com/e/qNMsgQBm)
* [3.3V regulator](http://s.click.aliexpress.com/e/DyoqPbhW)
* [Veroboard] (http://s.click.aliexpress.com/e/FnTQdduy)