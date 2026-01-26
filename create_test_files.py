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
import json

from PIL import Image

from typing_extensions import Literal

import steam_editor_tools as stet


def create_test_bbcode(
    file_path: "str | os.PathLike[str]",
    configs: stet.BBCodeConfig | None = None,
    out_file_name: str | None = None,
    dump_json: bool = True,
) -> None:
    """Create the testing files for BBCode validation."""
    file_path = os.path.splitext(file_path)[0].strip()
    doc = stet.DocumentParser().parse_file(file_path + ".md")
    if out_file_name is not None:
        out_file_path = os.path.join(os.path.dirname(file_path).strip(), out_file_name)
    else:
        out_file_path = file_path
    if dump_json:
        with open(out_file_path + ".json", "w", encoding="utf-8") as fobj:
            fobj.write(doc.model_dump_json(indent=2))
    with open(out_file_path + ".bbcode", "w", encoding="utf-8") as fobj:
        fobj.write(stet.BBCodeRenderer(configs).render(doc))


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
        anchor="bottom",
        rel_anchor="center",
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
        pos_shift=(0, 0),
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
        pos_shift=(0, 0),
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

    # Test LaTeX
    if shutil.which("latex") is not None:

        def set_glow_mode(
            img: stet.ImageMultiLayer, name: str, mode: stet.ImageComposerMode
        ) -> None:
            glow = img.layers[name].effects.glow
            if glow is None:
                return
            glow.mode = mode

        _img = (
            stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless)
            .add_image(img, name="layer1")
            .add_text(
                "Test Text",
                name="text1",
                font=font,
                font_size="h1",
                color=color,
                stroke_color=stroke,
                glow_color=shadow,
                related_to="layer1",
                pos_shift=(0, -96),
            )
            .add_latex(
                R"\nabla \times \mathbf{E} = -\mu \frac{\partial \mathbf{H}}{\partial t}",
                name="text2",
                font_size="h1",
                color=color,
                stroke_color=stroke,
                glow_color=shadow,
                related_to="text1",
                anchor="top",
                rel_anchor="bottom",
                pos_shift=(0, 0),
            )
        )
        set_glow_mode(_img, "text1", "multiply")
        set_glow_mode(_img, "text2", "multiply")
        _img.add_background().flatten().resize((160, None)).save(
            os.path.join(out_folder, "ref-complicated.webp")
        )

    # Test effects
    _img = (
        stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless)
        .add_image(img, name="layer1")
        .add_image(
            stet.ImageSingle(Image.new("RGBA", (500, 200), color="red")),
            name="block",
            related_to="layer1",
        )
        .add_background()
    )
    _img.layers["block"].effects.alpha_content = 0
    _img.layers["block"].add_overlay_color("#ffff0044", mode="screen")
    _img.layers["block"].set_bevel(max_distance=20)
    _img.layers["block"].set_shadow(size=10, offset=16)
    _img.flatten().resize((160, None)).save(
        os.path.join(out_folder, "ref-effects.webp")
    )


def create_composer_test_files(
    out_folder: "str | os.PathLike[str]" = "./tests/data",
) -> None:
    """Create test reference file from the image composer.

    Arguments
    ---------
    out_folder: `str | PathLike[str]`
        The path to the folder where the file is saved.
    """
    img = stet.ImageMultiLayer((64, 64)).add_background(color="#307040")
    img.add_image(
        stet.ImageSingle(Image.new("RGB", (32, 32), color="#112233")), "block"
    )
    _img = img.flatten().img
    _img_p = _img.load()
    if _img_p is None:
        raise ValueError("Unable to get the image pixels.")
    base_val = _img_p[0, 0]
    if isinstance(base_val, (int, float)):
        base_val = float(base_val)
        base_val = (base_val, base_val, base_val, 255.0)
    else:
        base_val = tuple(float(_val) for _val in base_val)

    modes: tuple[stet.ImageComposerMode, ...] = (
        "default",
        "add",
        "add_modulo",
        "screen",
        "lighter",
        "subtract",
        "subtract_modulo",
        "multiply",
        "darker",
        "difference",
        "soft_light",
        "hard_light",
    )

    data: dict[str, tuple[float, ...]] = {"base": base_val}

    for mode in modes:
        img.layers["block"].effects.blend = mode
        _img = img.flatten().img
        _img_p = _img.load()
        if _img_p is None:
            raise ValueError("Unable to get the image pixels.")
        val = _img_p[32, 32]
        if isinstance(val, (int, float)):
            val = float(val)
            val = (val, val, val, 255.0)
        else:
            val = tuple(float(_val) for _val in val)
        data[mode] = val

    with open(os.path.join(out_folder, "composer.json"), "w", encoding="utf-8") as fobj:
        json.dump(data, fobj, ensure_ascii=False)


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
    create_test_bbcode("./tests/data/extensive.md", dump_json=False)
    create_test_bbcode(
        "./tests/data/extensive.md",
        configs=stet.BBCodeConfig(
            quote="QUOTE",
            table="TABLE",
            table_head="td",
            alert=stet.AlertTitleConfigs(note="i", warning="strike", caution="h3"),
        ),
        out_file_name="extensive-custom",
        dump_json=False,
    )
    create_test_images("./tests/data/example.png")
    create_composer_test_files()
    # get_test_info_image("东方幕华祭 永夜篇", "schinese")
