"""Combine all PDFs from a folder into a single output PDF."""

import os
from collections.abc import Callable

from pypdf import PdfReader, PdfWriter

from core.pdf_scanner import scan_pdf_files
from utils.models import DEFAULT_OUTPUT_FILENAME, CombineResult

ProgressCallback = Callable[[str], None]


def combine_pdfs(
    folder_path: str,
    output_filename: str = DEFAULT_OUTPUT_FILENAME,
    overwrite: bool = False,
    on_progress: ProgressCallback | None = None,
) -> CombineResult:
    def progress(message: str) -> None:
        if on_progress:
            on_progress(message)

    scan_result = scan_pdf_files(folder_path, output_filename=output_filename)
    if not scan_result.pdf_files:
        raise ValueError("No PDF files were found in the selected folder.")

    output_path = os.path.join(folder_path, output_filename)
    if os.path.exists(output_path) and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path}")

    temp_path = os.path.join(folder_path, f".{output_filename}.tmp.pdf")
    if os.path.exists(temp_path):
        os.remove(temp_path)

    writer = PdfWriter()
    total_pages = 0

    progress(f"Found {scan_result.count} PDF file(s).")
    progress("Combine order:")
    for index, pdf_path in enumerate(scan_result.pdf_files, start=1):
        progress(f"  {index}. {os.path.basename(pdf_path)}")

    try:
        for index, pdf_path in enumerate(scan_result.pdf_files, start=1):
            file_name = os.path.basename(pdf_path)
            progress(f"Reading {index}/{scan_result.count}: {file_name}")

            try:
                reader = PdfReader(pdf_path)
            except Exception as exc:
                raise RuntimeError(f"Failed to read {file_name}: {exc}") from exc

            if reader.is_encrypted:
                raise RuntimeError(f"Cannot combine encrypted PDF: {file_name}")

            page_count = len(reader.pages)
            for page in reader.pages:
                writer.add_page(page)
            total_pages += page_count
            progress(f"Added {page_count} page(s) from {file_name}.")

        progress(f"Writing output: {output_path}")
        with open(temp_path, "wb") as output_file:
            writer.write(output_file)

        os.replace(temp_path, output_path)
        progress("Combine completed successfully.")
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise

    return CombineResult(
        folder_path=folder_path,
        output_path=output_path,
        input_files=scan_result.pdf_files,
        total_pages=total_pages,
    )
