"""Scan and sort PDF files in a selected folder."""

import os
import re

from utils.models import DEFAULT_OUTPUT_FILENAME, PdfScanResult


def natural_sort_key(path: str) -> list[object]:
    """Sort file names so 2.pdf comes before 10.pdf."""
    name = os.path.basename(path).lower()
    parts = re.split(r"(\d+)", name)
    return [int(part) if part.isdigit() else part for part in parts]


def scan_pdf_files(
    folder_path: str,
    output_filename: str = DEFAULT_OUTPUT_FILENAME,
) -> PdfScanResult:
    if not folder_path:
        raise ValueError("Please select a PDF folder first.")
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")

    output_name = output_filename.lower()
    pdf_files: list[str] = []

    for entry in os.scandir(folder_path):
        if not entry.is_file():
            continue
        if not entry.name.lower().endswith(".pdf"):
            continue
        if entry.name.lower() == output_name:
            continue
        if entry.name.lower().endswith(".tmp.pdf"):
            continue
        pdf_files.append(entry.path)

    pdf_files.sort(key=natural_sort_key)
    return PdfScanResult(folder_path=folder_path, pdf_files=pdf_files)
