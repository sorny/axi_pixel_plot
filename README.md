# axi_pixel_plot
Plot bitmaps through your AxiDraw. Or lets say its not really plotting, its 'dotting'.

# Main Features:

  - Plot any bitmap or jpg via pyaxidraw
  - Resolution: 20 dots per cm / 0.05mm
  - Example: 50cm x 70cm print = 1000x1400px bitmap
  - Progress is displayed via tqdm progress bars
  - If plot is aborted, the remaining plotting data is stored in a recovery file to resume plotting

### Tech

axi_pixel_plot uses open source libs and open data to work properly:

* [tqdm](https://github.com/tqdm/tqdm) - A Fast, Extensible Progress Bar for Python and CLI
* [Pillow](https://github.com/python-pillow/Pillow) - The friendly PIL fork (Python Imaging Library)
* [pyaxidraw](https://github.com/evil-mad/axidraw) - Software for the AxiDraw drawing machine

# Installation
1) Clone this repo
2) Install the requirements for this script
```sh
pip3 install -r requirements.txt
```
3) Test the script to get some plot metadata via the included test.bmp
```sh
python3 axi_pixel_plot.py --analyse test.bmp
```
4) Plot the included test.bmp (plots a filled 1x1cm square / 400 pen-downs)
```sh
python3 axi_pixel_plot.py --plot test.bmp
```
5) Get help via
```sh
python3 axi_pixel_plot.py -h
```

### Notes

 * This script is not plotting lines, it is pure pen-down / pen-up action -> This takes a while. E.g. 50x70cm takes around 8h to plot
 * Movements are not optimized, reducing x/y movements could be easily done I guess.
 * This script is only tests on OSX and rpi4
 * To run it on your raspberry: `sudo apt-get install libxslt-dev libopenjp2-7 libtiff5 libatlas-base-dev` prior to the pip install
 * I made some good experience with the Stabilo Fineliners for the pendown/penup action -> recommended tool of trade



Have fun 

License
----

MIT

**Free Software, Hell Yeah!**
