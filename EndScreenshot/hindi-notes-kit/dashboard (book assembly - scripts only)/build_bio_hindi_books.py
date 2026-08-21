#!/usr/bin/env python3
"""Build the per-board HINDI Biology books: cover + notes + that board's Hindi PYQs.

    Bordered Notes/Bio Notes + PYQ (Hindi)/<BOARD> Board/Chapter NN - <name>.pdf

The Hindi mirror of build_bio_pyq_books.py, so the Hindi folder lines up 1:1 with
"Bio Notes + PYQ (English)" -- same folder shape, same file names, same frame
templates, same header, same board covers (Hindi variants).

Only MP and RJ are built: those are the two boards the user asked for, and the two
Hindi PYQ sets that pair with chapters 1-7 (Hindi Hand/chapters/UP also exists, for
Ch1-13, if a UP book is ever wanted).

Sources
  notes : GPT-Notes/Hindi Bio Notes/Ch<NN> <name>/generated/page-NN.jpg
          in that chapter's own ORDER.txt sequence. Where the chapter carries a
          fixed/ page, that page WINS -- those are the post-QA corrections. See
          FIXED_REJECTS for the one page where the "fix" is a regression.
  PYQ   : GPT-Notes/Hindi Hand/chapters/<Board>/Ch<N>/*.jpg in that folder's
          ORDER.txt sequence, which already interleaves the dia-NN pages. A plain
          alphabetical sort would put every dia-NN before every page-NN.

FIT MODE forced to "stretch" (as in batch_bio_hindi.py): the Hindi renders are
1024x1536 and the template slot is 1791x2793, so cover-fit would center-crop ~2%
off each side and clip the outer ruling. config.json is left untouched.

Run with the repo venv:
  ./.venv/bin/python dashboard/build_bio_hindi_books.py            # all, both boards
  ./.venv/bin/python dashboard/build_bio_hindi_books.py 3          # just chapter 3
  ./.venv/bin/python dashboard/build_bio_hindi_books.py --board MP
  ./.venv/bin/python dashboard/build_bio_hindi_books.py --dry-run
"""
from __future__ import annotations

import gc
import io
import re
import sys
from pathlib import Path

from PIL import Image

import compositor as C
import front_pages as FP
import html_header as HH

HERE = Path(__file__).parent
TEMPLATES_DIR = HERE / "templates_assets"
FRONT_DIR = HERE / "front_pages"
ROOT = Path("/Users/vedanshsharma/PCMB Notes Final")
NOTES_ROOT = ROOT / "GPT-Notes" / "Hindi Bio Notes"
PYQ_ROOT = ROOT / "GPT-Notes" / "Hindi Hand" / "chapters"
OUT_ROOT = ROOT / "Bordered Notes" / "Bio Notes + PYQ (Hindi)"

# English chapter names -- the header and the output file name both use them, which is
# what keeps this folder name-for-name identical to the English one.
CH_NAMES = {
    1: "Sexual Reproduction in Flowering Plants",
    2: "Human Reproduction",
    3: "Reproductive Health",
    4: "Principles of Inheritance and Variation",
    5: "Molecular Basis of Inheritance",
    6: "Evolution",
    7: "Human Health and Disease",
}

# (cover id in front_pages/, output folder, PYQ board folder under chapters/)
BOARDS = [
    ("MP Board", "MP Board", "MP"),
    ("RJ Board", "RJ Board", "Rajasthan"),
]

# fixed/<page> that is NOT an improvement -> keep generated/. Ch01 page-22 stamps a
# patch over "पुनरावृति" in a smaller, greyer, misaligned font AND still spells it
# wrong ("पुनरावृत्ते", not पुनरावृत्ति); the original matra slip reads better.
FIXED_REJECTS = {(1, "page-22")}

ORDER_RE = re.compile(r"^\s*\d+\.\s*(\S+\.jpg)\s*$", re.I)
NUM_RE = re.compile(r"\d+")


def chapter_dir(num: int) -> Path:
    hits = sorted(NOTES_ROOT.glob(f"Ch{num:02d} *"))
    if not hits:
        raise SystemExit(f"[Ch{num:02d}] no notes folder under {NOTES_ROOT}")
    return hits[0]


def ordered(d: Path, order_file: Path | None = None) -> list[str]:
    """File names in reading order, from ORDER.txt; numeric sort only as a fallback."""
    of = order_file or (d / "ORDER.txt")
    if of.exists():
        names = [m.group(1) for ln in of.read_text(encoding="utf-8").splitlines()
                 if (m := ORDER_RE.match(ln))]
        if names:
            return names
    return sorted((p.name for p in d.glob("*.jpg")),
                  key=lambda n: [int(x) for x in NUM_RE.findall(n)])


def notes_pages(num: int) -> list[tuple[Path, bool]]:
    """(image path, came_from_fixed) for each notes page, in reading order."""
    ch = chapter_dir(num)
    gen, fixed = ch / "generated", ch / "fixed"
    out = []
    for name in ordered(gen, ch / "ORDER.txt"):
        fp = fixed / name
        stem = Path(name).stem
        if fp.exists() and (num, stem) not in FIXED_REJECTS:
            out.append((fp, True))
        else:
            gp = gen / name
            if not gp.exists():
                raise SystemExit(f"[Ch{num:02d}] ORDER.txt lists a missing page: {name}")
            out.append((gp, False))
    return out


def pyq_pages(board_dir: str, num: int) -> list[Path]:
    d = PYQ_ROOT / board_dir / f"Ch{num}"
    if not d.is_dir():
        return []
    pages = [d / n for n in ordered(d)]
    missing = [p.name for p in pages if not p.exists()]
    if missing:
        raise SystemExit(f"[Ch{num:02d} {board_dir}] ORDER.txt lists missing pages: {missing}")
    return pages


def safe_name(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|]+', "", s)
    return re.sub(r"\s+", " ", s).strip()


def save_pdf(pages: list[Image.Image], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    pages[0].save(buf, "PDF", save_all=True, append_images=pages[1:], resolution=150)
    out_path.write_bytes(buf.getvalue())


def main() -> int:
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    if dry:
        argv.remove("--dry-run")
    board_filter = None
    if "--board" in argv:
        i = argv.index("--board")
        board_filter = argv[i + 1].upper()
        del argv[i:i + 2]
    wanted = sorted({int(a) for a in argv}) if argv else sorted(CH_NAMES)

    boards = [b for b in BOARDS if board_filter is None or b[2].upper() == board_filter
              or b[1].split()[0].upper() == board_filter]
    if not boards:
        print(f"ERROR: no board matching {board_filter}", file=sys.stderr)
        return 1

    cfg = C.load_config()
    cfg["fit_mode"] = "stretch"          # this job only; config.json stays as it is
    templates = [p for p in C.list_templates(TEMPLATES_DIR) if not p.name.startswith("_")]
    if not templates:
        print("ERROR: no templates", file=sys.stderr)
        return 1
    bg = tuple(cfg.get("background_color", [255, 255, 255, 255]))
    tsize = cfg["template_size"]

    covers = {}
    for cover_id, out_folder, _ in boards:
        fp = FP.find(FRONT_DIR, cover_id, "Hindi")
        if fp is None:
            print(f"ERROR: no Hindi cover for {cover_id}", file=sys.stderr)
            return 1
        print(f"  cover {cover_id}: {fp.name}")
        if not dry:
            covers[out_folder] = FP.load_cover(fp, tsize, bg).convert("RGB")

    rows, from_fixed = [], []
    for num in wanted:
        name = CH_NAMES[num]
        notes = notes_pages(num)
        from_fixed += [f"Ch{num:02d} {p.stem}" for p, f in notes if f]

        if dry:
            for _, out_folder, board_dir in boards:
                pq = pyq_pages(board_dir, num)
                rows.append((out_folder, num, len(notes), len(pq), 1 + len(notes) + len(pq)))
                print(f"  [dry] {out_folder}/Chapter {num:02d}  "
                      f"1 + {len(notes)} + {len(pq)} = {1 + len(notes) + len(pq)} pp")
            continue

        header = HH.render_header(f"{num:02d}", name, cfg)
        # the notes block is identical for both boards, so compose it once
        composed_notes = []
        for pi, (fp, _) in enumerate(notes):
            with Image.open(fp) as im:
                tpl = C.load_template(templates[pi % len(templates)])
                composed_notes.append(
                    C.compose(tpl, im.convert("RGBA"), cfg, header_overlay=header).convert("RGB"))

        for _, out_folder, board_dir in boards:
            pq = pyq_pages(board_dir, num)
            # keep the frame cycle running across the notes -> PYQ seam
            pyq_composed = []
            for pi, fp in enumerate(pq, start=len(notes)):
                with Image.open(fp) as im:
                    tpl = C.load_template(templates[pi % len(templates)])
                    pyq_composed.append(
                        C.compose(tpl, im.convert("RGBA"), cfg, header_overlay=header).convert("RGB"))

            pdf = [covers[out_folder]] + composed_notes + pyq_composed
            fname = safe_name(f"Chapter {num:02d} - {name}") + ".pdf"
            save_pdf(pdf, OUT_ROOT / out_folder / fname)
            rows.append((out_folder, num, len(notes), len(pq), len(pdf)))
            print(f"  -> {out_folder}/{fname}  "
                  f"(1 cover + {len(notes)} notes + {len(pq)} PYQ = {len(pdf)} pp)", flush=True)
            for im in pyq_composed:
                im.close()
            del pyq_composed
            gc.collect()

        for im in composed_notes:
            im.close()
        del composed_notes
        gc.collect()

    print("\n[SUMMARY]")
    for _, out_folder, _ in boards:
        r = [x for x in rows if x[0] == out_folder]
        if r:
            print(f"  {out_folder}: {len(r)} chapters, {sum(x[2] for x in r)} notes pages, "
                  f"{sum(x[3] for x in r)} PYQ pages, {sum(x[4] for x in r)} pages total")
    seen = sorted(set(from_fixed))
    print(f"  notes pages taken from fixed/: {seen if seen else 'none'}")
    print(f"  fixed/ pages rejected: "
          f"{sorted(f'Ch{c:02d} {p}' for c, p in FIXED_REJECTS) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
