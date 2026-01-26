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
Render a figure as a title.
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PIL import Image

import steam_editor_tools as stet


__all__ = ("create_a_title_figure",)

FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data", "Roboto-Regular.ttf"
)


def create_a_title_figure(text: str, out_file_path: "str | os.PathLike[str]") -> None:
    """Create a simple title figure.

    Arguments
    ---------
    text: `str`
        The text of the title.

    out_file_path: `str | PathLike[str]`
        The path to the output file.
    """
    img = stet.ImageMultiLayer(width=1200, height=240, fmt="png")
    img.add_image(
        stet.ImageSingle(
            Image.new(
                "RGB", (900, 200), color=stet.improc.variables.steam_color_secondary
            )
        ),
        name="bg",
    ).add_text(
        text,
        name="title",
        font=FONT_PATH,
        font_size="h1",
        color="#ffffff",
        stroke_color=stet.improc.variables.steam_color_light,
        glow_color=stet.improc.variables.steam_color_dimmed,
        pos_shift=(0, 10),
    ).add_background().convert(
        "RGB"
    )
    img.layers["bg"].set_shadow()
    img.layers["title"].set_bevel()
    img.layers["title"].effects.alpha_content = 0
    img.save(out_file_path, quality="high")


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    create_a_title_figure(
        text="1. Introduction",
        out_file_path=os.path.join(root_dir, "example-title.png"),
    )
