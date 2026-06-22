from copy import deepcopy

from ui.theme import TOKENS, build_stylesheet


def test_build_stylesheet_uses_theme_tokens():
    tokens = deepcopy(TOKENS)
    tokens["color"]["primary"] = "#123456"
    tokens["font"]["table"] = 15

    stylesheet = build_stylesheet(tokens)

    assert "QMainWindow" in stylesheet
    assert "#123456" in stylesheet
    assert "font-size: 15px;" in stylesheet
