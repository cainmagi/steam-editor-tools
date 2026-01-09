# -*- coding: UTF-8 -*-
"""
Examples: Create a Title Figure
===============================
@ Steam Editor Tools

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
Search a font by the partial name
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("search_a_font_and_create_figure",)

FONT_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data"
)


def search_a_font_and_create_figure(out_file_path: "str | os.PathLike[str]") -> None:
    """Search a font, and create the figure with the searched font.

    Arguments
    ---------
    out_file_path: `str | PathLike[str]`
        The path to the output file.
    """
    font_locator = stet.FontLocator(FONT_FALLBACK_PATH)
    font = font_locator.query_best_with_fallbacks(["Century School", "Arial", ""])
    if font is None:
        raise ValueError(
            "This situation cannot happen because we have used Roboto as a fallback "
            "option."
        )
    font_name = font.get_name()
    print("Searched font name: {0}".format(font_name))

    img = stet.ImageMultiLayer(width=1200, height=240, fmt="png")
    img.add_text(
        font_name,
        name="title",
        font=font.path,
        font_size=80,
        color="#ffffff",
        stroke_color="black",
    ).add_background().convert("RGB")
    img.save(out_file_path, quality="high")


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    search_a_font_and_create_figure(
        out_file_path=os.path.join(root_dir, "example-font-search.png"),
    )
