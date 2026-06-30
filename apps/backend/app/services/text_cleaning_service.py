from app.utils.text import clean_text


class TextCleaningService:
    def clean(self, text: str) -> str:
        return clean_text(text)

