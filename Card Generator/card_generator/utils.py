import pandas as pd
from PIL import Image, ImageFont

from config import *


def xy(width_cm, height_cm):
    return int(64 * width_cm), int(64 * height_cm)


def pos(x, y):
    return int(512 * x), int(896 * y)


def _adjusted_font_size(font_size):
    return int(2.25 * font_size)


def text_font(size):
    return ImageFont.truetype(BARLOW_PATH, size=_adjusted_font_size(size))


def title_font(size):
    return ImageFont.truetype(ORIENTAL_PATH, size=_adjusted_font_size(size))


def bold_font(size):
    return ImageFont.truetype(BARLOW_BOLD_PATH, size=_adjusted_font_size(size))


def read_cube(cube_name="johto_cube", sheet_name=None):
    if not sheet_name:
        raise ValueError("The 'sheet_name' parameter is required.")
    df = pd.read_excel(ROOT_DIR / f"{cube_name}.xlsx", sheet_name=sheet_name)
    return df


def get_img(file_path, size):
    return Image.open(file_path).convert("RGBA").resize(size)


def get_text_width(d, text, font):
    bbox = d.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def get_multiline_size(d, text, font):
    bbox = d.multiline_textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrapped_text(d, text, font, boundaries, *args, **kwargs):
    words = text.split(" ")
    multiline_text_list = []
    for word in words:
        if (
            not multiline_text_list
            or get_text_width(d, f"{multiline_text_list[-1]} {word}", font)
            >= xy(*boundaries)[0]
        ):
            multiline_text_list.append("")
        multiline_text_list[-1] += word + " "

    multiline_text = "\n".join(multiline_text_list).strip()
    multi_width, multi_height = get_multiline_size(d, multiline_text, font)
    if multi_width >= xy(*boundaries)[0] or multi_height >= xy(*boundaries)[1]:
        smaller_font = ImageFont.truetype(font.path, size=font.size - 2)
        wrapped_text(d, text, smaller_font, boundaries, *args, **kwargs)
    else:
        d.multiline_text(text=multiline_text, font=font, *args, **kwargs)
