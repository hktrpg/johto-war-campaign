#!/usr/bin/env python3
"""Rename cropped TTS cards using Nickname from a save JSON (CardID mapping)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize(name: str, max_len: int = 80) -> str:
    name = (name or "").strip()
    name = INVALID.sub("_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    return (name or "unnamed")[:max_len]


def safe_stem(url: str) -> str:
    m = re.search(r"/ugc/(\d+)/([A-Fa-f0-9]+)", url or "")
    if m:
        return f"ugc_{m.group(1)}_{m.group(2)[:12]}"
    return "sheet"


def walk_cards(obj, face_to_names: dict[str, dict[int, str]], face_to_grid: dict[str, tuple[int, int]]):
    if isinstance(obj, dict):
        cd = obj.get("CustomDeck")
        if isinstance(cd, dict):
            for did, meta in cd.items():
                if not isinstance(meta, dict):
                    continue
                face = meta.get("FaceURL") or meta.get("faceURL")
                if not face:
                    continue
                nw = int(meta.get("NumWidth") or 1)
                nh = int(meta.get("NumHeight") or 1)
                face_to_grid[face] = (nw, nh)
                cid = obj.get("CardID")
                nick = obj.get("Nickname")
                if cid is not None and nick:
                    try:
                        idx = int(cid) - int(did) * 100
                    except (TypeError, ValueError):
                        continue
                    if 0 <= idx < nw * nh:
                        # keep first non-empty nickname for index
                        face_to_names.setdefault(face, {})
                        if idx not in face_to_names[face] or not face_to_names[face][idx]:
                            face_to_names[face][idx] = str(nick)
        for v in obj.values():
            walk_cards(v, face_to_names, face_to_grid)
    elif isinstance(obj, list):
        for v in obj:
            walk_cards(v, face_to_names, face_to_grid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--save",
        type=Path,
        default=Path.home()
        / "OneDrive"
        / "Documents"
        / "My Games"
        / "Tabletop Simulator"
        / "Saves"
        / "TS_AutoSave_2.json",
    )
    ap.add_argument("--extract-dir", type=Path, default=Path("tts_extract_3274191922"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(args.save.read_text(encoding="utf-8", errors="replace"))
    face_to_names: dict[str, dict[int, str]] = {}
    face_to_grid: dict[str, tuple[int, int]] = {}
    walk_cards(data, face_to_names, face_to_grid)

    cards_root = args.extract_dir / "cards"
    if not cards_root.is_dir():
        print("missing", cards_root, file=sys.stderr)
        sys.exit(1)

    # prefix -> face url (from manifest if present)
    prefix_to_face: dict[str, str] = {}
    man_path = args.extract_dir / "manifest.json"
    if man_path.is_file():
        man = json.loads(man_path.read_text(encoding="utf-8"))
        for s in man.get("sheets", []):
            prefix_to_face[s["prefix"]] = s["face"]

    renamed = 0
    unnamed = 0
    for folder in sorted(cards_root.iterdir()):
        if not folder.is_dir():
            continue
        prefix = folder.name
        face = prefix_to_face.get(prefix)
        if not face:
            # try reconstruct from prefix ugc_ID_HASH_WxH
            m = re.match(r"ugc_(\d+)_([A-Fa-f0-9]+)_(\d+)x(\d+)$", prefix)
            if m:
                # find face containing these
                for f in face_to_names:
                    if m.group(1) in f and m.group(2) in f:
                        face = f
                        break
        names = face_to_names.get(face or "", {})
        for png in sorted(folder.glob(f"{prefix}_*.png")):
            m = re.search(r"_(\d+)\.png$", png.name)
            if not m:
                continue
            file_idx = int(m.group(1))  # 1-based crop index
            card_idx = file_idx - 1  # TTS CardID offset is 0-based for this save
            nick = names.get(card_idx) or names.get(file_idx)
            if nick:
                new_name = f"{file_idx:03d}_{sanitize(nick)}.png"
                unnamed_flag = False
            else:
                new_name = f"{file_idx:03d}_unnamed.png"
                unnamed_flag = True
            dest = folder / new_name
            if dest.resolve() == png.resolve():
                continue
            # avoid collisions
            if dest.exists() and dest != png:
                stem = dest.stem
                n = 2
                while dest.exists():
                    dest = folder / f"{stem}__{n}.png"
                    n += 1
            if args.dry_run:
                print(f"{png.name} -> {dest.name}")
            else:
                png.rename(dest)
            renamed += 1
            if unnamed_flag:
                unnamed += 1

    # write name index
    index = {
        safe_stem(face) + f"_{nw}x{nh}": {
            f"{i+1:03d}": names[i] for i in sorted(names) if isinstance(i, int)
        }
        for face, names in face_to_names.items()
        for nw, nh in [face_to_grid.get(face, (0, 0))]
    }
    out_index = args.extract_dir / "card_names.json"
    if not args.dry_run:
        # simpler flat map by folder prefix
        flat = {}
        for face, names in face_to_names.items():
            nw, nh = face_to_grid.get(face, (1, 1))
            prefix = f"{safe_stem(face)}_{nw}x{nh}"
            flat[prefix] = {f"{i+1:03d}": names[i] for i in sorted(names)}
        out_index.write_text(json.dumps(flat, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"renamed={renamed} still_unnamed={unnamed}")
    print("index:", out_index)


if __name__ == "__main__":
    main()
