#!/usr/bin/env python3
"""Download TTS CustomDeck sheet images from a save/Workshop JSON and crop to single cards.

Default source for this campaign:
  Documents/My Games/Tabletop Simulator/Saves/TS_AutoSave_2.json
Workshop: https://steamcommunity.com/sharedfiles/filedetails/?id=3274191922
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image
from tqdm import tqdm

Image.MAX_IMAGE_PIXELS = None


def default_tts_root() -> Path:
    home = Path.home()
    candidates = [
        home / "OneDrive" / "Documents" / "My Games" / "Tabletop Simulator",
        home / "Documents" / "My Games" / "Tabletop Simulator",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def cache_name_candidates(url: str) -> list[str]:
    """TTS Mods/Images filenames are URL with punctuation stripped."""
    u = url.strip()
    # Historical cloud-3 form
    u2 = u.replace("https://steamusercontent-a.akamaihd.net", "http://cloud-3.steamusercontent.com")
    u2 = u2.replace("https://steamusercontent-a.akamaihd.net/", "http://cloud-3.steamusercontent.com/")
    variants = [u, u2, u.rstrip("/"), u2.rstrip("/")]
    names = []
    for v in variants:
        stripped = re.sub(r"[^A-Za-z0-9]", "", v)
        names.append(stripped)
        # common: keep leading http without ://
        if v.startswith("https://"):
            names.append(re.sub(r"[^A-Za-z0-9]", "", "http" + v[len("https://") :]))
        if v.startswith("http://"):
            names.append(re.sub(r"[^A-Za-z0-9]", "", "http" + v[len("http://") :]))
    # unique preserve order
    out, seen = [], set()
    for n in names:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def find_in_cache(url: str, image_dirs: list[Path]) -> Path | None:
    stems = cache_name_candidates(url)
    for d in image_dirs:
        if not d.is_dir():
            continue
        for stem in stems:
            for ext in (".png", ".jpg", ".jpeg", ".webp", ""):
                p = d / f"{stem}{ext}"
                if p.is_file() and p.stat().st_size > 0:
                    return p
        # fallback: substring match on ugc id segments
        m = re.search(r"/ugc/(\d+)/([A-Fa-f0-9]+)", url)
        if m:
            a, b = m.group(1), m.group(2)
            for p in d.iterdir():
                if p.is_file() and a in p.name and b in p.name:
                    return p
    return None


def walk_custom_decks(obj, decks: list[dict]):
    if isinstance(obj, dict):
        cd = obj.get("CustomDeck")
        if isinstance(cd, dict):
            for did, meta in cd.items():
                if not isinstance(meta, dict):
                    continue
                face = meta.get("FaceURL") or meta.get("faceURL")
                back = meta.get("BackURL") or meta.get("backURL")
                nw = int(meta.get("NumWidth") or meta.get("numWidth") or 1)
                nh = int(meta.get("NumHeight") or meta.get("numHeight") or 1)
                if face:
                    decks.append(
                        {
                            "nickname": obj.get("Nickname") or obj.get("Name") or "",
                            "name": obj.get("Name") or "",
                            "guid": obj.get("GUID") or "",
                            "deck_id": str(did),
                            "face": face,
                            "back": back,
                            "nw": nw,
                            "nh": nh,
                            "cards": int(obj.get("NumberOfCards") or 0) or None,
                        }
                    )
        for v in obj.values():
            walk_custom_decks(v, decks)
    elif isinstance(obj, list):
        for v in obj:
            walk_custom_decks(v, decks)


def safe_stem(url: str) -> str:
    m = re.search(r"/ugc/(\d+)/([A-Fa-f0-9]+)", url)
    if m:
        return f"ugc_{m.group(1)}_{m.group(2)[:12]}"
    path = urlparse(url).path.replace("/", "_").strip("_")
    return re.sub(r"[^A-Za-z0-9_-]", "", path)[:80] or "sheet"


def download(url: str, dest: Path, session: requests.Session) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    r = session.get(url, timeout=120)
    r.raise_for_status()
    ctype = (r.headers.get("content-type") or "").lower()
    ext = dest.suffix
    if not ext:
        if "jpeg" in ctype or "jpg" in ctype:
            dest = dest.with_suffix(".jpg")
        elif "webp" in ctype:
            dest = dest.with_suffix(".webp")
        else:
            dest = dest.with_suffix(".png")
    dest.write_bytes(r.content)
    return dest


def crop_sheet(sheet_path: Path, nw: int, nh: int, out_dir: Path, prefix: str) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(sheet_path).convert("RGBA")
    w, h = im.size
    cw, ch = w // nw, h // nh
    if cw < 1 or ch < 1:
        raise ValueError(f"bad grid {nw}x{nh} for {sheet_path} size={im.size}")
    n = 0
    for row in range(nh):
        for col in range(nw):
            idx = row * nw + col + 1
            card = im.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
            # skip nearly empty tiles (common trailing empties on TTS sheets)
            extrema = card.getextrema()
            alpha = extrema[3] if len(extrema) == 4 else None
            if alpha and alpha[1] == 0:
                continue
            # also skip fully transparent-ish / tiny content
            bbox = card.getbbox()
            if bbox is None:
                continue
            out = out_dir / f"{prefix}_{idx:03d}.png"
            card.save(out)
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Download & crop TTS CustomDeck sheets")
    ap.add_argument(
        "--save",
        type=Path,
        default=None,
        help="TTS save/Workshop JSON (default: newest large AutoSave)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("tts_extract_3274191922"),
        help="Output directory",
    )
    ap.add_argument("--download-only", action="store_true")
    ap.add_argument("--crop-only", action="store_true")
    ap.add_argument(
        "--min-tiles",
        type=int,
        default=2,
        help="Only crop sheets with nw*nh >= this (default 2)",
    )
    ap.add_argument("--limit", type=int, default=0, help="Limit unique sheets (0=all)")
    args = ap.parse_args()

    tts = default_tts_root()
    image_dirs = [tts / "Mods" / "Images", tts / "Mods" / "Images Raw"]

    save = args.save
    if save is None:
        saves = tts / "Saves"
        candidates = sorted(
            list(saves.glob("TS_AutoSave*.json")) + list(saves.glob("TS_Save_*.json")),
            key=lambda p: p.stat().st_size,
            reverse=True,
        )
        if not candidates:
            print("No TTS save JSON found under", saves, file=sys.stderr)
            sys.exit(1)
        save = candidates[0]

    print("TTS root:", tts)
    print("Save:", save, f"({save.stat().st_size/1024/1024:.1f} MB)")

    data = json.loads(save.read_text(encoding="utf-8", errors="replace"))
    print("SaveName:", data.get("SaveName"), "| GameMode:", data.get("GameMode"))

    decks: list[dict] = []
    walk_custom_decks(data, decks)
    print("CustomDeck object entries:", len(decks))

    # unique sheets by (face,nw,nh)
    sheets: dict[tuple, dict] = {}
    for d in decks:
        key = (d["face"], d["nw"], d["nh"])
        if key not in sheets:
            sheets[key] = {**d, "refs": 1}
        else:
            sheets[key]["refs"] += 1

    sheet_list = sorted(sheets.values(), key=lambda x: (-(x["nw"] * x["nh"]), -x["refs"]))
    if args.limit:
        sheet_list = sheet_list[: args.limit]

    out = args.out
    sheets_dir = out / "sheets"
    cards_dir = out / "cards"
    out.mkdir(parents=True, exist_ok=True)

    manifest = []
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; tts-extract/1.0)"

    print("Unique sheets:", len(sheet_list))
    for s in tqdm(sheet_list, desc="sheets"):
        face = s["face"]
        stem = safe_stem(face)
        prefix = f"{stem}_{s['nw']}x{s['nh']}"
        entry = {
            "face": face,
            "nw": s["nw"],
            "nh": s["nh"],
            "refs": s["refs"],
            "nickname_sample": s["nickname"],
            "prefix": prefix,
        }

        local = None
        if not args.crop_only:
            cached = find_in_cache(face, image_dirs)
            dest = sheets_dir / f"{prefix}"
            try:
                if cached:
                    # copy/link into sheets dir with stable name
                    ext = cached.suffix or ".png"
                    dest = dest.with_suffix(ext)
                    if not dest.exists():
                        dest.write_bytes(cached.read_bytes())
                    local = dest
                    entry["source"] = f"cache:{cached.name}"
                else:
                    dest = download(face, dest, session)
                    local = dest
                    entry["source"] = "download"
            except Exception as e:
                entry["error"] = str(e)
                manifest.append(entry)
                continue
        else:
            # find existing sheet file
            matches = list(sheets_dir.glob(f"{prefix}.*"))
            local = matches[0] if matches else None
            if not local:
                entry["error"] = "sheet missing for crop-only"
                manifest.append(entry)
                continue

        entry["sheet"] = str(local.relative_to(out)) if local else None

        tiles = s["nw"] * s["nh"]
        if not args.download_only and tiles >= args.min_tiles and local:
            try:
                n = crop_sheet(local, s["nw"], s["nh"], cards_dir / prefix, prefix)
                entry["cropped_cards"] = n
            except Exception as e:
                entry["crop_error"] = str(e)

        manifest.append(entry)

    (out / "manifest.json").write_text(
        json.dumps(
            {
                "save": str(save),
                "save_name": data.get("SaveName"),
                "workshop": "https://steamcommunity.com/sharedfiles/filedetails/?id=3274191922",
                "sheets": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    ok = sum(1 for e in manifest if not e.get("error"))
    cropped = sum(e.get("cropped_cards") or 0 for e in manifest)
    print(f"Done. sheets_ok={ok}/{len(manifest)} cropped_cards={cropped}")
    print("Output:", out.resolve())


if __name__ == "__main__":
    main()
