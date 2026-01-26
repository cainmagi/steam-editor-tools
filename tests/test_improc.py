# -*- coding: UTF-8 -*-
"""
Image Processing
================
@ Steam Editor Tools - Tests

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The tests for image processing.
"""

import os
import json
import logging

from typing_extensions import ClassVar

import numpy as np
from skimage.metrics import structural_similarity
from PIL import Image

import pytest

import steam_editor_tools as stet


class TestImageProcessing:
    """The the image processing.

    Will test:
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

    The resource "example.png" is in the public domain, see
    https://commons.wikimedia.org/wiki/File:Test_card.png

    The test font "Roboto-Regular.ttf" is acquired from
    https://github.com/googlefonts/roboto-3-classic
    """

    root_path: ClassVar[str] = os.path.dirname(str(__file__))

    @classmethod
    def get_data_path(cls, file_name: str) -> str:
        """Return the path to a data file."""
        return os.path.join(cls.root_path, "data", file_name)

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get the size of a file."""
        with open(file_path, "rb") as fobj:
            fobj.seek(0, os.SEEK_END)
            size = fobj.tell()
        return size

    @staticmethod
    def ssim(img_1: stet.ImageSingle, img_2: stet.ImageSingle) -> float:
        """Calculate SSIM between two images."""
        if img_1.width > 20:
            img_1 = img_1.resize((20, None))
        if img_1.size != img_2.size:
            img_2 = img_2.resize(img_1.size)
        _img_1 = np.asarray(img_1.add_background().convert("RGB").img, dtype=np.uint8)
        _img_2 = np.asarray(img_2.add_background().convert("RGB").img, dtype=np.uint8)
        _value: list[float] = []
        for c in range(_img_1.shape[-1]):
            _val = structural_similarity(_img_1[..., c], _img_2[..., c])
            assert isinstance(_val, float)
            _value.append(_val)
        return float(np.mean(_value))

    def test_improc_crop(self) -> None:
        """Test

        Crop an image into a smaller one.
        """
        log = logging.getLogger("steam_editor_tools.test")
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-crop.webp")),
            stet.ImageSingle(self.get_data_path("example.png")).crop(
                (320, None), anchor="bottom"
            ),
        )
        log.info("Score [crop]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_expand(self) -> None:
        """Test

        Expand an image by padding transparent margins.
        """
        log = logging.getLogger("steam_editor_tools.test")
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-expand.webp")),
            stet.ImageSingle(self.get_data_path("example.png")).crop(
                (1280, 720), anchor="center"
            ),
        )
        log.info("Score [expand]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_resize(self) -> None:
        """Test

        Resize an image.
        """
        log = logging.getLogger("steam_editor_tools.test")
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-resize.webp")),
            stet.ImageSingle(self.get_data_path("example.png")).resize((320, None)),
        )
        log.info("Score [resize]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_save(self) -> None:
        """Test

        Save an image.
        """
        log = logging.getLogger("steam_editor_tools.test")
        img = stet.ImageSingle(
            Image.new(mode="RGB", size=(400, 300), color="red"), fmt="webp"
        )
        with stet.utils.NamedTempFolder() as path:
            img.save(os.path.join(path, "test.png"))
            img.to_lossless().save(os.path.join(path, "test.webp"))
            img.save(os.path.join(path, "test.webp"))
            img.save(os.path.join(path, "test.jpg"))
        log.info("Successfully testing image saving.")

    def test_improc_quality(self) -> None:
        """Test

        Save an image.
        """
        log = logging.getLogger("steam_editor_tools.test")
        img = (
            stet.ImageMultiLayer(width=400, height=300, fmt="webp_lossless")
            .add_image(
                stet.ImageSingle(
                    Image.new(mode="RGB", size=(200, 100), color="red"),
                ),
                "block1",
                pos_shift=(-50, 0),
            )
            .add_image(
                stet.ImageSingle(
                    Image.new(mode="RGB", size=(200, 100), color="blue"),
                ),
                "block2",
                pos_shift=(50, 0),
            )
            .add_background()
            .flatten()
            .convert("RGB")
        )
        with stet.utils.NamedTempFolder() as path:
            img.to_palette(2).save(os.path.join(path, "test_small.webp"), quality="low")
            img.save(os.path.join(path, "test_big.webp"), quality="high")
            size_small = (
                self.get_file_size(os.path.join(path, "test_small.webp")) / 1024
            )
            size_big = self.get_file_size(os.path.join(path, "test_big.webp")) / 1024
            assert size_small < size_big
            log.info(
                "Image size compare (lossless): [low quality: {0:g}K] < "
                "[high quality: {1:g}K]".format(size_small, size_big)
            )

            img = img.to_lossy()
            img.save(os.path.join(path, "test_small.webp"), quality="low")
            img.save(os.path.join(path, "test_big.webp"), quality="high")
            size_small = (
                self.get_file_size(os.path.join(path, "test_small.webp")) / 1024
            )
            size_big = self.get_file_size(os.path.join(path, "test_big.webp")) / 1024
            assert size_small < size_big
            log.info(
                "Image size compare (lossy): [low quality: {0:g}K] < "
                "[high quality: {1:g}K]".format(size_small, size_big)
            )

    def test_improc_anchor(self) -> None:
        """Test

        Resize an image.
        """
        log = logging.getLogger("steam_editor_tools.test")
        img = stet.ImageSingle(self.get_data_path("example.png"))
        for pos in stet.ImageAnchor:
            score = self.ssim(
                stet.ImageSingle(self.get_data_path("ref-{0}.webp".format(pos.name))),
                stet.ImageMultiLayer((640, 360))
                .add_image(img, name="layer", anchor=pos)
                .flatten(),
            )
            log.info("Score [anchor={1}]: {0:g}".format(score, pos.name))
            assert score > 0.95

    def test_improc_near(self) -> None:
        """Test

        Place images relatively.
        """
        log = logging.getLogger("steam_editor_tools.test")
        img = stet.ImageSingle(self.get_data_path("example.png"))
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-near.webp")),
            stet.ImageMultiLayer((640, 360))
            .add_image(img, name="layer1", anchor=stet.ImageAnchor.right)
            .add_image(
                img,
                name="layer2",
                anchor=stet.ImageAnchor.left,
                related_to="layer1",
                rel_anchor=stet.ImageAnchor.right,
            )
            .flatten(),
        )
        log.info("Score [near]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_text(self) -> None:
        """Test

        Image text rendering.
        """
        log = logging.getLogger("steam_editor_tools.test")
        color = "#ffffff"
        stroke = "#000000"
        shadow = "#000000"
        font = self.get_data_path("Roboto-Regular.ttf")
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-text.webp")),
            stet.ImageMultiLayer((640, 640))
            .add_text(
                "Title",
                name="text1",
                font=font,
                font_size="h1",
                color=color,
                stroke_color=stroke,
                shadow_color=shadow,
                anchor="bottom",
                rel_anchor="center",
            )
            .add_text(
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
            )
            .add_text(
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
            )
            .add_background()
            .flatten(),
        )
        log.info("Score [text]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_img_and_text(self) -> None:
        """Test

        Hybrid image containing image and text.
        """
        log = logging.getLogger("steam_editor_tools.test")
        color = "#ffffff"
        stroke = "#000000"
        shadow = "#000000"
        font = self.get_data_path("Roboto-Regular.ttf")
        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-img_and_text.webp")),
            stet.ImageMultiLayer((800, 640))
            .add_image(
                stet.ImageSingle(self.get_data_path("example.png")), name="layer1"
            )
            .add_text(
                "Test Text",
                name="text1",
                font=font,
                font_size="h1",
                color=color,
                stroke_color=stroke,
                shadow_color=shadow,
                related_to="layer1",
            )
            .add_background()
            .flatten(),
        )
        log.info("Score [img and text]: {0:g}".format(score))
        assert score > 0.95

    @pytest.mark.needs_latex
    def test_improc_complicated(self) -> None:
        """Test

        Hybrid image containing image, text, and latex.
        """
        log = logging.getLogger("steam_editor_tools.test")
        color = "#ffffff"
        stroke = "#000000"
        shadow = "#000000"
        font = self.get_data_path("Roboto-Regular.ttf")

        def set_glow_mode(
            img: stet.ImageMultiLayer, name: str, mode: stet.ImageComposerMode
        ) -> None:
            glow = img.layers[name].effects.glow
            if glow is None:
                return
            glow.mode = mode

        _img = (
            stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless)
            .add_image(
                stet.ImageSingle(self.get_data_path("example.png")), name="layer1"
            )
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

        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-complicated.webp")),
            _img.add_background().flatten(),
        )
        log.info("Score [complicated]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_effects(self) -> None:
        """Test

        Test a complicated effect.
        """
        log = logging.getLogger("steam_editor_tools.test")

        _img = (
            stet.ImageMultiLayer((800, 640), fmt=stet.ImageFormat.webp_lossless)
            .add_image(
                stet.ImageSingle(self.get_data_path("example.png")), name="layer1"
            )
            .add_image(
                stet.ImageSingle(Image.new("RGBA", (500, 200), color="red")),
                name="block",
                related_to="layer1",
            )
        )
        _img.layers["block"].effects.alpha_content = 0
        _img.layers["block"].add_overlay_color("#ffff0044", mode="screen")
        _img.layers["block"].set_bevel(max_distance=20)
        _img.layers["block"].set_shadow(size=10, offset=16)

        score = self.ssim(
            stet.ImageSingle(self.get_data_path("ref-effects.webp")),
            _img.add_background().flatten(),
        )
        log.info("Score [effects]: {0:g}".format(score))
        assert score > 0.95

    def test_improc_composers(self) -> None:
        """Test

        Test the performance of all composers.
        """
        log = logging.getLogger("steam_editor_tools.test")

        img = stet.ImageMultiLayer((64, 64)).add_background(color="#307040")
        img.add_image(
            stet.ImageSingle(Image.new("RGB", (32, 32), color="#112233")), "block"
        )

        def locate_pixel(
            _img: stet.ImageSingle, pos: tuple[int, int]
        ) -> tuple[float, ...]:
            _img_i = _img.img
            _img_p = _img_i.load()
            if _img_p is None:
                raise ValueError("Unable to get the image pixels.")
            val = _img_p[pos[0], pos[1]]
            if isinstance(val, (int, float)):
                val = float(val)
                val = (val, val, val, 255.0)
            else:
                val = tuple(float(_val) for _val in val)
            return val

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

        with open(self.get_data_path("composer.json"), "r", encoding="utf-8") as fobj:
            data: dict[str, tuple[float, ...]] = json.load(fobj)

        for mode in modes:
            img.layers["block"].effects.blend = mode
            bg_val = locate_pixel(img.flatten(), (0, 0))
            fg_val = locate_pixel(img.flatten(), (32, 32))
            score_bg = float(
                1 - np.mean(np.abs(np.asarray(bg_val) - np.asarray(data["base"]))) / 512
            )
            score_fg = float(
                1 - np.mean(np.abs(np.asarray(fg_val) - np.asarray(data[mode]))) / 512
            )
            log.info(
                "Score [composer][{0}]: {1:g}, {2: g}".format(mode, score_bg, score_fg)
            )
            assert score_bg > 0.99
            assert score_fg > 0.99
