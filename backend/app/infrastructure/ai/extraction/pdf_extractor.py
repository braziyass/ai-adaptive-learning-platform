from __future__ import annotations

from pathlib import Path


class PDFExtractor:
    def extract(self, pdf_path: str | Path) -> list[dict[str, object]]:
        try:
            import pymupdf
        except ImportError as exc:
            raise RuntimeError("PyMuPDF (fitz) is required for PDF extraction") from exc

        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")

        pages: list[dict[str, object]] = []
        with pymupdf.open(path) as document:
            for index, page in enumerate(document, start=1):
                text = page.get_text("text") or ""
                pages.append({"page_number": index, "text": text})
        return pages