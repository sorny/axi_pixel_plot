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

# consts
RESOLUTION = 0.05
DURATION_FACTOR = 2.5


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


def generate_plot_statistics(image, axi_pen_downs, axi_pen_downs_recover):
    stats = dict()
    stats['name'] = image.filename
    stats['image_mode'] = image.mode
    stats['image_size'] = str(image.width) + 'x' + str(image.height) + 'px'
    stats['plot_resolution'] = math.floor(1 / RESOLUTION)
    stats['plot_size_width'] = image.width / (1 / RESOLUTION)
    stats['plot_size_height'] = image.height / (1 / RESOLUTION)
    stats['pen_downs'] = len(axi_pen_downs)
    stats['plot_duration'] = stats['pen_downs'] / DURATION_FACTOR
    stats['recover_pen_downs'] = stats['pen_downs']
    stats['recover_plot_duration'] = stats['plot_duration']
    if len(axi_pen_downs_recover) > 0:
        stats['recover_pen_downs'] = len(axi_pen_downs_recover)
        stats['recover_plot_duration'] = ['recover_pen_downs'] / DURATION_FACTOR

    return stats


def pps(name, value):
    print(' {0: <17}'.format(name + ': ') + value)


def print_statistics(image, axi_pen_downs, recovery_file, axi_pen_downs_recover):
    stats = generate_plot_statistics(image, axi_pen_downs, axi_pen_downs_recover)
    print('Plot statistics...')
    pps('Image', stats['name'])
    pps('Image mode', stats['image_mode'])
    pps('Size', stats['image_size'])
    pps('Plot resolution', str(stats['plot_resolution']) + 'px/cm')
    pps('Plotsize', str(stats['plot_size_width']) + 'x' + str(stats['plot_size_height']) + 'cm')

    if len(axi_pen_downs_recover) > 0:
        pps('Recover file', recovery_file)
        pps('# Total Pen-Downs', str(stats['pen_downs']))
        pps('# Pen-Downs left', str(stats['recover_pen_downs']))
        pps('Plot duration total', str(datetime.timedelta(seconds=stats['plot_duration'])))
        pps('Plot duration left',
            str(datetime.timedelta(seconds=stats['recover_plot_duration'])))
    else:
        pps('# Pen-Downs', str(stats['pen_downs']))
        pps('Plot duration', str(datetime.timedelta(seconds=stats['plot_duration'])))
    print()


def generate_pen_downs(image):
    pen_downs = []
    axipos_x = 0.0
    axipos_y = 0.0
    for x in range(image.width):
        for y in range(image.height):
            p = image.getpixel((x, y))
            if image.mode == 'L':
                if p < 250:
                    pen_downs.append((axipos_x, axipos_y))
            if image.mode == 'P':
                if p == 1:
                    pen_downs.append((axipos_x, axipos_y))
            axipos_y = round(axipos_y + RESOLUTION, 2)
        axipos_y = 0.0
        axipos_x = round(axipos_x + RESOLUTION, 2)
    return pen_downs


if __name__ == '__main__':
    # cli args
    parser = argparse.ArgumentParser(description='Plot pixels on your AxiDraw')
    parser.add_argument('-p', '--plot', dest='action', action='store_const',
                        const='plot', default='analyse', help='Plot the file')
    parser.add_argument('-a', '--analyse', dest='action', action='store_const',
                        const='analyse', default='analyse', help='Analyse the file and print statistics')
    parser.add_argument('source_file', type=open,
                        help='file to plot')
    args = parser.parse_args()

    # load files
    image = Image.open(args.source_file.name)
    if not (image.mode == 'L' or image.mode == 'P'):
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
    print('Analysing {}...'.format(image.filename))
    axi_pen_downs = generate_pen_downs(image)
    print_statistics(image, axi_pen_downs, recovery_file, axi_pen_downs_recover)

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
                plotting_progress.set_description('Plotting progress ({:.2f}/{:.2f})'.format(pd[0], pd[1]),
                                                  refresh=True)
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
