import os
import collections.abc

from typing_extensions import Literal

from PIL import Image

import steam_editor_tools as stet


FONT_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data"
)


def get_bg_img() -> stet.ImageSingle:
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
    return img


def create_effect(
    func: collections.abc.Callable[[stet.improc.ImageLayer], None],
    img: stet.ImageSingle,
    name: str,
    font: stet.improc.FontInfo,
    text_color: Literal["white", "black"] = "white",
) -> stet.ImageSingle:
    """Cast effect to an image."""
    _img = (
        stet.ImageMultiLayer(img, name=name)
        .add_text(
            name,
            "text-{0}".format(name),
            font=font,
            font_size=32,
            color=text_color,
            stroke_color="black" if text_color == "white" else "white",
            related_to=name,
            anchor=stet.ImageAnchor.bottom_center,
            rel_anchor=stet.ImageAnchor.bottom_center,
        )
        .add_background()
    )
    func(_img.layers[name])
    return _img.flatten()


def list_effects(
    out_file_path: "str | os.PathLike[str]",
    bg_color: str | tuple[float, ...] = "#888888",
) -> Image.Image:
    """List all effects, and save the results in an image.

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

    def shadow(layer: stet.improc.ImageLayer) -> None:
        layer.set_shadow()

    def glow(layer: stet.improc.ImageLayer) -> None:
        layer.set_glow(color="#FFFFaa")

    def stroke(layer: stet.improc.ImageLayer) -> None:
        layer.set_stroke(color="cyan")

    def bevel(layer: stet.improc.ImageLayer) -> None:
        layer.set_bevel(max_distance=10)

    def alpha(layer: stet.improc.ImageLayer) -> None:
        layer.effects.alpha_content = 0
        layer.set_bevel(max_distance=8, smooth=6)

    def overlay(layer: stet.improc.ImageLayer) -> None:
        layer.add_overlay_color(color="#ff88cca0", mode="screen")

    def lay_gradient(layer: stet.improc.ImageLayer) -> None:
        layer.add_overlay_gradient(
            color_a="#FF0000",
            color_b="#0000FF",
            direction="rect_center_to_outside",
            size=(120, 120),
            mode="hard_light",
        )

    def lay_image(layer: stet.improc.ImageLayer) -> None:
        _img = Image.new("RGBA", (80, 80), color="#FFAA00")
        layer.add_overlay_image(
            _img, feather_depth=10, pos_shift=(40, 0), size=(80, 80), mode="screen"
        )

    def hybrid(layer: stet.improc.ImageLayer) -> None:
        layer.add_overlay_gradient(
            color_a="#0000E0",
            color_b="#000000",
            direction="top_to_bottom",
            mode="default",
        )
        layer.set_bevel(max_distance=10, smooth=0)
        layer.set_shadow()

    n_cols = 5
    img_bg = get_bg_img()

    res = stet.improc.tools.ImageGrids(
        n_cols,
        width=n_cols * 256,
        margins=(10, 10),
        gaps=(10, 10),
        bg_color=bg_color,
    )

    for op in (
        shadow,
        glow,
        stroke,
        bevel,
        alpha,
        overlay,
        lay_gradient,
        lay_image,
        hybrid,
    ):
        op_name = op.__name__
        res.append(create_effect(op, img_bg, op_name, font=font))

    res_img = res.img.flatten().convert("RGB")

    res_img.save(out_file_path)
    return res_img.img


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    list_effects(os.path.join(root_dir, "example-effects.png"))
