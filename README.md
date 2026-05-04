# Combine PDF Tool

This project is a small local Python GUI tool for combining all PDF files in a selected folder into one output PDF.

## Functionality

The user selects a folder in the GUI, then clicks `Combine PDFs`. The application scans the selected folder, sorts all PDF files by natural file-name order, combines them, and saves the output as:

```text
combined_pdf.pdf
```

The output file is saved directly inside the selected folder.

## Project Structure

```text
Combine pdf/
├── README.md
├── Combine_pdf_tool/
│   ├── Combine_pdf_tool.exe
│   └── _internal/
└── implementation/
    ├── main.py
    ├── requirements.txt
    ├── build.bat
    ├── ui/
    │   ├── __init__.py
    │   └── main_window.py
    ├── core/
    │   ├── __init__.py
    │   ├── pdf_scanner.py
    │   └── pdf_combiner.py
    └── utils/
        ├── __init__.py
        ├── models.py
        └── logger.py
```

## Run in Development

From the `implementation` folder:

```bash
pip install -r requirements.txt
python main.py
```

## Build

From the `implementation` folder:

```bat
build.bat
```

The packaged application will be generated under:

```text
implementation/dist/Combine_pdf_tool
```

The ready-to-use copy is placed under:

```text
Combine_pdf_tool/Combine_pdf_tool.exe
```

## Notes

- The scanner is non-recursive. It only combines PDFs directly inside the selected folder.
- `combined_pdf.pdf` is excluded from the input list to avoid combining the output file into itself.
- Files are sorted by natural file-name order, so `2.pdf` comes before `10.pdf`.
- If `combined_pdf.pdf` already exists, the GUI asks for confirmation before overwriting it.
