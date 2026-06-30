from app.utils.text import clean_text


def test_clean_text_collapses_spaces_and_blank_lines():
    assert clean_text("hello   world\n\n\nnext") == "hello world\n\nnext"


def test_clean_text_handles_empty_text():
    assert clean_text("") == ""


def test_clean_text_preserves_korean_sentences():
    text = "저는 FastAPI 프로젝트를 진행했습니다.\n성과를 개선했습니다."
    assert clean_text(text) == text

