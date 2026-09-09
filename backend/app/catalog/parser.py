import os
import logging

from app.catalog.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class DocumentParser:
    MAX_CHARS = 5000
    INITIAL_MAX_CHARS = 20000

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
            content = f.read(DocumentParser.INITIAL_MAX_CHARS)
        cleaned=TextCleaner.clean(content)
        return cleaned[:DocumentParser.MAX_CHARS]


    @staticmethod
    def _read_pdf(path: str) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            full_text=full_text[:DocumentParser.INITIAL_MAX_CHARS]
            cleaned = TextCleaner.clean(full_text)
            return cleaned[:DocumentParser.MAX_CHARS]
        except Exception as e:
            logger.error(f"Ошибка чтения PDF {path}: {e}", exc_info=True)
            return ""