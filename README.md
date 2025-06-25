# hackpad
My own take on the hackpad using QMK as firmware

## Features
* 9 keys
* an EC11 encoder controlling volume (mutes upon press)
* a 128x32 oled display showing the currently playing music
* 16 neopixel leds for backlighting efects
* case consisting of two parts
* some nice drawings by my girlfriend on the silkscreen and on the case
* QMK (maybe I'll add VIA sometime)


## Cad model
the keyboard fits together using 7 M3 screws - 3 for the pcb and 4 for the case itself which comes in two parts.

<img src=images/hackpad.png>

made in fusion 360 (crashed my computer only 5 times!)

## PCB
My pcb was made in kicad with the silkscreen made up of my girlfriends drawings.

Schematic
<svg src=images/schematic.svg>

PCB
<img src=images/PCB.png>

## Firmware and Software
The Firmware is plain QMK but the oled screen is rendered on the host and sent pixel by pixel .
That is because it look nicer and allows support for non-English languages like hebrew.

the screen should look aproximatlly like this:
<img src=images/oled.png>

claude helped here a little bit but not too much.

## BOM:
This should be everything needed for this hackpad:

* 9x Cherry MX switches
* 9x DSA Keycaps
* 7x M3x5x4 Heatset inserts
* 7x M3x4 screws
* 12x 1N4148 DO-35 Diodes
* 16x WS2812B Leds
* 1x 0.91" 128x32 OLED display
* 1x EC11 Rotary encoder
* 1x XIAO seeed RP2040
* 1x pcb
* 1x case (2 3d printed parts)

