# -*- coding: UTF-8 -*-
"""
Data
=====
@ Steam Editor Tools - Image Processing

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The data structures for configuring this package.
"""

import enum

from typing_extensions import Self, TypedDict

from PIL import Image

from pydantic import BaseModel


__all__ = (
    "TeXTemplate",
    "Templates",
    "ImageFontAbsSize",
    "ImageFontSize",
    "ImageFormat",
    "ImageQuality",
    "ImageAnchor",
)


class TeXTemplate(BaseModel):
    """The template used for rendering LaTeX."""

    prep: str
    """The beginning part of the LaTeX template."""

    end: str
    """The end part of the LaTeX template."""

    def render(self, text: str) -> str:
        """Render the content of the full `.tex` file.

        Here `text` should be an equation.
        """
        return "{0}{1}{2}".format(self.prep, text.strip(), self.end)


class Templates(TypedDict):
    """Default supported LaTeX templates."""

    default: TeXTemplate
    """The default LaTeX template."""

    chinese: TeXTemplate
    """The LaTeX template used for rendering equations containing Chinese."""

    multilines: TeXTemplate
    """The LaTeX template only contains a bare equation environment. Use it for
    writing multi-line equations."""

    multilines_chinese: TeXTemplate
    """The LaTeX template "multilines" with Chinese support."""


class ImageFontAbsSize(BaseModel):
    """Absolute image text size."""

    n_per_line: int | None = None
    """Number of characters per line."""

    font_size: int
    """The absolute font size."""


class ImageFontSize(enum.Enum):
    """Size of the text in the image.

    This font size is high-level. When renderin the text, the pixel size of the
    text will be determined by this size and the number of characters.
    """

    h1 = "h1"
    h2 = "h2"
    h3 = "h3"
    h4 = "h4"

    @classmethod
    def from_str(cls: type[Self], val: str | Self) -> Self:
        """Use a `str` to define this size.

        The argument `val` should be `h1`-`h4`.
        """
        if isinstance(val, cls):
            return val
        elif isinstance(val, ImageFontSize):
            return cls(value=val.value)
        val = val.strip().casefold()
        return cls(value=val)

    def get_line_size(self, n_text: int) -> tuple[int, int]:
        """Get the sizes of the text.

        Arguments
        ---------
        n_text: `int`
            The length of the text to be rendered.

        Returns
        -------
        #1: `int`
            The number of characters for each line.

        #2: `int`
            The pixel font size.
        """
        if self == ImageFontSize.h1:
            return self._get_line_h1(n_text)
        elif self == ImageFontSize.h2:
            return self._get_line_h2(n_text)
        elif self == ImageFontSize.h3:
            return self._get_line_h3(n_text)
        else:
            return self._get_line_h4(n_text)

    def _get_line_h1(self, n_text: int) -> tuple[int, int]:
        """(Private) Dynamically get the font size when this value is h1."""
        if n_text < 17:
            n_width = 16
            size_font = 96
        elif n_text < 33:
            n_width = 16
            size_font = 64
        elif n_text < 49:
            n_width = 24
            size_font = 48
        else:
            n_width = 32
            size_font = 36
        return n_width, size_font

    def _get_line_h2(self, n_text: int) -> tuple[int, int]:
        """(Private) Dynamically get the font size when this value is h2."""
        if n_text < 25:
            n_width = 24
            size_font = min(96, int((24 * 44) / n_text))
        elif n_text < 49:
            n_width = 24
            size_font = 44
        elif n_text < 91:
            n_width = 30
            size_font = 36
        else:
            n_width = 36
            size_font = 30
        return n_width, size_font

    def _get_line_h3(self, n_text: int) -> tuple[int, int]:
        """(Private) Dynamically get the font size when this value is h3."""
        if n_text < 25:
            n_width = 24
            size_font = min(80, int((24 * 36) / n_text))
        elif n_text < 49:
            n_width = 24
            size_font = 36
        elif n_text < 91:
            n_width = 30
            size_font = 28
        else:
            n_width = 36
            size_font = 24
        return n_width, size_font

    def _get_line_h4(self, n_text: int) -> tuple[int, int]:
        """(Private) Dynamically get the font size when this value is h4."""
        if n_text < 31:
            n_width = 30
            size_font = min(48, int((30 * 36) / n_text))
        elif n_text < 61:
            n_width = 30
            size_font = 36
        else:
            n_width = 45
            size_font = 24
        return n_width, size_font


class ImageFormat(enum.Enum):
    """The image file format.

    This format is only used when saving the images to files.
    """

    png = "png"
    jpeg = "jpeg"
    webp = "webp"
    webp_lossless = "webp_lossless"

    @classmethod
    def from_str(cls: type[Self], val: str | Self) -> Self:
        """Use a `str` to define this size.

        The argument `val` should be a file name extension without the staring dot.

        For example `jpg` or `jpeg` will be converted to `ImageFormat.jpeg`.
        """
        if isinstance(val, cls):
            return val
        elif isinstance(val, ImageFormat):
            return cls(value=val.value)
        val = val.strip().casefold()
        if val == "jpg":
            val = "jpeg"
        return cls(value=val)

    @classmethod
    def from_img(cls: type[Self], img: Image.Image) -> Self:
        """Get the appropriate image format by inferring from the image object."""
        if img.format is not None:
            return cls.from_str(img.format)
        img_mode = img.mode
        if img_mode in ("1", "L"):
            return cls(value="png")
        if img_mode in ("P", "RGBA"):
            return cls(value="webp_lossless")
        else:
            return cls(value="webp")

    def as_fmt_str(self) -> str:
        """Convert this value as the format name that can be used in pillow."""
        if self.value == "webp_lossless":
            return "webp"
        else:
            return self.value


class ImageQuality(enum.Enum):
    """The image quality.

    Will be interpreted in different ways for different image formats.
    """

    low = "low"
    medium = "medium"
    high = "high"


class ImageAnchor(enum.Enum):
    """The image anchor.

    Inspired by LaTeX/TikZ's node anchors. This value can help users
    put the image near another image easily.

    For example, we can align the "top left" corner of an image to the same position
    of another image. Then the two image will share the same top-left corner
    position.
    """

    top_left = "top left"
    top_center = "top center"
    top_right = "top right"
    left = "left"
    center = "center"
    right = "right"
    bottom_left = "bottom left"
    bottom_center = "bottom center"
    bottom_right = "bottom right"

    @classmethod
    def from_str(cls: type[Self], val: str | Self) -> Self:
        """Use a `str` to define this size.

        The text used for conversion is flexible. For example, both
        "bottom-left" and "bottom left" will be converted to
        `ImageAnchor.bottom_left`.
        """
        if isinstance(val, cls):
            return val
        elif isinstance(val, ImageAnchor):
            return cls(value=val.value)
        val = val.strip().casefold()
        _val = set(val.split(" "))
        if "top" in _val:
            if "left" in _val:
                return cls(value="top left")
            elif "right" in _val:
                return cls(value="top right")
            else:
                return cls("top center")
        elif "bottom" in _val:
            if "left" in _val:
                return cls(value="bottom left")
            elif "right" in _val:
                return cls(value="bottom right")
            else:
                return cls("bottom center")
        elif "left" in _val:
            return cls(value="left")
        elif "right" in _val:
            return cls(value="right")
        elif "center" in _val or "middle" in _val:
            return cls(value="center")
        raise ValueError("Unrecognized ImageAnchor str: {0}".format(val))
