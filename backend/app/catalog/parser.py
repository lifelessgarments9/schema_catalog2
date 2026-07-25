import os
import logging

logger = logging.getLogger(__name__)

class DocumentParser:

    @staticmethod
    def parse(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".txt":
            return DocumentParser._read_txt(file_path)
        if ext == ".pdf":
            return DocumentParser._read_pdf(file_path)
        return ""

    @staticmethod
    def _read_txt(path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def _read_pdf(path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.error(f"Ошибка чтения PDF {path}: {e}", exc_info=True)
            return ""