"""
common.py

Common tools used between Python modules.

Author:     Steve Foga
Created:    02 Nov 2017

Python version: 3.7.3
"""
import os
import sys
import PIL.Image
import logging


DEFAULT_MAX_CPUS = os.cpu_count()

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)
lsh = logging.StreamHandler()
lsh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s- %(message)s','%m-%d-%Y %H:%M:%S')
lsh.setFormatter(formatter)
logger.addHandler(lsh)


def progress(count, total, suffix=''):
    """
    Display progress bar in command line

    :param count: <int> current iteration
    :param total: <int> total number of iterations
    :param suffix: <str> text to be plotted next to bar (should be description of progress)
    :return:
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[{0}] {1}{2} {3}\r'.format(bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben


def batch_split(input_values, process_count):
    """
    chunk a list of items
    :param input_values: <list>
    :param process_count: <int>
    :return: <list>
    """
    chunk_size = round(len(input_values) / float(process_count))
    if chunk_size == 0:
        chunk_size = 1
    chunk_low = 0
    chunk_high = chunk_size
    chunk_out = {}
    for part in range(0, process_count):
        logger.debug("part: {} | low: {} | high: {}".format(part, chunk_low, chunk_high))
        if part == process_count - 1:
            # fix the index to the last value
            values_to_write = input_values[chunk_low:len(input_values)]
            if values_to_write:  # prevents empty values being written to keys, otherwise apply_async gets upset
                chunk_out[part] = values_to_write
        else:
            values_to_write = input_values[chunk_low:chunk_high]
            if values_to_write:
                chunk_out[part] = values_to_write
            chunk_low += chunk_size
            chunk_high += chunk_size
    return chunk_out


class ImageIO():
    def __init__(self, image_path):
        self.image_path = image_path
        self.image_open = PIL.Image.open(self.image_path)
        self.image_exif = self.image_open._getexif()
        self.rgba = None

    def get_size(self):
        return self.image_open.size

    def overlay(self, image2, map_x_pos, max_y_pos):
        # TODO: use self.rgba() variable, and make this fucntion update self()
        base_img_rgba = self.image_open.convert("RGBA")
        map_img_rgba = image2.image_open.convert("RGBA")
        base_img_rgba.paste(map_img_rgba, (map_x_pos, max_y_pos), map_img_rgba)

        return base_img_rgba

    def rgba_to_rgb_mask(self):
        base_img_jpg_out = PIL.Image.new("RGB", self.image_open.size, (255, 255, 255))
        base_img_jpg_out.paste(self.image_open, mask=self.image_open.split()[3])

        return base_img_jpg_out

    def get_feature_vector(self, blocks=4):
        if not self.image_open.mode == 'RGB':
            raise Exception("Image mode {0} not supported.".format(self.image_open.mode))

        feature = [0] * blocks * blocks * blocks
        pixel_count = 0
        for pixel in self.image_open.getdata():
            ridx = int(pixel[0] / (256 / blocks))
            gidx = int(pixel[1] / (256 / blocks))
            bidx = int(pixel[2] / (256 / blocks))
            idx = ridx + gidx * blocks + bidx * blocks * blocks
            feature[idx] += 1
            pixel_count += 1

        return [x / float(pixel_count) for x in feature]


'''
class Common():
    @staticmethod
    def open_image(img_path):
        """
        Open image file.

        :param img_path: <str>
        :return: <PIL.Image>
        """
        from PIL import Image

        iopen = Image.open(img_path)
        print("Opened image {0}".format(img_path))

        return iopen

    @staticmethod
    def process_image(image, blocks=4):
        """
        Given a PIL Image object it returns its feature vector.

        :param image: <PIL.Image> image to process.
        :param blocks: <int> number of block to subdivide the RGB space (default=4).
        :return: <list> feature vector if successful. None if the image is not RGB.
        """
        import sys

        if not image.mode == 'RGB':
            raise Exception("Image mode {0} not supported.".format(image.mode))

        feature = [0] * blocks * blocks * blocks
        pixel_count = 0
        for pixel in image.getdata():
            ridx = int(pixel[0] / (256 / blocks))
            gidx = int(pixel[1] / (256 / blocks))
            bidx = int(pixel[2] / (256 / blocks))
            idx = ridx + gidx * blocks + bidx * blocks * blocks
            feature[idx] += 1
            pixel_count += 1

        return [x / float(pixel_count) for x in feature]
'''
