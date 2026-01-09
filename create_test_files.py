# -*- coding: UTF-8 -*-
"""
Create Test files
=================
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
Create the reference test files.

This script shold be run by the developer. The generated files need to be verified
manually.
"""

import os
import shutil

from typing_extensions import Literal

import steam_editor_tools as stet


def create_test_bbcode(file_path: "str | os.PathLike[str]"):
    """Create the testing files for BBCode validation."""
    file_path = os.path.splitext(file_path)[0].strip()
    doc = stet.DocumentParser().parse_file(file_path + ".md")
    with open(file_path + ".json", "w", encoding="utf-8") as fobj:
        fobj.write(doc.model_dump_json(indent=2))
    with open(file_path + ".bbcode", "w", encoding="utf-8") as fobj:
        fobj.write(stet.BBCodeRenderer().render(doc))


def create_test_images(
    file_path: "str | os.PathLike[str]",
    out_folder: "str | os.PathLike[str]" = "./tests/data",
) -> None:
    """Create test reference images from the given input.

    Prepare the reference images for
    1. Crop an image.
    2. Expand an image.
    3. Resize an image.
    4. Save an image (as png, webp and jpeg).
    5. Save a low-quality image (only test png).
    6. Place an image on 8 positions of an image.
    7. Place an image near another image.
    8. Place text one-by-one.
    9. Place image and text.
    10. Place image, text, and equation (when latex is available).
    """
    img = stet.ImageSingle(file_path, fmt=stet.ImageFormat.webp_lossless)

    img.crop((320, None), anchor="bottom").resize((40, None)).save(
        os.path.join(out_folder, "ref-crop.webp")
    )
    img.crop((1280, 720), anchor="center").resize((160, None)).save(
        os.path.join(out_folder, "ref-expand.webp")
    )
    img.resize((320, None)).resize((40, None)).save(
        os.path.join(out_folder, "ref-resize.webp")
    )

    for pos in stet.ImageAnchor:
        stet.ImageMultiLayer((640, 360), fmt=stet.ImageFormat.webp_lossless).add_image(
            img, name="layer", anchor=pos
        ).flatten().resize((40, None)).save(
            os.path.join(out_folder, "ref-{0}.webp".format(pos.name))
        )

    stet.ImageMultiLayer((640, 360), fmt=stet.ImageFormat.webp_lossless).add_image(
        img, name="layer1", anchor=stet.ImageAnchor.right
    ).add_image(
        img,
        name="layer2",
        anchor=stet.ImageAnchor.left,
        related_to="layer1",
        rel_anchor=stet.ImageAnchor.right,
    ).flatten().resize(
        (40, None)
    ).save(
        os.path.join(out_folder, "ref-near.webp")
    )

    color = "#ffffff"
    stroke = "#000000"
    shadow = "#000000"
    font = os.path.join(out_folder, "Roboto-Regular.ttf")
    stet.ImageMultiLayer((640, 640), fmt=stet.ImageFormat.webp_lossless).add_text(
        "Title",
        name="text1",
        font=font,
        font_size="h1",
        color=color,
        stroke_color=stroke,
        shadow_color=shadow,
        anchor="top",
        rel_anchor="top",
    ).add_text(
        "line 1: lorem ipsum",
        name="text2",
        font=font,
        font_size="h3",
        color="#ff8888",
        stroke_color=stroke,
        shadow_color=shadow,
        anchor="top",
        related_to="text1",
        rel_anchor="bottom",
        pos_shift=(0, -64),
    ).add_text(
        "line 2: test line",
        name="text3",
        font=font,
        font_size="h3",
        color="#aaaaff",
        stroke_color=stroke,
        shadow_color=shadow,
        anchor="top",
        related_to="text2",
        rel_anchor="bottom",
        pos_shift=(0, -48),
    ).add_background().flatten().resize(
        (160, None)
    ).save(
        os.path.join(out_folder, "ref-text.webp")
    )

    stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless).add_image(
        img, name="layer1"
    ).add_text(
        "Test Text",
        name="text1",
        font=font,
        font_size="h1",
        color=color,
        stroke_color=stroke,
        shadow_color=shadow,
        related_to="layer1",
    ).add_background().flatten().resize(
        (160, None)
    ).save(
        os.path.join(out_folder, "ref-img_and_text.webp")
    )

    if shutil.which("latex") is not None:
        stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless).add_image(
            img, name="layer1"
        ).add_text(
            "Test Text",
            name="text1",
            font=font,
            font_size="h1",
            color=color,
            stroke_color=stroke,
            glow_color=shadow,
            related_to="layer1",
            pos_shift=(0, -96),
        ).add_latex(
            R"\nabla \times \mathbf{E} = -\mu \frac{\partial \mathbf{H}}{\partial t}",
            name="text2",
            font_size="h1",
            color=color,
            stroke_color=stroke,
            glow_color=shadow,
            related_to="text1",
            anchor="top",
            rel_anchor="bottom",
            pos_shift=(0, -64),
        ).add_background().flatten().resize(
            (160, None)
        ).save(
            os.path.join(out_folder, "ref-complicated.webp")
        )


def get_test_info_image(
    name: str = "Hollow Knight", lang: Literal["english", "schinese"] = "english"
) -> None:
    """Get the capsule-level header image of a game.

    Arguments
    ---------
    name: `str`
        The name used for searching the game.

    lang: `"english" | "schinese"`
        The language used for searching the game.
    """
    region = "CN" if lang == "schinese" else "US"
    app = stet.query_app_by_name_simple(name, lang=lang, cc=region)[0]
    info = stet.get_app_details(app, lang=lang, cc=region)
    if info is None:
        raise ValueError("Unable to get the information of: {0}".format(app.name))
    img = info.get_header_image(level="capsule")
    if img is None:
        raise ValueError("No figure: {0}".format(app.name))
    stet.ImageSingle(img, fmt="webp_lossless").save("test.webp")


if __name__ == "__main__":
    create_test_bbcode("./tests/data/example.md")
    create_test_images("./tests/data/example.png")
    # get_test_info_image("东方幕华祭 永夜篇", "schinese")
