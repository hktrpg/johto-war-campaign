import re

import pandas as pd
from PIL import Image, ImageFont

from config import *

_CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f\uff00-\uffef]')


def xy(width_cm, height_cm):
    return int(64 * width_cm), int(64 * height_cm)


def pos(x, y):
    return int(512 * x), int(896 * y)


def _adjusted_font_size(font_size):
    return int(2.25 * font_size)


def _needs_cjk_font(text) -> bool:
    """True when text needs a CJK-capable font (Chinese or fullwidth forms)."""
    return isinstance(text, str) and bool(_CJK_RE.search(text))


def text_font(size, text=None):
    path = CJK_FONT_PATH if _needs_cjk_font(text) else BARLOW_PATH
    return ImageFont.truetype(path, size=_adjusted_font_size(size))


def title_font(size, text=None):
    path = CJK_FONT_PATH if _needs_cjk_font(text) else ORIENTAL_PATH
    return ImageFont.truetype(path, size=_adjusted_font_size(size))


def bold_font(size, text=None):
    path = CJK_BOLD_FONT_PATH if _needs_cjk_font(text) else BARLOW_BOLD_PATH
    return ImageFont.truetype(path, size=_adjusted_font_size(size))


def read_cube(cube_name='johto_cube', sheet_name=None):
    if not sheet_name:
        raise ValueError("The 'sheet_name' parameter is required.")
    df = pd.read_excel(ROOT_DIR / f'{cube_name}.xlsx', sheet_name=sheet_name)
    return df


def _is_blank_effect(value) -> bool:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return True
    text = str(value).strip()
    return text == '' or text.lower() in {'nan', 'none'}


# Rulebook MOVE ARCHETYPES (Johto War v1.0.2), Traditional Chinese for card text.
# Labels with no secondary effect (SONG / DANCE / BOMB / MODIFY / PERSISTING) are omitted.
_ARCHETYPE_EFFECTS = {
    'SWITCH': '使用此招式後，使用者可以替換退場。',
    'MULTI': '攻擊所有敵方寶可夢。若只有一個目標，攻擊強度+1。',
    'MULTI ALL': '攻擊其他所有場上寶可夢。若只有一個目標，攻擊強度+1。',
    'PROTECT': '本回合剩餘時間內，使用者不受傷害並忽略攻擊效果。若上回合使用過保護類招式，本回合不可再使用。',
    'FORM': '若此招式為使用者的招牌招式，使用後進行型態變化。',
}


def archetype_effect_text(archetype) -> str:
    """Return rule text for a single archetype label, or '' if none / label-only."""
    if archetype is None or (isinstance(archetype, float) and pd.isna(archetype)):
        return ''
    key = str(archetype).strip()
    if not key or key.lower() in {'nan', 'none'}:
        return ''
    if key in _ARCHETYPE_EFFECTS:
        return _ARCHETYPE_EFFECTS[key]
    if key.startswith('PRIORITY'):
        return '此招式會比優先度較低或無優先度的招式先發動。負優先度則較晚發動。'
    if key.startswith('RECHARGE'):
        n = key.split()[-1]
        return f'使用者下次攻擊擲骰時少擲{n}顆骰。不受挑釁影響。'
    if key.startswith('DELAY'):
        n = key.split()[-1]
        return f'此攻擊的骰子在{n}回合後才擲出。擲骰當回合，使用者必須嘗試使出此招式。'
    return ''


def resolve_move_effect(stats) -> str:
    """Use move_effect when present; if blank, fall back to archetype rule text."""
    effect = getattr(stats, 'move_effect', None)
    if not _is_blank_effect(effect):
        return str(effect).strip()

    parts = []
    seen = set()
    for attr in ('archetype_1', 'archetype_2', 'archetype_3'):
        arch = getattr(stats, attr, None)
        text = archetype_effect_text(arch)
        if text and text not in seen:
            parts.append(text)
            seen.add(text)

    arches = [
        str(getattr(stats, attr)).strip()
        for attr in ('archetype_1', 'archetype_2', 'archetype_3')
        if not _is_blank_effect(getattr(stats, attr, None))
    ]
    if any(a.startswith('PROTECT') for a in arches) and any(a.startswith('DELAY') for a in arches):
        combo = '當保護與延遲同時使用時，保護效果持續至擲骰為止。'
        if combo not in seen:
            parts.append(combo)

    return '\n'.join(parts)


def get_img(file_path, size):
    return Image.open(file_path).convert('RGBA').resize(size)


def _text_size(d, text, font):
    if hasattr(d, 'textbbox'):
        left, top, right, bottom = d.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    return d.textsize(text, font)


def _font_file(font):
    return getattr(font, 'path', None) or CJK_FONT_PATH


def _shrink_font(font, delta=2):
    return ImageFont.truetype(_font_file(font), size=max(2, font.size - delta))


def _ensure_font_for_text(font, text):
    """Swap in CJK/bold-CJK when the requested font cannot cover the string."""
    if not _needs_cjk_font(text):
        return font
    path = str(_font_file(font)).lower()
    if 'msyh' in path or 'msjh' in path:
        return font
    cjk_path = CJK_BOLD_FONT_PATH if 'bold' in path else CJK_FONT_PATH
    return ImageFont.truetype(cjk_path, size=font.size)


def _wrap_token_lines(text: str):
    """Split for wrapping: keep explicit newlines; CJK wraps per char, Latin by word."""
    lines = str(text).split('\n')
    token_lines = []
    for line in lines:
        if _needs_cjk_font(line):
            token_lines.append(list(line) if line else [''])
        else:
            token_lines.append(line.split(' ') if line else [''])
    return token_lines


def wrapped_text(d, text, font, boundaries, *args, **kwargs):
    text = '' if text is None else str(text)
    font = _ensure_font_for_text(font, text)

    max_w, max_h = xy(*boundaries)
    is_cjk = _needs_cjk_font(text)
    joined_lines = []
    for tokens in _wrap_token_lines(text):
        current = ''
        for token in tokens:
            if is_cjk:
                candidate = current + token
            else:
                candidate = token if not current else f'{current} {token}'
            if current and _text_size(d, candidate, font)[0] >= max_w:
                joined_lines.append(current.rstrip())
                current = token
            else:
                current = candidate
        joined_lines.append((current or '').rstrip())

    multiline_text = '\n'.join(joined_lines).strip()
    text_w, text_h = _text_size(d, multiline_text, font)
    if text_w >= max_w or text_h >= max_h:
        wrapped_text(d, text, _shrink_font(font), boundaries, *args, **kwargs)
    else:
        d.multiline_text(text=multiline_text, font=font, *args, **kwargs)
