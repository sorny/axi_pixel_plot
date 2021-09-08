#!/usr/bin/python

import sys
import os
import sys
from pyaxidraw import axidraw
from PIL import Image
from tqdm import tqdm
import json


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question + ' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


def write_recovery_file(data, file):
    print('Aborting, saving unplotted data to {}...'.format(file))
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# setup AxiDraw
ad = axidraw.AxiDraw()

ad.interactive()
connected = ad.connect()

if not connected:
    sys.exit()

ad.options.units = 1  # we work in cm
ad.update()

# setup plot
axi_pen_downs = []
bmp_file = sys.argv[1]
recovery_file = 'recovery_' + bmp_file.replace('.bmp', '') + '.json'
resolution = 0.05

# check if user wants to recover from aborted plot
recover = False
if os.path.exists(recovery_file):
    recover = yes_or_no('Continue plotting {} from {}?'.format(bmp_file, recovery_file))

# either load data from recovery json or generate from bitmap
if recover:
    print('Recovering plotting data from {}...'.format(recovery_file))
    axi_pen_downs = json.loads(open(recovery_file, 'r').read())
    print('plotpoints: {}'.format(len(axi_pen_downs)))
else:
    im = Image.open(bmp_file)
    print('Analysing {}...'.format(bmp_file))
    axipos_x = 0.0
    axipos_y = 0.0
    for x in range(im.width):
        for y in range(im.height):
            p = im.getpixel((x, y))
            if p < 250:
                axi_pen_downs.append((axipos_x, axipos_y))
            axipos_y = round(axipos_y + resolution, 2)
        axipos_y = 0.0
        axipos_x = round(axipos_x + resolution, 2)

    print('w: {} h: {} plotpoints: {}/{}'.format(im.width, im.height, len(axi_pen_downs), (im.width * im.height)))

unplotted = [i for i in axi_pen_downs]
try:
    print('Plotting...')
    plotting_progress = tqdm(axi_pen_downs, desc='Plotting progress', unit='pd')
    for pd in plotting_progress:
        plotting_progress.set_description('Plotting progress ({:.2f}/{:.2f})'.format(pd[0], pd[1]), refresh=True)
        ad.goto(pd[0], pd[1])
        ad.pendown()
        ad.penup()
        unplotted.remove(pd)

    print('Done, returning to home...')
    # hack to also write recovery file if pause button is pressed on AxiDraw, found no other way to hook into pause
    if len(unplotted) > 0:
        write_recovery_file(unplotted, recovery_file)
except KeyboardInterrupt:
    write_recovery_file(unplotted, recovery_file)

finally:
    ad.goto(0, 0)
    ad.disconnect()
