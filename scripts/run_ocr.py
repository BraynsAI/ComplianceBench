"""
Usage:
    python ocr_pdfs.py --input_dir INPUT_DIR --output_dir OUTPUT_DIR [--fmt md|txt] [
    --force-ocr] [--overwrite]
"""

import argparse
import logging
import sys
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

logger = logging.getLogger("ocr_pdfs")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--input_dir",
        type=Path,
        help="Directory containing PDFs (searched recursively)",
    )
    p.add_argument(
        "--output_dir",
        type=Path,
        help="Directory to write results into (same structure)",
    )
    p.add_argument(
        "--fmt", choices=["md", "txt"], default="md", help="Output format (default: md)"
    )
    p.add_argument(
        "--force-ocr",
        action="store_true",
        help="Ignore embedded text layer and OCR every page",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-process files whose output already exists",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args()


def build_converter(force_ocr: bool) -> DocumentConverter:
    opts = PdfPipelineOptions(do_ocr=True)
    opts.ocr_options.force_full_page_ocr = force_ocr
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )


def target_path(pdf: Path, src: Path, dst: Path, fmt: str) -> Path:
    return (dst / pdf.relative_to(src)).with_suffix(f".{fmt}")


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    src: Path = args.input_dir.resolve()
    dst: Path = args.output_dir.resolve()
    if not src.is_dir():
        logger.error(f"input dir does not exist: {src}")
        return 1

    pdfs = sorted(src.rglob("*.pdf"))
    if not args.overwrite:
        pdfs = [p for p in pdfs if not target_path(p, src, dst, args.fmt).exists()]
    if not pdfs:
        logger.info("nothing to do")
        return 0
    logger.info(f"processing {len(pdfs)} PDF(s) -> {dst}")

    converter = build_converter(args.force_ocr)
    ok = failed = 0

    for res in converter.convert_all(pdfs, raises_on_error=False):
        pdf = Path(res.input.file)
        out = target_path(pdf, src, dst, args.fmt)

        if res.status not in (
            ConversionStatus.SUCCESS,
            ConversionStatus.PARTIAL_SUCCESS,
        ):
            logger.error(f"FAILED {pdf.relative_to(src)} ({res.status})")
            failed += 1
            continue

        text = (
            res.document.export_to_markdown()
            if args.fmt == "md"
            else (res.document.export_to_text())
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        logger.info(f"wrote {out.relative_to(dst)}")
        ok += 1

    logger.info(f"done: {ok} ok, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
