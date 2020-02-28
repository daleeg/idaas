# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PIL import Image
import piexif
import logging
LOG = logging.getLogger(__name__)


def auto_rotate_image(filename):
    try:
        img = Image.open(filename)
    except Exception as e:
        LOG.error(e)
        return

    if "exif" in img.info:
        exif_dict = piexif.load(img.info["exif"])

        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            orientation = exif_dict["0th"].pop(piexif.ImageIFD.Orientation)
            if orientation == 2:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                img = img.rotate(180)
            elif orientation == 4:
                img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                img = img.rotate(-90, expand=True)
            elif orientation == 7:
                img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            img.save(filename)
    img.close()


def resize_image(path, new_path, max_width=1024, max_height=768):
    try:
        close_image = image = Image.open(path)
    except Exception as e:
        LOG.error(e)
        return
    image_format = "JPEG"
    if image.format != "JPEG":
        image = image.convert("RGB")
    width, height = image.size
    wmh = width * max_height
    hmw = height * max_width

    if wmh > hmw:
        new_width = max_width
        new_height = int(height * max_width / width)
    elif wmh < hmw:
        new_width = int(width * max_height / height)
        new_height = max_height
    else:
        new_width = max_width
        new_height = max_height

    if new_width + new_height < width + height:
        # shrink
        image = image.resize((new_width, new_height), Image.ANTIALIAS)

    elif new_width + new_height > width + height:
        # enlarge
        image = image.resize((new_width, new_height))

    image.save(new_path, image_format)
    close_image.close()
