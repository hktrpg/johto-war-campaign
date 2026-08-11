import pandas as pd
from PIL import ImageDraw
from tqdm import tqdm

from config import *
from utils import xy, read_cube, get_img, wrapped_text, text_font, title_font, bold_font


def get_base():
    return get_img(CARD_ASSETS_DIR / 'move_base.png', xy(14.5, 7.5))


def add_header(img, stats):
    d = ImageDraw.Draw(img)

    # Move Type 1
    type_img = get_img(CARD_ASSETS_DIR / 'types' / f'{stats.move_type}.png', xy(2, 2))
    img.paste(type_img, xy(0.25, 0.25), type_img)

    # Move Name
    name = str(stats.ability_name)
    wrapped_text(d, name, bold_font(36, name), boundaries=(9.5, 1.75), xy=xy(7.25, 1.25), fill=DARK_COLOUR,
                 anchor='mm', align='center')

    # Move Type 2
    type_img = get_img(CARD_ASSETS_DIR / 'types' / f'{stats.move_type2}.png', xy(2,2))
    img.paste(type_img, xy(12.25, 0.25), type_img)


def add_description(img, stats):
    d = ImageDraw.Draw(img)

    effect = str(stats.move_effect)
    wrapped_text(d, effect, text_font(28, effect), boundaries=(13.5, 4.5), xy=xy(7.25, 4.75), fill=DARK_COLOUR,
                 anchor='mm', align='center')


def generate_moves(overwrite):
    print('Generating moves:')
    ABILITY_MOVES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='abilities')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = ABILITY_MOVES_OUTPUT_DIR / f'{stats.ability_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = get_base()
        add_header(img, stats)
        add_description(img, stats)
        img.save(output_path)


def generate_card_backs(overwrite):
    print('Generating card backs:')
    ABILITY_CARD_BACKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='abilities')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = ABILITY_CARD_BACKS_OUTPUT_DIR / f'{stats.ability_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = get_img(CARD_ASSETS_DIR / 'card_backs' / 'Ability.png', xy(16, 28))
        img.save(output_path)


def run(overwrite=True):
    generate_moves(overwrite)
    generate_card_backs(overwrite)


if __name__ == '__main__':
    run(overwrite=True)