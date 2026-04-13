"""
Convert all PDFs and EPUBs in a Papers/ directory to txt.

Each page is preceded by: === [Page X] === where X is the printed page number.
If no printed number is found, falls back to ~N (physical page, approximate).
For image-only PDF pages, OCR is applied automatically via Tesseract.

USAGE
  Convert all new files (skip already-converted):
    python3 convert.py --root Papers/

  Check for missing conversions only (no conversion):
    python3 convert.py --root Papers/ --check

  Force re-conversion of a specific file:
    python3 convert.py --root Papers/ --force "somefile.pdf"

  Convert a single file explicitly:
    python3 convert.py --root Papers/ --file "subdir/somefile.pdf"

DEPENDENCIES
  pip install pymupdf ebooklib beautifulsoup4
  For OCR: brew install tesseract  +  pip install pytesseract pdf2image
"""

import os
import re
import sys
import argparse
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_printed_page(page_fitz):
    """Return printed page number string if found in a fitz page, else None."""
    text = page_fitz.get_text("text")
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for c in lines[:3] + lines[-3:]:
        if re.fullmatch(r'\d+', c):
            return c
    return None


def is_image_only(page_fitz, min_chars=20):
    """Return True if the page has no meaningful text (image-only scan)."""
    text = page_fitz.get_text("text").strip()
    return len(text) < min_chars


def ocr_page(pil_image):
    """Run Tesseract OCR on a PIL image and return text."""
    try:
        import pytesseract
        return pytesseract.image_to_string(pil_image)
    except ImportError:
        return "[OCR unavailable — install pytesseract and tesseract]"


def pdf_page_to_image(pdf_path, page_index, dpi=300):
    """Convert a single PDF page to a PIL image via pdf2image."""
    try:
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, dpi=dpi,
                                   first_page=page_index + 1,
                                   last_page=page_index + 1)
        return images[0] if images else None
    except ImportError:
        return None


# ── PDF conversion ────────────────────────────────────────────────────────────

def pdf_to_txt(pdf_path: Path, out_path: Path):
    try:
        import fitz
    except ImportError:
        print("ERROR: pymupdf not installed. Run: pip install pymupdf")
        sys.exit(1)

    doc = fitz.open(str(pdf_path))
    output = [f"SOURCE: {pdf_path.name}\n"]
    ocr_pages = 0

    for i, page in enumerate(doc):
        printed = extract_printed_page(page)
        label = printed if printed else f"~{i+1}"
        text = page.get_text("text")

        # Auto-OCR for image-only pages
        if is_image_only(page):
            img = pdf_page_to_image(str(pdf_path), i)
            if img is not None:
                text = ocr_page(img)
                ocr_pages += 1
            else:
                text = "[Image-only page — install pdf2image and pytesseract for OCR]"

        output.append(f"\n\n=== [Page {label}] ===\n\n{text}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(output), encoding="utf-8")

    msg = f"Done: {pdf_path.name} ({len(doc)} pages"
    if ocr_pages:
        msg += f", {ocr_pages} OCR'd"
    print(msg + ")")


# ── EPUB conversion ───────────────────────────────────────────────────────────

def epub_to_txt(epub_path: Path, out_path: Path):
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        print("ERROR: ebooklib/beautifulsoup4 not installed. Run: pip install ebooklib beautifulsoup4")
        sys.exit(1)

    book = epub.read_epub(str(epub_path))
    output = [f"SOURCE: {epub_path.name}\n"]
    chapter_num = 0

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapter_num += 1
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text(separator="\n")
            # Use chapter as the "page" marker
            output.append(f"\n\n=== [Chapter {chapter_num}] ===\n\n{text}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(output), encoding="utf-8")
    print(f"Done: {epub_path.name} ({chapter_num} chapters)")


# ── Core logic ────────────────────────────────────────────────────────────────

SUPPORTED = {".pdf": pdf_to_txt, ".epub": epub_to_txt}


def txt_path_for(source: Path, root: Path) -> Path:
    """Mirror source path into root/txt/, with .txt extension."""
    rel = source.relative_to(root)
    return root / "txt" / rel.with_suffix(".txt")


def needs_conversion(source: Path, root: Path, force_name: str = None) -> bool:
    if force_name and source.name == force_name:
        return True
    return not txt_path_for(source, root).exists()


def collect_sources(root: Path) -> list:
    sources = []
    txt_dir = root / "txt"
    for dirpath, _, files in os.walk(root):
        if Path(dirpath).is_relative_to(txt_dir):
            continue
        for fname in files:
            suffix = Path(fname).suffix.lower()
            if suffix in SUPPORTED:
                sources.append(Path(dirpath) / fname)
    return sources


def convert_one(source: Path, root: Path):
    out = txt_path_for(source, root)
    suffix = source.suffix.lower()
    SUPPORTED[suffix](source, out)


def check_missing(root: Path):
    sources = collect_sources(root)
    missing = [s for s in sources if not txt_path_for(s, root).exists()]
    if missing:
        for m in missing:
            print(f"Missing: {m}")
    else:
        print("All files converted.")
    return missing


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Convert PDFs/EPUBs to txt")
    parser.add_argument("--root", required=True,
                        help="Papers root directory (e.g. Papers/)")
    parser.add_argument("--check", action="store_true",
                        help="Check for missing conversions only; do not convert")
    parser.add_argument("--force", metavar="FILENAME",
                        help="Re-convert this specific filename even if txt exists")
    parser.add_argument("--file", metavar="RELPATH",
                        help="Convert a single file (relative to --root)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory")
        sys.exit(1)

    if args.check:
        check_missing(root)
        return

    if args.file:
        source = root / args.file
        if not source.exists():
            print(f"ERROR: {source} not found")
            sys.exit(1)
        convert_one(source, root)
        return

    sources = collect_sources(root)
    to_convert = [s for s in sources if needs_conversion(s, root, args.force)]

    if not to_convert:
        print("Nothing to convert.")
        return

    for source in to_convert:
        try:
            convert_one(source, root)
        except Exception as e:
            print(f"ERROR {source.name}: {e}")

    print("All done.")


if __name__ == "__main__":
    main()
