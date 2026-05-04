"""Shared data structures for the PDF combine workflow."""

from dataclasses import dataclass, field


DEFAULT_OUTPUT_FILENAME = "combined_pdf.pdf"


@dataclass
class PdfScanResult:
    folder_path: str
    pdf_files: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.pdf_files)


@dataclass
class CombineResult:
    folder_path: str
    output_path: str
    input_files: list[str] = field(default_factory=list)
    total_pages: int = 0

    @property
    def total_files(self) -> int:
        return len(self.input_files)
