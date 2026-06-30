import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if not re.fullmatch(r"\d+", line)]
    return "\n".join(lines).strip()


def contains_any(text: str | None, needles: list[str]) -> bool:
    haystack = text or ""
    return any(needle in haystack for needle in needles)


def token_count(text: str) -> int:
    return len(text.split())

