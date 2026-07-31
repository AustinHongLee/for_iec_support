"""Render three-source Type drawing contact sheets for visual audit.

The renderer consumes docs/type_source_audit.json and writes only temporary PNG
files.  It does not make any sameness decision; a human must inspect each row.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont


APP_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = APP_DIR.parent
DEFAULT_AUDIT = REPO_DIR / "docs" / "type_source_audit.json"
DEFAULT_OUTPUT = REPO_DIR / "tmp" / "pdfs" / "type_source_audit"
SOURCE_IDS = ("cw_e25_24_hp6", "ctci_22a_5123a", "ctci_20e4588")
SOURCE_LABELS = {
    "cw_e25_24_hp6": "Chung Wei E25-24 / HP6",
    "ctci_22a_5123a": "CTCI 22A_5123A",
    "ctci_20e4588": "CTCI 20E4588",
}

SHEET_WIDTH = 2040
LABEL_HEIGHT = 38
TYPE_LABEL_WIDTH = 90
SOURCE_WIDTH = (SHEET_WIDTH - TYPE_LABEL_WIDTH) // 3
ROW_HEIGHT = 720
ROWS_PER_SHEET = 3
MARGIN = 10


def _font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/msjh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


TITLE_FONT = _font(23)
LABEL_FONT = _font(17)
SMALL_FONT = _font(13)


def _render_pdf(path: Path, output_prefix: Path) -> list[Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            "100",
            str(path),
            str(output_prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return sorted(
        output_prefix.parent.glob(output_prefix.name + "-*.png"),
        key=lambda item: item.name.casefold(),
    )


def _tile_pages(
    page_paths: list[Path],
    *,
    width: int,
    height: int,
) -> Image.Image:
    canvas = Image.new("RGB", (width, height), "white")
    if not page_paths:
        return canvas
    columns = 1 if len(page_paths) == 1 else 2
    rows = (len(page_paths) + columns - 1) // columns
    cell_width = width // columns
    cell_height = height // rows
    for index, page_path in enumerate(page_paths):
        with Image.open(page_path) as source:
            page = source.convert("RGB")
        page.thumbnail(
            (cell_width - 2 * MARGIN, cell_height - 2 * MARGIN),
            Image.Resampling.LANCZOS,
        )
        col = index % columns
        row = index // columns
        x = col * cell_width + (cell_width - page.width) // 2
        y = row * cell_height + (cell_height - page.height) // 2
        canvas.paste(page, (x, y))
    return canvas


def _render_type_pages(row: dict, source_id: str, cache_dir: Path) -> list[Path]:
    rendered: list[Path] = []
    for file_index, fact in enumerate(row["files"][source_id], start=1):
        pdf_path = REPO_DIR / fact["path"]
        prefix = cache_dir / (
            f"type_{row['type_id']}_{source_id}_{file_index:02d}"
        )
        rendered.extend(_render_pdf(pdf_path, prefix))
    return rendered


def build_sheets(audit: dict, output_dir: Path) -> list[Path]:
    cache_dir = output_dir / "rendered"
    cache_dir.mkdir(parents=True, exist_ok=True)
    rows = [
        row
        for row in audit["types"]
        if sum(bool(value) for value in row["presence"].values()) >= 2
    ]
    rendered_by_type: dict[tuple[str, str], list[Path]] = {}
    for row in rows:
        for source_id in SOURCE_IDS:
            rendered_by_type[(row["type_id"], source_id)] = _render_type_pages(
                row, source_id, cache_dir
            )

    sheet_paths = []
    for sheet_index, start in enumerate(
        range(0, len(rows), ROWS_PER_SHEET), start=1
    ):
        batch = rows[start : start + ROWS_PER_SHEET]
        sheet_height = LABEL_HEIGHT + ROW_HEIGHT * len(batch)
        sheet = Image.new("RGB", (SHEET_WIDTH, sheet_height), "#E9EDF2")
        draw = ImageDraw.Draw(sheet)
        draw.rectangle((0, 0, SHEET_WIDTH, LABEL_HEIGHT), fill="#24364B")
        draw.text((14, 6), "Type source visual audit", font=TITLE_FONT, fill="white")
        for source_index, source_id in enumerate(SOURCE_IDS):
            x = TYPE_LABEL_WIDTH + source_index * SOURCE_WIDTH
            draw.text(
                (x + 14, 9),
                SOURCE_LABELS[source_id],
                font=LABEL_FONT,
                fill="white",
            )

        for row_index, row in enumerate(batch):
            y = LABEL_HEIGHT + row_index * ROW_HEIGHT
            fill = "white" if row_index % 2 == 0 else "#F7F9FB"
            draw.rectangle((0, y, SHEET_WIDTH, y + ROW_HEIGHT), fill=fill)
            draw.text(
                (15, y + 18),
                f"TYPE\n{row['type_id']}",
                font=TITLE_FONT,
                fill="#16324F",
                spacing=4,
            )
            for source_index, source_id in enumerate(SOURCE_IDS):
                x = TYPE_LABEL_WIDTH + source_index * SOURCE_WIDTH
                draw.line(
                    (x, y, x, y + ROW_HEIGHT),
                    fill="#AAB4C0",
                    width=1,
                )
                page_paths = rendered_by_type[(row["type_id"], source_id)]
                panel = _tile_pages(
                    page_paths,
                    width=SOURCE_WIDTH - 2 * MARGIN,
                    height=ROW_HEIGHT - 45,
                )
                sheet.paste(panel, (x + MARGIN, y + 35))
                filenames = ", ".join(
                    fact["name"] for fact in row["files"][source_id]
                )
                draw.text(
                    (x + 12, y + 8),
                    filenames or "(not supplied)",
                    font=SMALL_FONT,
                    fill="#374151",
                )
            draw.line(
                (0, y + ROW_HEIGHT - 1, SHEET_WIDTH, y + ROW_HEIGHT - 1),
                fill="#7E8B99",
                width=1,
            )

        sheet_path = output_dir / f"contact_{sheet_index:02d}.png"
        sheet.save(sheet_path)
        sheet_paths.append(sheet_path)
    return sheet_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    if args.clean and args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    paths = build_sheets(audit, args.output_dir)
    print(f"Rendered {len(paths)} contact sheets under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
