import pytest
from PIL import Image
import axi_pixel_plot


def test_statistics_bmp():
    image = Image.open('test.bmp')
    assert image.mode == 'P'

    pen_downs = axi_pixel_plot.generate_pen_downs(image)
    assert len(pen_downs) == 188

    stats = axi_pixel_plot.generate_plot_statistics(image, pen_downs, [])
    assert stats['name'] == 'test.bmp'
    assert stats['image_size'] == '40x20px'
    assert stats['plot_size_width'] == 2
    assert stats['plot_size_height'] == 1
    assert stats['pen_downs'] == 188
    assert stats['plot_duration'] == 75.2
    assert stats['recover_pen_downs'] == stats['pen_downs']
    assert stats['recover_plot_duration'] == stats['plot_duration']
    assert stats['name'] == 'test.bmp'
