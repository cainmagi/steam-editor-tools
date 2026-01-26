import os
import math
from PIL import Image, ImageChops

import steam_editor_tools as stet


FONT_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data"
)


def get_test_img(font: stet.improc.FontInfo) -> Image.Image:
    """Create the overlaying testing image.

    This is a radial gradient with a "S" character at the center.
    """
    img = stet.ImageSingle(
        Image.radial_gradient("L").point(
            lambda v: 255 - v * (math.sqrt(255 / 128)), mode="L"
        )
    )
    img = (
        stet.ImageMultiLayer((256, 256), "png")
        .add_background("white")
        .add_image(img, "bg")
        .add_text(
            "s", "text", font=font, font_size=196, pos_shift=(0, 16), color="black"
        )
        .convert("RGB")
    )
    return img.flatten().img


def get_bg_img() -> Image.Image:
    """Create the background testing image.

    This image contains blocks in three different colors.
    """
    img = (
        stet.ImageMultiLayer((256, 256), "png")
        .add_image(
            stet.ImageSingle(Image.new("RGB", (60, 60), color="red")),
            "red",
            pos_shift=(0, int(-15 * 2)),
        )
        .add_image(
            stet.ImageSingle(Image.new("RGB", (60, 60), color="green")),
            "green",
            pos_shift=(int(-15 * 1.732), 15),
        )
        .add_image(
            stet.ImageSingle(Image.new("RGB", (60, 60), color="blue")),
            "blue",
            pos_shift=(int(15 * 1.732), 15),
        )
    )
    img = img.flatten()
    img = img.blur(10, 5)
    return img.img


def list_composer_operators(
    out_file_path: "str | os.PathLike[str]",
    bg_color: str | tuple[float, ...] = "#888888",
) -> Image.Image:
    """List all composer operators, and save the results in an image.

    Arguments
    ---------
    out_file_path: `str | PathLike[str]`
        The path to the output file.

    bg_color: `tuple[int, int]`
        The background color. This value can be an RGBA color.
    """
    font = stet.FontLocator(FONT_FOLDER_PATH, False).query_best("Roboto")
    if font is None:
        raise FileNotFoundError("Font Roboto is not found.")

    comp = stet.improc.composer.ImageComposer()
    ops = (
        comp.alpha_composite,
        comp.add,
        comp.add_modulo,
        comp.darker,
        comp.difference,
        comp.lighter,
        comp.logical_and,
        comp.logical_or,
        comp.logical_xor,
        comp.multiply,
        comp.soft_light,
        comp.hard_light,
        comp.overlay,
        comp.screen,
        comp.subtract,
        comp.subtract_modulo,
    )

    def threshold(image: Image.Image) -> Image.Image:
        return comp.threshold(image, 48)

    s_ops = (comp.invert, comp.invert_luminance, threshold)
    n_cols = 5
    img_bg = get_bg_img()
    img_fg = get_test_img(font)
    img_fg = Image.composite(
        Image.new("RGBA", img_fg.size, "#ffffff"),
        Image.new("RGBA", img_fg.size, "#ffffff00"),
        img_fg.convert("L"),
    )
    img_fg2 = ImageChops.invert(img_fg.convert("RGB")).convert("RGBA")
    img_fg2.putalpha(img_fg.getchannel("A"))

    def _get_imop_res(
        img_bg: Image.Image, img_fg: Image.Image, text_color: str = "white"
    ) -> stet.ImageSingle:
        n_ops = len(ops)

        n_rows = n_ops // 5 + (1 if n_ops % 5 > 0 else 0)
        res = stet.improc.tools.ImageGrids(
            n_rows,
            n_cols,
            width=n_cols * 256,
            height=n_rows * 256,
            margins=(10, 10),
            gaps=(10, 10),
            bg_color=bg_color,
        )

        for idx, op in enumerate(ops):
            op_name = op.__name__
            res_cur = op(img_bg, img_fg)
            res.append(
                stet.ImageMultiLayer(256, 256)
                .add_image(
                    stet.ImageSingle(res_cur, "png"),
                    "layer-{0}".format(idx),
                )
                .add_text(
                    op_name,
                    "test-{0}".format(idx),
                    font=font,
                    font_size=32,
                    color=text_color,
                    stroke_color="black" if text_color == "white" else "white",
                    related_to="layer-{0}".format(idx),
                    anchor=stet.ImageAnchor.bottom_center,
                    rel_anchor=stet.ImageAnchor.bottom_center,
                )
                .flatten()
            )
        return res.img.flatten().convert("RGB")

    def _get_imop_single_res(
        img_bg: Image.Image, text_color: str = "white"
    ) -> stet.ImageSingle:
        n_ops = len(s_ops)

        n_rows = n_ops // 5 + (1 if n_ops % 5 > 0 else 0)
        res = stet.improc.tools.ImageGrids(
            n_rows,
            n_cols,
            width=n_cols * 256,
            height=n_rows * 256,
            margins=(10, 10),
            gaps=(10, 10),
            bg_color=bg_color,
        )

        for idx, op in enumerate(s_ops):
            op_name = op.__name__
            res_cur = op(img_bg)
            res.append(
                stet.ImageMultiLayer(256, 256)
                .add_image(
                    stet.ImageSingle(res_cur, "png"),
                    "layer-{0}".format(idx),
                )
                .add_text(
                    op_name,
                    "test-{0}".format(idx),
                    font=font,
                    font_size=32,
                    color=text_color,
                    stroke_color="black" if text_color == "white" else "white",
                    related_to="layer-{0}".format(idx),
                    anchor=stet.ImageAnchor.bottom_center,
                    rel_anchor=stet.ImageAnchor.bottom_center,
                )
                .flatten()
            )
        return res.img.flatten().convert("RGB")

    imgs = [
        _get_imop_res(img_bg, img_fg, "white"),
        _get_imop_res(img_bg, img_fg2, "black"),
        _get_imop_single_res(img_bg, "white"),
    ]
    height = sum(img.height for img in imgs) + 10 * max(0, len(imgs) - 1)
    width = max(img.width for img in imgs)

    res = stet.ImageMultiLayer((width, height), "png").add_background(bg_color)
    prev_name: str | None = None
    for idx, img in enumerate(imgs):
        cur_name = "mode{0}".format(idx)
        res.add_image(
            img,
            cur_name,
            anchor="top",
            rel_anchor="top" if prev_name is None else "bottom",
            related_to=prev_name,
            pos_shift=(0, 10 if prev_name is not None else 0),
        )
        prev_name = cur_name

    res.save(out_file_path)
    return res.flatten().img


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    list_composer_operators(os.path.join(root_dir, "example-composers.png"))
