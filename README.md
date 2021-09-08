# axi_bitmap_plot
Plot bitmaps through your AxiDraw

# Main Features:

  - Plot any bitmap via pyaxidraw
  - Resolution: 20 dots per cm
  - Example: 50cm x 70cm print = 1000x1400px bitmap
  - Progress is displayed via tqdm progress bars
  - If plot is aborted, the remaining plotting data is stored in a recovery file to resume plotting

### Tech

axi_bitmap_plot uses open source libs and open data to work properly:

* [tqdm](https://github.com/tqdm/tqdm) - A Fast, Extensible Progress Bar for Python and CLI
* [Pillow](https://github.com/python-pillow/Pillow) - The friendly PIL fork (Python Imaging Library)
* [pyaxidraw](https://github.com/evil-mad/axidraw) - Software for the AxiDraw drawing machine

# Installation
1) Clone this repo
2) Install the requirements for this script
```sh
pip3 install -r requirements.txt
```
3) Update `pyaxi_bitmap_plot.py` and set the bitmap to plot
4) Run the script in dryrun mode
```sh
python3 pyaxi_bitmap_plot.py
```

### Notes

 * This script is not plotting lines, it is pure pen-down / pen-up action -> This takes a while. E.g. 50x70cm takes around 8h to plot
 * Movements are not optimized



Have fun 

License
----

MIT

**Free Software, Hell Yeah!**
