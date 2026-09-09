import re


class TextCleaner:
    TOC_PATTERNS = [
        r"^\s*contents\s*$",
        r"^\s*table\s+of\s+contents\s*$",
        r"^\s*оглавление\s*$",
        r"^\s*содержание\s*$",
    ]
    DOT_LEADER_PATTERN = re.compile(r"\.{4,}")
    DASH_LINE_PATTERN = re.compile(r"^\s*[-—_]{3,}\s*$")
    TOC_ENTRY_PATTERN = re.compile(r"^\d+.*\d+\s*$")

    @classmethod
    def clean(cls, text: str) -> str:
        if not text:
            return ""

        lines = text.splitlines()
        cleaned = []
        in_toc = False

        for line in lines:
            stripped = line.strip()

            # Пустые строки
            if not stripped:
                if cleaned and cleaned[-1] != "":
                    cleaned.append("")
                continue

            # Начало оглавления
            if cls._is_toc_header(stripped):
                in_toc = True
                continue

            # Строки оглавления с точками-заполнителями
            if in_toc:
                if cls.DOT_LEADER_PATTERN.search(stripped):
                    continue
                in_toc = False

            # Пропуск пунктирных линий
            if cls.DASH_LINE_PATTERN.match(stripped):
                continue

            # Удаляем точки-заполнители из ЛЮБОЙ строки
            # "1 Product ....... 5" → "1 Product 5"
            if cls.DOT_LEADER_PATTERN.search(stripped):
                stripped = cls.DOT_LEADER_PATTERN.sub(" ", stripped)

            # Схлопываем пробелы
            collapsed = re.sub(r"\s+", " ", stripped).strip()

            if collapsed:
                cleaned.append(collapsed)

        return "\n".join(cleaned)

    @classmethod
    def _is_toc_header(cls, line: str) -> bool:
        return any(re.search(p, line, re.IGNORECASE) for p in cls.TOC_PATTERNS)