# -*- coding: UTF-8 -*-
"""
Examples: Create Logo
=====================
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
Create the logo banner of this project
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PIL import Image

import steam_editor_tools as stet


__all__ = ("create_logo_styled", "create_logo_banner")

FONT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data", "Roboto-Regular.ttf"
)


def create_logo_styled(
    logo_path: "str | os.PathLike[str]",
    color: str,
    stroke_color: str,
    shadow_color: str,
) -> stet.ImageSingle:
    """Create a styled logo.

    Arguments
    ---------
    logo_path: `str | PathLike[str]`
        The path to the source logo file.

    color: `str`
        The HEX color of the logo body.

    stroke_color: `str`
        The HEX color of the logo stroke.

    shadow_color: `str`
        The HEX color of the logo shadow.
    """
    img_logo = (
        stet.ImageMultiLayer(
            stet.ImageSingle(Image.new("L", (300, 300), color=0)),
            "bg",
        )
        .add_image(
            stet.ImageSingle(
                Image.open(logo_path).copy().getchannel("A").resize((160, 160))
            ),
            "logo",
        )
        .flatten()
        .convert("L")
        .img
    )
    img_logo = Image.composite(
        Image.new("RGBA", img_logo.size, color=color),
        Image.new("RGBA", img_logo.size, color=color + "00"),
        img_logo,
    )

    img_logo_styled = stet.ImageMultiLayer(300, 300, "png").add_image(
        stet.ImageSingle(img_logo), "logo"
    )

    img_logo_styled.layers["logo"].set_glow(mode="default", size=16, color=shadow_color)
    img_logo_styled.layers["logo"].set_stroke(
        mode="default", size=2, color=stroke_color
    )

    return img_logo_styled.flatten()


def create_logo_with_text(logo: stet.ImageSingle) -> stet.ImageSingle:
    """Create a logo with text image.

    Arguments
    ---------
    logo: `stet.ImageSingle`
        The logo image (it is a squared image).

    Returns
    -------
    #1: `stet.ImageSingle`
        The logo with text image. The text is placed on the right side of the logo.

        The image size is `(1150, 300)`.
    """
    font_size = 80
    img_text = (
        stet.ImageMultiLayer((1150, 300), fmt="png")
        .add_image(
            logo.resize((300, None)),
            name="logo",
            anchor="left",
            rel_anchor="left",
            pos_shift=(36 - 70, 0),
        )
        .add_text(
            "Steam Editor Tools",
            name="text1",
            font=FONT_PATH,
            font_size=font_size,
            color="#ffffff",
            stroke_color=stet.improc.variables.steam_color_light,
            glow_color=stet.improc.variables.steam_color_dimmed,
            anchor="left",
            related_to="logo",
            rel_anchor="right",
            pos_shift=(-70, 10),
        )
        .add_text(
            "St",
            name="text2",
            font=FONT_PATH,
            font_size=font_size,
            color=stet.improc.variables.steam_color_light,
            stroke_color="#ffffff",
            anchor="left",
            related_to="text1",
            rel_anchor="left",
            pos_shift=(0, 0),
        )
        .add_text(
            "eam E",
            name="text3",
            font=FONT_PATH,
            font_size=font_size,
            color="#00000000",
            anchor="left",
            related_to="text2",
            rel_anchor="right",
            pos_shift=(0, 0),
        )
        .add_text(
            "E",
            name="text4",
            font=FONT_PATH,
            font_size=font_size,
            color=stet.improc.variables.steam_color_light,
            stroke_color="#ffffff",
            anchor="right",
            related_to="text3",
            rel_anchor="right",
            pos_shift=(0, 0),
        )
        .add_text(
            "ditor T",
            name="text5",
            font=FONT_PATH,
            font_size=font_size,
            color="#00000000",
            anchor="left",
            related_to="text3",
            rel_anchor="right",
            pos_shift=(0, 0),
        )
        .add_text(
            "T",
            name="text6",
            font=FONT_PATH,
            font_size=font_size,
            color=stet.improc.variables.steam_color_light,
            stroke_color="#ffffff",
            anchor="right",
            related_to="text5",
            rel_anchor="right",
            pos_shift=(0, 0),
        )
        .flatten()
    )
    return img_text


def create_logo_banner(
    out_file_path: "str | os.PathLike[str]", banner_size: tuple[int, int] = (1200, 300)
) -> None:
    """Create the logo banner of this project.

    Arguments
    ---------
    out_file_path: `str | PathLike[str]`
        The path to the output file.

    banner_size: `tuple[int, int]`
        The size of the logo banner.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_file_path)), exist_ok=True)
    inner_width = banner_size[0] - 150
    inner_height = banner_size[1] - 100

    img_bg = (
        stet.ImageMultiLayer(width=inner_width, height=inner_height, fmt="png")
        .add_image(
            stet.ImageSingle(
                Image.new(
                    "RGB",
                    (inner_width, inner_height),
                    color=stet.improc.variables.steam_color,
                )
            ),
            name="bg",
        )
        .flatten()
    )

    img_logo_styled = create_logo_styled(
        "./logo.png",
        color="#ffffff",
        stroke_color=stet.improc.variables.steam_color_light,
        shadow_color=stet.improc.variables.steam_color_dimmed,
    )

    img_text = create_logo_with_text(img_logo_styled)

    img = stet.ImageMultiLayer(banner_size, fmt="webp_lossless")
    img.add_image(img_bg, name="bg").add_image(img_text, name="text", pos_shift=(96, 0))
    img.layers["bg"].set_shadow(mode="default", size=5, offset=5)
    img.save(out_file_path, quality="high")


def create_logo_github_banner(
    out_file_path: "str | os.PathLike[str]",
    outer_size: tuple[int, int] = (1280, 640),
    inner_size=(1120, 480),
) -> None:
    """Create the GitHub logo banner of this project.

    Arguments
    ---------
    out_file_path: `str | PathLike[str]`
        The path to the output file.

    outer_size: `tuple[int, int]`
        The size of the logo banner.

    inner_size: `tuple[int, int]`
        The actual available size of the logo banner
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_file_path)), exist_ok=True)
    inner_width = inner_size[0] - 32
    inner_height = inner_size[1] - 32

    img_bg = (
        stet.ImageMultiLayer(width=inner_width, height=inner_height, fmt="png")
        .add_image(
            stet.ImageSingle(
                Image.new(
                    "RGB",
                    (inner_width, inner_height),
                    color=stet.improc.variables.steam_color,
                )
            ),
            name="bg",
        )
        .flatten()
    )

    img_logo_styled = create_logo_styled(
        "./logo.png",
        color="#ffffff",
        stroke_color=stet.improc.variables.steam_color_light,
        shadow_color=stet.improc.variables.steam_color_dimmed,
    )

    img_text = create_logo_with_text(img_logo_styled)  # Expected to be (1150, 300)

    img = stet.ImageMultiLayer(outer_size, fmt="png")
    img.add_image(img_bg, name="bg").add_image(
        img_text.resize((int(inner_size[0] * 0.8), None)),
        name="title",
        anchor="top",
        related_to="bg",
        rel_anchor="top",
        pos_shift=(96, 0),
    ).add_text(
        "This package offers editor tools helping users write Steam guides and "
        "reviews.",
        name="text",
        font=FONT_PATH,
        font_size=stet.ImageFontAbsSize(n_per_line=56, font_size=32),
        color="#ffffff",
        stroke_color="#000000",
        anchor="top",
        related_to="title",
        rel_anchor="bottom",
        pos_shift=(-96, -16),
    ).add_text(
        "Support Steam information queries, image editing tools, and BBCode "
        "text processing tools.",
        name="text2",
        font=FONT_PATH,
        font_size=stet.ImageFontAbsSize(n_per_line=56, font_size=32),
        color="#ffffff",
        stroke_color="#000000",
        anchor="top left",
        related_to="text",
        rel_anchor="bottom left",
        pos_shift=(0, 16),
    )
    img.layers["bg"].set_shadow(mode="default", size=5, offset=5)
    img.save(out_file_path, quality="high")


if __name__ == "__main__":
    create_logo_banner(out_file_path="./display/logo-banner.webp")
    create_logo_github_banner(out_file_path="logo-github-banner.png")
