from io import BytesIO

import pandas as pd
import requests
from PIL import ImageDraw
from tqdm import tqdm

from config import *
from utils import xy, read_cube, get_img, text_font, title_font, bold_font, wrapped_text  # noqa: F401


#
# Base
#

def compose_base(stats):
    base_img = get_img(CARD_ASSETS_DIR / 'card_bases' / f'{stats.image_type}.png', xy(16, 28))
    return base_img

def add_move(img, stats):
    d = ImageDraw.Draw(img)

    # Determine fill color based on image_type
    fill_color = WHITE_COLOUR if stats.image_type == "Warp" else DARK_COLOUR

    # Header (top sky band)
    header = '神社祝福'
    wrapped_text(d, header, bold_font(40, header), boundaries=(12, 1.6), xy=xy(8, 1.45), fill=WHITE_COLOUR,
                 anchor='mm', align='center')

    # Multiplayer note — single line inside upper white capsule (y≈15.02)
    note = '4人以上：另選一位訓練家也獲得此效果'
    wrapped_text(d, note, bold_font(22, note), boundaries=(13.9, 1.8), xy=xy(8, 15.02), fill=DARK_COLOUR,
                 anchor='mm', align='center')

    # Card name — mid padding in bottom white box (box y≈19.8–27.3)
    name = str(stats.internal_name)
    d.text(xy(8, 20.85), name, fill=fill_color, font=bold_font(36, name), anchor='mm')

    # Effect — centered in remaining lower box area
    wrapped_text(d, stats.card_effect, text_font(28, stats.card_effect), boundaries=(13.5, 5.4), xy=xy(8, 24.1), fill=fill_color,
                 anchor='mm', align='center')
    

def add_emblem(img):
    if VANILLA_EMBLEM_PATH.is_file():
        emblem_name = 'vanilla'
    else:
        emblem_name = 'custom'
    emblem_img = get_img(CARD_ASSETS_DIR / 'emblems' / f'{emblem_name}.png', xy(0.5, 0.5))
    img.paste(emblem_img, xy(15, 27), emblem_img)

def generate_card_backs(overwrite):
    print('Generating card backs:')
    SHRINE_CARD_BACKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='shrine')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = SHRINE_CARD_BACKS_OUTPUT_DIR / f'{stats.utility_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = get_img(CARD_ASSETS_DIR / 'card_backs' / 'Shrine.png', xy(16, 28))
        img.save(output_path)

#
# Entry
#

def run(overwrite=True):
    print('Generating card fronts:')
    
    df = read_cube(sheet_name='shrine')
    for i, stats in tqdm(df.iterrows(), total=df.shape[0]):
        directory_name = stats.image_type if stats.image_type != "Warp" else "Shrine"
        output_dir = (OUTPUT_DIR / directory_name / 'card_fronts')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f'{i}_{stats.utility_name.lower()}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = compose_base(stats)

        add_move(img, stats)
        add_emblem(img)

        img.save(output_path)
    generate_card_backs(overwrite)


if __name__ == '__main__':
    run(overwrite=True)
