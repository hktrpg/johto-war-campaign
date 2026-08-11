import pandas as pd
from PIL import ImageDraw
from tqdm import tqdm

from config import *
from utils import xy, read_cube, get_img, wrapped_text, text_font, title_font, resolve_move_effect


def get_base():
    return get_img(CARD_ASSETS_DIR / 'move_base.png', xy(14.5, 7.5))


def add_header(img, stats):
    d = ImageDraw.Draw(img)

    # Move Type
    type_img = get_img(CARD_ASSETS_DIR / 'types' / f'{stats.move_type}.png', xy(2, 2))
    img.paste(type_img, xy(0.25, 0.25), type_img)

    # Move Name
    wrapped_text(d, stats.move_name, text_font(36), boundaries=(9.5, 1.75), xy=xy(7.25, 1.25), fill=DARK_COLOUR,
                 anchor='mm', align='center')

    # Move Attack Strength
    if stats.move_attack_strength != "blank":
        d.text(xy(13.25, 1.25), str(stats.move_attack_strength), fill=DARK_COLOUR, font=title_font(44), anchor='mm')

    # Archetype Sections Based on stats.archetype_count
    if str(stats.archetype_count) == "1":
        # Add archetype 1 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'1_{stats.archetype_1}.png', xy(14.5, 1.15))
        img.paste(type_img, xy(0, 6.36), type_img)

        # Add archetype 1 text
        text_fill = DARK_COLOUR if stats.archetype_1 in {"RECHARGE 1", "RECHARGE 2", "RECHARGE 3", "RECHARGE 4", "RECHARGE 5", "RECHARGE 6", "RECHARGE 7", "RECHARGE 8", "RECHARGE 9", "SONG", "PROTECT"} else WHITE_COLOUR
        d.text(xy(7.25, 6.91), str(stats.archetype_1), font=title_font(26), fill=text_fill, anchor='mm')

    elif str(stats.archetype_count) == "2":
        # Add archetype 1 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'21_{stats.archetype_1}.png', xy(7.2, 1.15))
        img.paste(type_img, xy(0, 6.36), type_img)

        # Add archetype 2 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'22_{stats.archetype_2}.png', xy(7.2, 1.15))
        img.paste(type_img, xy(7.31, 6.36), type_img)

        # Add archetype 1 text
        text_fill = DARK_COLOUR if stats.archetype_1 in {"RECHARGE 1", "RECHARGE 2", "RECHARGE 3", "RECHARGE 4", "RECHARGE 5", "RECHARGE 6", "RECHARGE 7", "RECHARGE 8", "RECHARGE 9", "SONG", "PROTECT"} else WHITE_COLOUR
        d.text(xy(3.87, 6.91), str(stats.archetype_1), font=title_font(23.5), fill=text_fill, anchor='mm')

        # Add archetype 2 text
        text_fill = DARK_COLOUR if stats.archetype_2 in {"RECHARGE 1", "RECHARGE 2", "RECHARGE 3", "RECHARGE 4", "RECHARGE 5", "RECHARGE 6", "RECHARGE 7", "RECHARGE 8", "RECHARGE 9", "SONG", "PROTECT"} else WHITE_COLOUR
        d.text(xy(10.63, 6.91), str(stats.archetype_2), font=title_font(23.5), fill=text_fill, anchor='mm')

    elif str(stats.archetype_count) == "3":
        # Add archetype 1 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'31_{stats.archetype_1}.png', xy(4.8, 1.15))
        img.paste(type_img, xy(0, 6.36), type_img)

        # Add archetype 2 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'32_{stats.archetype_2}.png', xy(4.8, 1.15))
        img.paste(type_img, xy(4.8575, 6.36), type_img)

        # Add archetype 3 image
        type_img = get_img(CARD_ASSETS_DIR / 'archetypes' / f'33_{stats.archetype_3}.png', xy(4.8, 1.15))
        img.paste(type_img, xy(9.71, 6.36), type_img)

        # Add archetype texts
        archetypes = [stats.archetype_1, stats.archetype_2, stats.archetype_3]
        positions = [(2.58, 6.91), (7.25, 6.91), (11.92, 6.91)]
        for archetype, (x, y) in zip(archetypes, positions):
            text_fill = DARK_COLOUR if archetype in {"RECHARGE 1", "RECHARGE 2", "RECHARGE 3", "RECHARGE 4", "RECHARGE 5", "RECHARGE 6", "RECHARGE 7", "RECHARGE 8", "RECHARGE 9", "SONG", "PROTECT"} else WHITE_COLOUR
            d.text(xy(x, y), str(archetype), font=title_font(17), fill=text_fill, anchor='mm')


def add_description(img, stats):
    d = ImageDraw.Draw(img)

    effect = resolve_move_effect(stats)
    if not effect:
        return
    if str(stats.archetype_count) in {"1", "2", "3"}:
        wrapped_text(d, effect, text_font(28, effect), boundaries=(13.5, 3.6), xy=xy(7.25, 4.27), fill=DARK_COLOUR,
                     anchor='mm', align='center')
    else:
        wrapped_text(d, effect, text_font(28, effect), boundaries=(13.5, 4.5), xy=xy(7.25, 4.75), fill=DARK_COLOUR,
                     anchor='mm', align='center')


def generate_moves(overwrite):
    print('Generating moves:')
    POKEMON_MOVES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='moves')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = POKEMON_MOVES_OUTPUT_DIR / f'{stats.move_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = get_base()
        add_header(img, stats)
        add_description(img, stats)
        img.save(output_path)


def generate_card_backs(overwrite):
    print('Generating card backs:')
    POKEMON_CARD_BACKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='moves')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        output_path = POKEMON_CARD_BACKS_OUTPUT_DIR / f'{stats.move_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = get_img(CARD_ASSETS_DIR / 'card_backs' / f'standard.png', xy(16, 28))
        move_img = get_img(POKEMON_MOVES_OUTPUT_DIR / f'{stats.move_name}.png', xy(14.5, 7.5))
        img.paste(move_img, xy(0.75, 19.75), move_img)
        img.save(output_path)


def run(overwrite=True):
    generate_moves(overwrite)
    generate_card_backs(overwrite)


if __name__ == '__main__':
    run(overwrite=True)
