#!/usr/bin/python3
import argparse
import sys
import os
import sys
from pyaxidraw import axidraw
from PIL import Image
from tqdm import tqdm
import json
import math
import datetime


# helper definitions
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


def statistic(name, value):
    return ' {0: <17}'.format(name + ': ') + value


def print_statistics(args, image, resolution, axi_pen_downs, recovery_file, axi_pen_downs_recover):
    duration_factor = 2.5
    print('Plot statistics...')
    print(statistic('Image', args.source_file.name))
    if image.mode == 'L':
        print(statistic('Image mode', 'L (8bit pixels, black and white)'))
    if image.mode == 'RGB':
        print(statistic('Image mode', 'RGB (3x8-bit pixels, true color)'))
        print(statistic('RGB filter', str(args.r) + ',' + str(args.g) + ',' + str(args.b)))

    print(statistic('Size', str(image.width) + 'x' + str(image.height) + 'px'))
    print(statistic('Plot resolution', str(math.floor(1 / resolution)) + 'px/cm'))
    print(
        statistic('Plotsize', str(image.width / (1 / resolution)) + 'x' + str(image.height / (1 / resolution)) + 'cm'))
    if len(axi_pen_downs_recover) > 0:
        print(statistic('Recover file', recovery_file))
        print(statistic('# Total Pen-Downs', str(len(axi_pen_downs))))
        print(statistic('# Pen-Downs left', str(len(axi_pen_downs_recover))))
        print(
            statistic('Plot duration total', str(datetime.timedelta(seconds=(len(axi_pen_downs) / duration_factor)))))
        print(statistic('Plot duration left',
                        str(datetime.timedelta(seconds=(len(axi_pen_downs_recover) / duration_factor)))))
    else:
        print(statistic('# Pen-Downs', str(len(axi_pen_downs))))
        print(statistic('Plot duration', str(datetime.timedelta(seconds=(len(axi_pen_downs) / duration_factor)))))
    print()


# cli args
parser = argparse.ArgumentParser(description='Plot pixels on your AxiDraw')
parser.add_argument('-p', '--plot', dest='action', action='store_const',
                    const='plot', default='analyse', help='Plot the file')
parser.add_argument('-a', '--analyse', dest='action', action='store_const',
                    const='analyse', default='analyse', help='Analyse the file and print statistics')
parser.add_argument('source_file', type=open,
                    help='file to plot')
parser.add_argument('-r', type=int,
                    help='Red value for RGB filter')
parser.add_argument('-g', type=int,
                    help='Green value for RGB filter')
parser.add_argument('-b', type=int,
                    help='Blue value for RGB filter')
args = parser.parse_args()

### plotting business ###
resolution = 0.05

# load files
image = Image.open(args.source_file.name)
if not (image.mode == 'L' or image.mode == 'RGB'):
    raise Exception('Image mode ' + image.mode + ' not supported...')
recovery_file = 'recovery_' + args.source_file.name.split('.')[0] + '.json'

axi_pen_downs = []
axi_pen_downs_recover = []
recover = False
if os.path.exists(recovery_file) and args.action == 'plot':
    recover = yes_or_no('Continue plotting {} from {}?'.format(bmp_file, recovery_file))
    if recover:
        print('Recovering plotting data from {}...'.format(recovery_file))
        axi_pen_downs_recover = json.loads(open(recovery_file, 'r').read())

# analyse image
print('Analysing {}...'.format(args.source_file.name))
axipos_x = 0.0
axipos_y = 0.0
for x in range(image.width):
    for y in range(image.height):
        p = image.getpixel((x, y))
        if image.mode == 'L':
            if p < 250:
                axi_pen_downs.append((axipos_x, axipos_y))
        if image.mode == 'RGB':
            if p[0] == args.r and p[1] == args.g and p[2] == args.b:
                axi_pen_downs.append((axipos_x, axipos_y))

        axipos_y = round(axipos_y + resolution, 2)
    axipos_y = 0.0
    axipos_x = round(axipos_x + resolution, 2)

print_statistics(args, image, resolution, axi_pen_downs, recovery_file, axi_pen_downs_recover)

if args.action == 'plot':
    print('Connecting to AxiDraw...')
    ad = axidraw.AxiDraw()
    ad.interactive()
    connected = ad.connect()
    if not connected:
        sys.exit()
    ad.options.units = 1
    ad.update()

    if not yes_or_no('Start plotting?'):
        sys.exit()
    print('Plotting...')
    if recover:
        axi_pen_downs = axi_pen_downs_recover
    unplotted = [i for i in axi_pen_downs]

    try:
        plotting_progress = tqdm(axi_pen_downs, desc='Plotting progress', unit='pd')
        for pd in plotting_progress:
            plotting_progress.set_description('Plotting progress ({:.2f}/{:.2f})'.format(pd[0], pd[1]), refresh=True)
            ad.goto(pd[0], pd[1])
            ad.pendown()
            ad.penup()
            unplotted.remove(pd)

        print('Done, returning to home...')
        # hack to also write recovery file if pause button is pressed on AxiDraw
        if len(unplotted) > 0:
            write_recovery_file(unplotted, recovery_file)
    except KeyboardInterrupt:
        write_recovery_file(unplotted, recovery_file)

    finally:
        ad.goto(0, 0)
        ad.disconnect()
