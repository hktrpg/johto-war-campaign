#!/usr/bin/env python3
"""Crop generator_assets components from TTS finished cards (true art, not placeholders)."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Card Generator" / "generator_assets"
TTS = ROOT / "tts_extract_3274191922" / "cards"

GAMBLE_DIR = TTS / "ugc_9592057910454539512_F208923E354E_10x7"
ZINNIA_TACTIC = TTS / "ugc_11028791174481059789_8A2CCA496032_10x7" / "013_Zinnia.png"
ZINNIA_POKE = TTS / "ugc_12950069160474438173_1B24CE174C71_10x7" / "035_Altaria (Lore Keeper Zinnia).png"

# Cube order = sheet slots 001-022
GAMBLE_NAMES = [
    "ability_capsule_gamble_card",
    "apricorn_cache_gamble_card",
    "huge_apricorn_cache_gamble_card",
    "journey_reward_gamble_card",
    "wonder_egg_gamble_card",
    "dining_voucher_gamble_card",
    "plus_1_gamble_card",
    "plus_2_gamble_card",
    "plus_3_gamble_card",
    "plus_5_gamble_card",
    "minus_1_gamble_card",
    "minus_2_gamble_card",
    "minus_3_gamble_card",
    "minus_5_gamble_card",
    "double!_gamble_card",
    "triple!_gamble_card",
    "bankrupt!_gamble_card",
    "half!_gamble_card",
    "gambling_odds_gamble_card",
    "gambling_evens_gamble_card",
    "insider_trading_gamble_card",
    "risk_it_all_gamble_card",
]

BACK_TYPES = {
    1: "PRIZE GAMBLE CARD",  # slots 1-6
    7: "ADDITIVE GAMBLE CARD",  # 7-14
    15: "MULTIPLY GAMBLE CARD",  # 15-18
    19: "BETTING GAMBLE CARD",  # 19-22
}


def load(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def find_gamble_file(slot: int) -> Path:
    matches = sorted(GAMBLE_DIR.glob(f"{slot:03d}_*.png"))
    if not matches:
        raise FileNotFoundError(slot)
    return matches[0]


def blank_panel(draw: ImageDraw.ImageDraw, box, fill):
    draw.rounded_rectangle(box, radius=12, fill=fill)


# Native TTS art window on 512x896 cards (aspect ≈1.355).
# Export at 2x for generator 1024x1792 — never squash to 400x260.
GAMBLE_TTS_ART_BOX = (40, 197, 471, 515)  # left, top, right, bottom
GAMBLE_ART_SCALE = 2


def crop_gamble_art(card: Image.Image) -> Image.Image:
    """Middle illustration window on 512x896 Gamble cards (aspect-preserving)."""
    left, top, right, bottom = GAMBLE_TTS_ART_BOX
    art = card.crop((left, top, right, bottom))
    tw = (right - left) * GAMBLE_ART_SCALE
    th = (bottom - top) * GAMBLE_ART_SCALE
    return art.resize((tw, th), Image.Resampling.LANCZOS)


def make_gamble_base(template: Image.Image) -> Image.Image:
    """Strip title/effect text and art from a finished Gamble card → empty base."""
    img = template.copy()
    w, h = img.size
    arr = np.array(img)

    header_gray = tuple(int(x) for x in arr[100, w // 2, :3])
    footer_gray = tuple(int(x) for x in arr[700, w // 2, :3])
    # orange frame color under subtitle area
    frame_orange = tuple(int(x) for x in arr[int(h * 0.185), w // 2, :3])
    d = ImageDraw.Draw(img)
    # Header name plate
    blank_panel(d, (int(w * 0.12), int(h * 0.045), int(w * 0.88), int(h * 0.145)), header_gray + (255,))
    # Subtitle band on orange frame
    d.rectangle((int(w * 0.15), int(h * 0.145), int(w * 0.85), int(h * 0.195)), fill=frame_orange + (255,))
    # Art window → black
    d.rectangle((int(w * 0.06), int(h * 0.205), int(w * 0.94), int(h * 0.585)), fill=(0, 0, 0, 255))
    # Footer
    blank_panel(d, (int(w * 0.08), int(h * 0.60), int(w * 0.92), int(h * 0.93)), footer_gray + (255,))

    return img.resize((600, 1050), Image.Resampling.LANCZOS)


GAMBLE_BACK_URL = (
    "https://steamusercontent-a.akamaihd.net/ugc/"
    "16557639718947582271/E250A618C08717099C1DACBE9B61EF4688E4CA86/"
)


def download_gamble_back_sheet() -> Image.Image:
    """TTS UniqueBack sheet for Gamble (10x7, first 22 tiles used)."""
    import requests

    cache = ROOT / "tts_extract_3274191922" / "sheets" / "gamble_back_sheet_tts.png"
    if not cache.is_file():
        r = requests.get(GAMBLE_BACK_URL, timeout=120, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(r.content)
    return load(cache)


def crop_sheet_tile(sheet: Image.Image, index_1based: int, nw: int = 10, nh: int = 7) -> Image.Image:
    w, h = sheet.size
    cw, ch = w // nw, h // nh
    i = index_1based - 1
    col, row = i % nw, i // nw
    return sheet.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))


def make_zinnia_climate(card: Image.Image) -> Image.Image:
    """Build climate from Lore Keeper Zinnia TTS card edge stars + brown fill."""
    clair = load(ASSETS / "climates" / "Clair.png")
    # Use Clair as structure only for size; paint with Zinnia TTS colors/stars
    w, h = 406, 720
    arr = np.array(card.convert("RGBA"))
    ch, cw = arr.shape[:2]
    # Sample brown from left margin
    bg = arr[int(ch * 0.30), 12, :3].astype(np.float32)
    out = np.zeros((h, w, 4), dtype=np.uint8)
    # Vertical gradient from lighter brown (top) to darker (bottom) using TTS samples
    top_c = arr[int(ch * 0.15), 15, :3].astype(np.float32)
    bot_c = arr[int(ch * 0.50), 15, :3].astype(np.float32)
    for y in range(h):
        t = y / max(h - 1, 1)
        col = top_c * (1 - t) + bot_c * t
        out[y, :, :3] = col.astype(np.uint8)
        out[y, :, 3] = 255

    # Stamp real star pixels from TTS card side strips (scaled)
    strip = card.crop((0, int(ch * 0.12), int(cw * 0.14), int(ch * 0.55))).resize(
        (int(w * 0.18), int(h * 0.45)), Image.Resampling.LANCZOS
    )
    strip_r = card.crop((int(cw * 0.86), int(ch * 0.12), cw, int(ch * 0.55))).resize(
        (int(w * 0.18), int(h * 0.45)), Image.Resampling.LANCZOS
    )
    base = Image.fromarray(out, "RGBA")
    base.alpha_composite(strip, (int(w * 0.02), int(h * 0.08)))
    base.alpha_composite(strip_r, (int(w * 0.80), int(h * 0.28)))
    # Extra stars from top band
    top_band = card.crop((int(cw * 0.15), int(ch * 0.12), int(cw * 0.45), int(ch * 0.20))).resize(
        (int(w * 0.40), int(h * 0.08)), Image.Resampling.LANCZOS
    )
    base.alpha_composite(top_band, (int(w * 0.25), int(h * 0.12)))
    return base


def make_zinnia_tactic_base(card: Image.Image) -> Image.Image:
    """Blank move/ability text from Zinnia tactics card → tactic_bases/Zinnia.png."""
    img = card.copy()
    w, h = img.size
    arr = np.array(img)
    gray = tuple(int(x) for x in arr[int(h * 0.28), w // 2, :3])
    d = ImageDraw.Draw(img)
    # Cover entire upper + lower panels fully (including leftover footer lines)
    d.rounded_rectangle((int(w * 0.05), int(h * 0.12), int(w * 0.95), int(h * 0.50)), radius=18, fill=gray + (255,))
    d.rounded_rectangle((int(w * 0.05), int(h * 0.53), int(w * 0.95), int(h * 0.92)), radius=18, fill=gray + (255,))
    return img.resize((870, 1242), Image.Resampling.LANCZOS)


def make_zinnia_button(card: Image.Image) -> Image.Image:
    """Crop center button between the two tactic panels."""
    w, h = card.size
    # Small circle between panels ~ mid height
    cx, cy = w // 2, int(h * 0.515)
    r = int(w * 0.055)
    btn = card.crop((cx - r, cy - r, cx + r, cy + r))
    return btn.resize((117, 119), Image.Resampling.LANCZOS)


def main():
    print("=== Gamble card_images ===")
    out_img = ASSETS / "card_images"
    out_img.mkdir(parents=True, exist_ok=True)
    for i, uname in enumerate(GAMBLE_NAMES, start=1):
        src = find_gamble_file(i)
        art = crop_gamble_art(load(src))
        dest = out_img / f"{uname}.png"
        art.save(dest)
        print(" ", dest.name, art.size)

    print("=== Gamble base ===")
    base = make_gamble_base(load(find_gamble_file(7)))  # PLUS 1 clean geometric art
    base_path = ASSETS / "card_bases" / "Gamble.png"
    base.save(base_path)
    print(" ", base_path, base.size)

    print("=== Gamble backs (UniqueBack sheet tiles by type) ===")
    back_dir = ASSETS / "card_backs"
    sheet = download_gamble_back_sheet()
    # Representative tile index (1-based on 10x7 sheet) per utility_type
    back_tiles = {
        "PRIZE GAMBLE CARD": 1,
        "ADDITIVE GAMBLE CARD": 7,
        "MULTIPLY GAMBLE CARD": 15,
        "BETTING GAMBLE CARD": 19,
    }
    for label, idx in back_tiles.items():
        tile = crop_sheet_tile(sheet, idx).resize((600, 1050), Image.Resampling.LANCZOS)
        dest = back_dir / f"{label}.png"
        tile.save(dest)
        print(" ", dest.name, tile.size, f"(sheet #{idx})")

    print("=== Zinnia climate ===")
    climate = make_zinnia_climate(load(ZINNIA_POKE))
    climate_path = ASSETS / "climates" / "Zinnia.png"
    climate.save(climate_path)
    # also lowercase for code path .lower()
    climate.save(ASSETS / "climates" / "zinnia.png")
    print(" ", climate_path, climate.size)

    print("=== Zinnia tactic_bases ===")
    zt = load(ZINNIA_TACTIC)
    tb = make_zinnia_tactic_base(zt)
    tb_path = ASSETS / "tactic_bases" / "Zinnia.png"
    tb.save(tb_path)
    btn = make_zinnia_button(zt)
    btn_path = ASSETS / "tactic_bases" / "Zinnia_button.png"
    btn.save(btn_path)
    print(" ", tb_path, tb.size)
    print(" ", btn_path, btn.size)

    print("=== aliases ===")
    # vanilla / default from existing real assets
    custom = ASSETS / "emblems" / "custom.png"
    vanilla = ASSETS / "emblems" / "vanilla.png"
    if custom.exists() and not vanilla.exists():
        vanilla.write_bytes(custom.read_bytes())
        print("  vanilla.png <- custom.png")
    standard = ASSETS / "card_backs" / "standard.png"
    default = ASSETS / "card_backs" / "default.png"
    if standard.exists() and not default.exists():
        default.write_bytes(standard.read_bytes())
        print("  default.png <- standard.png")

    print("DONE")


if __name__ == "__main__":
    main()
