"""Apply Traditional Chinese polish to johto_cube.xlsx from translation JSON + dictionaries."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "Card Generator"
ZH_PATH = ROOT / "johto_cube.xlsx"
ENG_PATH = ROOT / "johto_cube_ENG.xlsx"
BACKUP_PATH = ROOT / "johto_cube.pre_translate_backup.xlsx"

LEGEND_NAMES = {
    "Arceus": "阿爾宙斯",
    "Articuno": "急凍鳥",
    "Celebi": "時拉比",
    "Cresselia": "克雷色利亞",
    "Darkrai": "達克萊伊",
    "Dialga": "帝牙盧卡",
    "Entei": "炎帝",
    "Eternatus": "無極汰那",
    "Galarian Articuno": "伽勒爾急凍鳥",
    "Galarian Moltres": "伽勒爾火焰鳥",
    "Galarian Zapdos": "伽勒爾閃電鳥",
    "Giratina": "騎拉帝納",
    "Groudon": "固拉多",
    "Ho-Oh": "鳳王",
    "Keldeo": "凱路迪歐",
    "Kyogre": "蓋歐卡",
    "Latias": "拉帝亞斯",
    "Latios": "拉帝歐斯",
    "Lugia": "洛奇亞",
    "Mew": "夢幻",
    "Moltres": "火焰鳥",
    "Necrozma": "奈克洛茲瑪",
    "Palkia": "帕路奇亞",
    "Raikou": "雷公",
    "Rayquaza": "烈空坐",
    "Suicune": "水君",
    "Type: Null": "屬性：空",
    "Zapdos": "閃電鳥",
    "Zygarde": "基格爾德",
}

BOON_ITEM_ZH = {
    "Judgement Plate": "裁決石板",
    "Frost Feather": "冰霜之羽",
    "check Memory Disc item": "詳見記憶碟道具",
}

NAME_FIXES_BY_DEX = {
    "483-o": "帝牙盧卡",
    "483-o-shiny": "帝牙盧卡",
    "484-o": "帕路奇亞",
    "484-o-shiny": "帕路奇亞",
    "487-o": "騎拉帝納",
    "487-o-shiny": "騎拉帝納",
    "492-s": "謝米",
    "492-s-shiny": "謝米",
    "669": "花蓓蓓",
    "669-shiny": "花蓓蓓",
    "130-shiny": "暴鯉龍",
    "793-f": "虛吾伊德",
}

OTHERS_NAME_OVERRIDES = {
    180: "蘿絲安妮",  # ROSEANNE (was wrongly 小光)
    184: "芙蓉",  # SKYLA
    88: "冒險者",  # match trainer_cards
}

GENUS_FALLBACK = {
    "Candy Apple Pokémon": "糖蘋果寶可夢",
    "Matcha Pokémon": "抹茶寶可夢",
    "Retainer Pokémon": "侍從寶可夢",
    "Mask Pokémon": "面具寶可夢",
    "Apple Hydra Pokémon": "蘋果多頭龍寶可夢",
    "Tera Pokémon": "太晶寶可夢",
    "Subjugation Pokémon": "支配寶可夢",
}


def load_genus_map() -> dict[str, str]:
    dex_genus: dict[int, str] = {}
    with open(ROOT / "_pokemon_species_names.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["local_language_id"] == "4" and row["genus"]:
                dex_genus[int(row["pokemon_species_id"])] = row["genus"]

    class_to_dex = json.loads((ROOT / "_class_to_dex.json").read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for eng_class, dex in class_to_dex.items():
        if dex in dex_genus:
            out[eng_class] = dex_genus[dex]
        elif eng_class in GENUS_FALLBACK:
            out[eng_class] = GENUS_FALLBACK[eng_class]
    out.update(GENUS_FALLBACK)
    return out


def build_name_dict(sheets: dict[str, pd.DataFrame]) -> dict[str, str]:
    s1 = sheets["sheet1"]
    en_col, zh_col = s1.columns[0], s1.columns[1]
    mp = {str(en_col): str(zh_col)}
    mp.update({str(a): str(b) for a, b in zip(s1[en_col], s1[zh_col]) if pd.notna(a) and pd.notna(b)})
    return mp


def apply_others(df: pd.DataFrame, eng: pd.DataFrame) -> pd.DataFrame:
    translations = {
        x["i"]: x
        for x in json.loads((ROOT / "_others_translations.json").read_text(encoding="utf-8"))
    }
    out = df.copy()
    # Restore image_type as first column (ZH file currently mislabeled)
    cols = list(out.columns)
    cols[0] = "image_type"
    out.columns = cols
    out["image_type"] = eng["image_type"].values
    for i, tr in translations.items():
        name = OTHERS_NAME_OVERRIDES.get(i, tr["card_name"])
        out.at[i, "card_name"] = name
        out.at[i, "card_effect"] = tr["card_effect"]
    return out


def apply_legacy(df: pd.DataFrame) -> pd.DataFrame:
    rows = json.loads((ROOT / "_legacy_translations.json").read_text(encoding="utf-8"))
    out = df.copy()
    for row in rows:
        i = row["i"]
        for key in (
            "trainer_class",
            "ability_1_name",
            "ability_1_description",
            "ability_2_name",
            "ability_2_description",
        ):
            out.at[i, key] = row[key]
    return out


def apply_abilities(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["classification"] = "特性卡"
    # Normalize first column name if needed
    if out.columns[0] != "ability_name" and "Unnamed: 0" in out.columns:
        out = out.rename(columns={"Unnamed: 0": "ability_name"})
    return out


def apply_legend(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["classification"] = "傳說任務"
    for i, row in out.iterrows():
        en_name = row["card_name"]
        if isinstance(en_name, str) and en_name in LEGEND_NAMES:
            zh = LEGEND_NAMES[en_name]
            out.at[i, "card_name"] = zh
            if pd.isna(row["pokedex_name"]) or (
                isinstance(row["pokedex_name"], str)
                and not re.search(r"[\u4e00-\u9fff]", row["pokedex_name"])
            ):
                out.at[i, "pokedex_name"] = zh
        boon = row["boon"]
        if isinstance(boon, str) and boon in BOON_ITEM_ZH:
            out.at[i, "boon"] = BOON_ITEM_ZH[boon]
    return out


def apply_pokemon(df: pd.DataFrame, eng: pd.DataFrame, genus_map: dict[str, str]) -> pd.DataFrame:
    del eng  # sheets can be row-misaligned; translate ZH classification text in place
    out = df.copy()
    for i, row in out.iterrows():
        eng_class = row["classification"]
        if isinstance(eng_class, str) and eng_class in genus_map:
            out.at[i, "classification"] = genus_map[eng_class]
        name = row["pokedex_name"]
        dex = str(row["pokedex_number"])
        needs = pd.isna(name) or str(name).lower() == "nan" or not re.search(
            r"[\u4e00-\u9fff]", str(name)
        )
        if needs and dex in NAME_FIXES_BY_DEX:
            out.at[i, "pokedex_name"] = NAME_FIXES_BY_DEX[dex]
    return out


def main() -> None:
    zh_sheets = pd.read_excel(ZH_PATH, sheet_name=None)
    eng_sheets = pd.read_excel(ENG_PATH, sheet_name=None)

    if not BACKUP_PATH.exists():
        with pd.ExcelWriter(BACKUP_PATH, engine="openpyxl") as writer:
            for name, df in zh_sheets.items():
                df.to_excel(writer, sheet_name=name, index=False)
        print(f"Backup written: {BACKUP_PATH}")

    genus_map = load_genus_map()
    zh_sheets["others"] = apply_others(zh_sheets["others"], eng_sheets["others"])
    zh_sheets["trainer_cards_legacy"] = apply_legacy(zh_sheets["trainer_cards_legacy"])
    zh_sheets["abilities"] = apply_abilities(zh_sheets["abilities"])
    zh_sheets["legend"] = apply_legend(zh_sheets["legend"])
    zh_sheets["pokemon"] = apply_pokemon(zh_sheets["pokemon"], eng_sheets["pokemon"], genus_map)

    with pd.ExcelWriter(ZH_PATH, engine="openpyxl") as writer:
        for name, df in zh_sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

    print("Updated", ZH_PATH)


if __name__ == "__main__":
    main()
