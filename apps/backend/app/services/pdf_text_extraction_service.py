from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.errors import AppError


class PdfTextExtractionService:
    def extract(self, content: bytes) -> str:
        if not content:
            raise AppError(400, "empty_pdf", "PDF file must not be empty.")

        try:
            reader = PdfReader(BytesIO(content))
        except PdfReadError as exc:
            raise AppError(400, "invalid_pdf", "Uploaded file is not a readable PDF.") from exc

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as exc:
                raise AppError(400, "encrypted_pdf", "Encrypted PDFs are not supported.") from exc

        text_parts = []
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception as exc:
                raise AppError(400, "pdf_text_extraction_failed", f"Failed to extract page {page_number}.") from exc
            if page_text.strip():
                text_parts.append(page_text.strip())

        text = "\n\n".join(text_parts).strip()
        if not text:
            raise AppError(400, "empty_pdf_text", "PDF does not contain extractable text.")
        return text
