# -*- coding: UTF-8 -*-
"""
Renderer
========
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
The single-layer and multi-layer image renderers. This module provides easy-to-use
methods for optimizing the images when saving them.
"""

import os
import inspect
import collections
import collections.abc
import textwrap

from typing import Any, IO
from typing_extensions import Self, TypedDict, overload

from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter
from PIL import ImageDraw
from PIL import ImageFont

from .data import (
    TeXTemplate,
    ImageFontAbsSize,
    ImageFontSize,
    ImageFormat,
    ImageQuality,
    ImageAnchor,
)
from .font import FontInfo
from .latex_to_img import TeXRenderer
from .composer import ImageComposer
from .layer import ImageLayer
from .variables import steam_color


__all__ = ("ImageSingle", "ImageText", "ImageTeX", "ImageMultiLayer")


class _LayerPos(TypedDict):
    """(Private) Real position of an image layer."""

    pos: tuple[int, int]
    size: tuple[int, int]


class ImageSingle:
    """The basic one-layer style of image.

    Add some extended method for providing extra image processing features.
    """

    __slots__ = ("img", "fmt")

    def __init__(
        self,
        img: "str | os.PathLike[str] | IO[bytes] | Image.Image | Self",
        fmt: str | ImageFormat | None = None,
    ) -> None:
        """Initialization.

        Arguments
        ---------
        img: `str | PathLike[str] | IO[bytes] | Image.Image | ImageSingle`
            The image used for initializing this instance. It can be a file path,
            a file-like object, an image object or this kind of object.

        fmt: `str | ImageFormat | None`
            The format to be used for saving this image. If not specified, will
            try to automatically infer the format.
        """
        if isinstance(img, ImageSingle):
            _img = img.img
            _fmt = img.fmt if fmt is None else ImageFormat.from_str(fmt)
        else:
            if not isinstance(img, Image.Image):
                img = Image.open(img, mode="r")
                img.load()
            _img = img
            _fmt = (
                ImageFormat.from_img(img) if fmt is None else ImageFormat.from_str(fmt)
            )
        self.fmt: ImageFormat = _fmt
        self.img: Image.Image = _img.copy()

    @property
    def width(self) -> int:
        """Property: The image width."""
        return self.img.width

    @property
    def height(self) -> int:
        """Property: The image height."""
        return self.img.height

    @property
    def size(self) -> tuple[int, int]:
        """Property: The image `(width, height)`."""
        return self.img.size

    def copy(self: Self) -> Self:
        """Get a copy of this object.

        Returns
        -------
        #1: `Self`
            The copied image.
        """
        return self.__class__(img=self, fmt=None)

    def to_lossless(self: Self) -> Self:
        """Convert the format of this image to the lossless type.

        This operation is non-inplace.

        Returns
        -------
        #1: `Self`
            The converted image.
        """
        if self.fmt == ImageFormat.webp:
            fmt = ImageFormat.webp_lossless
        elif self.fmt in (ImageFormat.jpeg,):
            fmt = ImageFormat.png
        else:
            fmt = self.fmt
        return self.__class__(img=self.img, fmt=fmt)

    def to_lossy(self: Self) -> Self:
        """Convert the format of this image to the lossy type.

        This operation is non-inplace.

        Returns
        -------
        #1: `Self`
            The converted image.
        """
        if self.fmt in (
            ImageFormat.webp_lossless,
            ImageFormat.png,
        ):
            fmt = ImageFormat.webp
        else:
            fmt = self.fmt
        return self.__class__(img=self.img, fmt=fmt)

    def to_palette(self: Self, n: int | None = None) -> Self:
        """Quantize the image and convert the image mode to the palette-based mode.
        Note that this method will convert the image to the RGB image.

        This operation is non-inplace.

        Arguments
        ---------
        n: `int | None`
            The number of colors used in the palette. If not specified, will use
            `Image.Palette.WEB` palette.

        Returns
        -------
        #1: `Self`
            The converted image.
        """
        if n is None:
            img = self.img.convert(mode="RGB").convert(
                "P", dither=Image.Dither.NONE, palette=Image.Palette.WEB
            )
            return self.__class__(img=img, fmt=self.fmt)
        img = self.img.convert(mode="RGB").convert(
            "P", dither=Image.Dither.NONE, palette=Image.Palette.ADAPTIVE, colors=n
        )
        return self.__class__(img=img, fmt=self.fmt)

    def convert(self: Self, mode: str) -> Self:
        """Convert the image mode.

        This operation is non-inplace.

        Arguments
        ---------
        mode: `str`
            The mode of the converted image.

        Returns
        -------
        #1: `Self`
            The converted image.
        """
        if self.img.mode == mode:
            return self.__class__(img=self.img.copy(), fmt=self.fmt)
        img = self.img.convert(mode)
        return self.__class__(img=img, fmt=self.fmt)

    def quantize(self: Self, n: int = 16) -> Self:
        """Quantize the image.

        This operation is non-inplace.

        Arguments
        ---------
        n: `int`
            The number of colors used during the quantization.

        Returns
        -------
        #1: `Self`
            The converted image.
        """
        img = self.img.quantize(
            colors=n,
            method=(
                Image.Quantize.FASTOCTREE
                if self.img.mode == "RGBA"
                else Image.Quantize.MAXCOVERAGE
            ),
        )
        return self.__class__(img=img, fmt=self.fmt)

    @staticmethod
    def __save_quantize(img: Image.Image, quality: ImageQuality) -> Image.Image:
        """(Private) The quantize step of the `save()` method."""
        if img.mode == "RGBA" or quality == ImageQuality.high:
            n_colors = None
        elif quality == ImageQuality.medium:
            n_colors = 256
        else:
            n_colors = 16
        if n_colors is not None and (img.mode not in ("1", "L", "P")):
            img = img.quantize(
                colors=n_colors,
                method=(
                    Image.Quantize.FASTOCTREE
                    if img.mode == "RGBA"
                    else Image.Quantize.MAXCOVERAGE
                ),
            )
            img = img.convert(
                "P",
                dither=Image.Dither.NONE,
                palette=Image.Palette.ADAPTIVE,
                colors=n_colors,
            )
        return img

    @staticmethod
    def __save_quality(quality: ImageQuality) -> int:
        """(Private) Get the quality of the `save()` method."""
        if quality == ImageQuality.high:
            return 85
        elif quality == ImageQuality.medium:
            return 75
        else:
            return 60

    def __save_solve_fmt(
        self, fobj: "str | os.PathLike[str] | IO[bytes]"
    ) -> ImageFormat:
        """(Private) Infer the format used in the `save()` method."""
        if isinstance(fobj, (str, os.PathLike)):
            fobj = str(fobj)
            postfix = (
                os.path.splitext(fobj)[-1].strip().casefold().lstrip(".").strip("")
            )
        else:
            postfix = ""
        fmt = self.fmt
        _fmt = ImageFormat.from_str(postfix) if postfix else None
        if _fmt is not None:
            if fmt in (ImageFormat.webp, ImageFormat.webp_lossless) and _fmt in (
                ImageFormat.webp,
                ImageFormat.webp_lossless,
            ):
                return fmt
            return _fmt
        return fmt

    def save(
        self,
        fobj: "str | os.PathLike[str] | IO[bytes]",
        quality: str | ImageQuality = ImageQuality.high,
    ) -> None:
        """Save the image as a file.

        Before saving the image, this method will run optimizations corresponding to
        the saving format.

        Arguments
        ---------
        fobj: `str | IO[bytes]`
            The file path of file-like object of the output file.

        quality: `str | ImageQuality`
            The quality of the image to be saved.
        """
        fmt = self.__save_solve_fmt(fobj)
        quality = (
            quality
            if isinstance(quality, ImageQuality)
            else ImageQuality(value=quality)
        )
        if fmt == ImageFormat.png:
            img = self.__save_quantize(self.img, quality)
            img.save(fobj, format="png", optimize=True, compress_level=9)
        elif fmt == ImageFormat.webp_lossless:
            img = self.__save_quantize(self.img, quality)
            img.save(fobj, format="webp", lossless=True, quality=100)
        elif fmt == ImageFormat.webp:
            img = self.img
            if img.mode == "RGBA":
                img.save(
                    fobj,
                    format="webp",
                    lossless=False,
                    quality=self.__save_quality(quality),
                    alpha_quality=int(0.8 * self.__save_quality(quality)),
                )
            else:
                img.save(
                    fobj,
                    format="webp",
                    lossless=False,
                    quality=self.__save_quality(quality),
                )
        elif fmt == ImageFormat.jpeg:
            img = self.img
            img.convert("RGB").save(
                fobj,
                format="jpeg",
                optimize=True,
                quality=self.__save_quality(quality),
                subsampling=1 if quality == ImageQuality.high else 2,
            )
        else:
            raise TypeError("Format {0} is not supported yet.".format(fmt))

    def save_steam_screenshot(
        self,
        folder_path: "str | os.PathLike[str]",
        file_name: str,
        quality: str | ImageQuality = ImageQuality.high,
    ) -> None:
        """Save the image as a Steam screenshot.

        When using this method to save the image, we will create a "thumbnails"
        folder where we save the image, and save the small version
        (thumbnail image) in the "thumbnails" folder.

        Arguments
        ---------
        folder_path: `str`
            The path of the folder where we save the image.

        file_name: `str`
            The name of the saved screenshot file.

        quality: `str | ImageQuality`
            The quality of the image to be saved.
        """
        os.makedirs(folder_path, exist_ok=True)
        thumb_folder = os.path.join(folder_path, "thumbnails")
        os.makedirs(thumb_folder, exist_ok=True)
        file_path = os.path.join(folder_path, file_name)
        thumb_path = os.path.join(thumb_folder, file_name)
        self.__class__(img=self.img, fmt=ImageFormat.jpeg).save(
            file_path, quality=quality
        )
        self.__class__(
            img=self.img.resize(
                (200, max(1, round(self.img.height / self.img.width * 200))),
                resample=Image.Resampling.NEAREST,
            ).convert("RGB"),
            fmt=ImageFormat.jpeg,
        ).save(thumb_path, quality=ImageQuality.medium)

    def blur(
        self,
        blur_size: int,
        dil_size: int | None = None,
    ):
        """Make the image blured.

        This operation is non-inplace.

        Arguments
        ---------
        blur_size: `int`
            The size of blur filter.

        dil_size: `int | None`
            The size of the dilation. If not specified, it will be the same as
            `blur_size`.

        Returns
        -------
        #1: `Self`
            The modified image.
        """
        blur_size = max(0, blur_size)
        if dil_size is None:
            dil_size = blur_size
        dil_size = max(0, dil_size)
        img = self.img.copy()
        if dil_size > 0:
            img = img.filter(ImageFilter.MaxFilter(dil_size * 2 + 1)).filter(
                ImageFilter.SMOOTH
            )
        if blur_size > 0:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_size))
        return self.__class__(img=img, fmt=self.fmt)

    @overload
    def resize(
        self: Self, size: tuple[None, int], resample: int | None = None
    ) -> Self: ...

    @overload
    def resize(
        self: Self, size: tuple[int, None], resample: int | None = None
    ) -> Self: ...

    @overload
    def resize(
        self: Self, size: tuple[int, int], resample: int | None = None
    ) -> Self: ...

    def resize(
        self: Self, size: tuple[int | None, int | None], resample: int | None = None
    ) -> Self:
        """Resize this image.

        This operation is non-inplace.

        Arguments
        ---------
        size: `(int | None, int | None)`
            The size of the resized image.

            One of the size can be `None`, which means preserving the w-h ratio.

        resample: `int | None`
            The resample method specified by `Image.Resampling`.

            If not specified, will select the resample method automatically:

            1. If `size` is smaller than the current image size (for either width or
               height), will use `Image.Resampling.LANCZOS`.

            2. Otherwise (usually used for enlarging the image), use
               `Image.Resampling.BICUBIC`.

        Returns
        -------
        #1: `Self`
            The resized image.
        """
        _width = size[0]
        _height = size[1]
        if _width is None:
            if _height is None:
                raise TypeError('The arugment "size" cannot be `(None, None)`.')
            ratio = self.img.width / self.img.height
            _width = max(1, round(_height * ratio))
        if _height is None:
            if _width is None:
                raise TypeError('The arugment "size" cannot be `(None, None)`.')
            ratio = self.img.height / self.img.width
            _height = max(1, round(_width * ratio))
        _size = (_width, _height)
        resample = (
            Image.Resampling.LANCZOS
            if (_size[0] < self.img.width or _size[1] < self.img.height)
            else Image.Resampling.BICUBIC
        )
        return self.__class__(
            img=self.img.resize(size=_size, resample=resample), fmt=self.fmt
        )

    def crop(
        self: Self,
        size: tuple[int | None, int | None],
        anchor: str | ImageAnchor = ImageAnchor.center,
    ) -> Self:
        """Crop this image.

        This operation is non-inplace.

        Arguments
        ---------
        size: `tuple[int | None, int | None]`
            The size of the cropped image. If this size is larger than the original
            size, the image mode will be converted to RGBA.

            If a size is value `None`, will treat it as width/height.

        anchor: `str | ImageAnchor`
            The anchor where we set for cropping the image. For example, when this
            anchor is "center", will crop the image for four sides.

        Returns
        -------
        #1: `Self`
            The cropped image.
        """
        size_prev = self.img.size
        if size[0] is None and size[1] is None:
            return self.copy()
        _width = self.width if size[0] is None else size[0]
        _height = self.height if size[1] is None else size[1]
        size_crop = (min(_width, size_prev[0]), min(_height, size_prev[1]))
        _anchor = ImageAnchor.from_str(anchor).value
        if "top" in _anchor:
            v_start = 0
        elif "bottom" in _anchor:
            v_start = size_prev[1] - size_crop[1]
        else:
            v_start = (size_prev[1] - size_crop[1]) // 2
        if "left" in _anchor:
            h_start = 0
        elif "right" in _anchor:
            h_start = size_prev[0] - size_crop[0]
        else:
            h_start = (size_prev[0] - size_crop[0]) // 2
        img_crop = self.img.crop(
            (h_start, v_start, h_start + size_crop[0], v_start + size_crop[1])
        )
        if not ((_width > size_crop[0]) or (_height > size_crop[1])):
            return self.__class__(img=img_crop, fmt=self.fmt)
        img_crop = img_crop.convert("RGBA")
        edge_color = img_crop.getpixel((0, 0))
        if edge_color is None:
            edge_color = (0, 0, 0, 0)
        elif isinstance(edge_color, (int, float)):
            edge_color = (int(edge_color), int(edge_color), int(edge_color), 0)
        img_target = Image.new("RGBA", (_width, _height), (*edge_color[:3], 0))
        if "top" in _anchor:
            v_start = 0
        elif "bottom" in _anchor:
            v_start = _height - size_crop[1]
        else:
            v_start = (_height - size_crop[1]) // 2
        if "left" in _anchor:
            h_start = 0
        elif "right" in _anchor:
            h_start = _width - size_crop[0]
        else:
            h_start = (_width - size_crop[0]) // 2
        img_target.paste(img_crop, (h_start, v_start))
        return self.__class__(img=img_target, fmt=self.fmt)

    def add_background(
        self: Self, color: str | tuple[float, ...] = steam_color
    ) -> Self:
        """Add a background to the image.

        If the current image mode is not RGBA, the output image mode will be
        converted to RGB automatically.

        Arguments
        ---------
        color: `str | tuple[float, ...]`
            The color of the added background.

        Returns
        -------
        #1: `Self`
            The modified image.
        """
        img_new = Image.new("RGBA", size=self.img.size, color=color)
        img_foreground = self.img.convert("RGBA")
        img_new.alpha_composite(img_foreground, (0, 0))
        if self.img.mode != "RGBA":
            img_new = img_new.convert("RGB")
        return self.__class__(img=img_new, fmt=self.fmt)


class ImageText:
    """A layer of text that can be rendered as an image.

    The image will be rendered every time when it is accessed.
    """

    __slots__ = (
        "__text",
        "font",
        "__font_size",
        "pad_size",
        "color",
        "__temp_vars",
        "__temp_img",
    )

    def __init__(
        self,
        text: str,
        font: "str | os.PathLike[str] | FontInfo | None" = None,
        font_size: int | str | ImageFontSize | ImageFontAbsSize = ImageFontSize.h2,
        pad_size: int = 0,
        color: str | tuple[float, ...] = "#FFFFFF",
    ) -> None:
        """Initialization.

        Arguments
        ---------
        text: `str`
            The text to be rendered.

        font: `str | os.PathLike[str] | FontInfo | None`
            The path of the font, or the searched font used for rendering the text.
            If not specified, will use the default font.

        font_size: `int | str | ImageFontAbsSize | ImageFontSize`
            The dynamic font size of the rendered text. If using `int`, this size
            will be absolute.

        pad_size: `int`
            The size used for padding on all sides of the text.

        color: `str | tuple[float, ...]`
            The text color.
        """
        text = "\n".join((line.strip() for line in text.strip().splitlines()))
        self.__text: str = text
        self.font: "str | os.PathLike[str] | FontInfo | None" = font
        self.__font_size: ImageFontAbsSize | ImageFontSize = (
            ImageFontAbsSize(font_size=font_size)
            if isinstance(font_size, int)
            else (
                font_size
                if isinstance(font_size, ImageFontAbsSize)
                else ImageFontSize.from_str(font_size)
            )
        )
        self.pad_size: int = int(pad_size)
        self.color: str | tuple[float, ...] = color

        # Temp vars
        self.__temp_vars: dict[str, Any] = dict()
        self.__temp_img: Image.Image | None = None

    @property
    def text(self) -> str:
        """Property: The text to be rendered."""
        return self.__text

    @text.setter
    def text(self, val: str) -> None:
        """Property: The text to be rendered."""
        self.__text = "\n".join((line.strip() for line in val.strip().splitlines()))
        self.__temp_vars.clear()
        self.__temp_img = None

    @property
    def font_size(self) -> ImageFontAbsSize | ImageFontSize:
        """Property: The font size (dynamic or absolute size)."""
        return self.__font_size

    @font_size.setter
    def font_size(self, val: int | str | ImageFontSize | ImageFontAbsSize) -> None:
        """Property: The font size (dynamic or absolute size)."""
        self.__font_size = (
            ImageFontAbsSize(font_size=val)
            if isinstance(val, int)
            else (
                val
                if isinstance(val, ImageFontAbsSize)
                else ImageFontSize.from_str(val)
            )
        )
        self.__temp_vars.clear()
        self.__temp_img = None

    @property
    def width(self) -> int:
        if "im_width" not in self.__temp_vars:
            self._renew_size_info()
        return self.__temp_vars["im_width"] + 2 * self.pad_size

    @property
    def height(self) -> int:
        if "im_height" not in self.__temp_vars:
            self._renew_size_info()
        return self.__temp_vars["im_height"] + 2 * self.pad_size

    @property
    def size(self) -> tuple[int, int]:
        if ("im_width" not in self.__temp_vars) or (
            "im_height" not in self.__temp_vars
        ):
            self._renew_size_info()
        pad_size = 2 * self.pad_size
        return (
            self.__temp_vars["im_width"] + pad_size,
            self.__temp_vars["im_height"] + pad_size,
        )

    def copy(self) -> Self:
        """Get a copy of this instance."""
        return self.__class__(
            text=self.__text,
            font=self.font,
            font_size=self.__font_size,
            pad_size=self.pad_size,
            color=self.color,
        )

    def _renew_size_info(self) -> None:
        """(Private) Renew the size information. This method needs to be called when
        the text or font size is changed.
        """
        if isinstance(self.__font_size, ImageFontAbsSize):
            n_width = self.__font_size.n_per_line
            size_font = self.__font_size.font_size
        else:
            n_width, size_font = self.__font_size.get_line_size(len(self.__text))
        size_line = int(size_font * 1.5)
        font = self._get_font(self.font, size_font)
        # Parse text.
        if n_width is not None:
            text_div = textwrap.wrap(self.__text, width=n_width)
        else:
            text_div = [self.__text.strip()]
        num_lines = len(text_div)
        dummy_image = Image.new("RGB", (1, 1), (255, 255, 255))
        draw = ImageDraw.Draw(dummy_image)
        max_width = 0
        for line in text_div:
            bbox = draw.textbbox((0, 0), line, font=font)
            max_width = int(max(max_width, bbox[2] - bbox[0]))
        im_width = max_width
        im_height = num_lines * size_line
        self.__temp_vars.update(
            n_width=n_width, size_font=size_font, im_width=im_width, im_height=im_height
        )

    @staticmethod
    def _get_font(
        font: "str | os.PathLike[str] | FontInfo | None", font_size: int
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Get the freetype font by the specified information."""
        if font is None:
            return ImageFont.load_default_imagefont()
        if isinstance(font, FontInfo):
            return font.get_font(font_size)
        font = str(font).strip()
        if font:
            return ImageFont.truetype(font, font_size)
        return ImageFont.load_default_imagefont()

    @staticmethod
    def _cast_text_style(
        img_shape: Image.Image, text_color: str | tuple[float, ...]
    ) -> Image.Image:
        """(Private) Cast the text with the style configuration.

        This method accept the L-mode `img_shape` and return the styled `img`.
        """
        clr = ImageColor.getcolor(text_color, "RGBA")
        if isinstance(clr, int):
            clr = (clr, clr, clr, 255)
        img_shape = Image.composite(
            Image.new("RGBA", img_shape.size, color=clr),
            Image.new("RGBA", img_shape.size, color=(*clr[:3], 0)),
            img_shape,
        )
        return img_shape

    @staticmethod
    def _create_text_mask(
        text: collections.abc.Sequence[str],
        img_size: tuple[int, int],
        pos: tuple[int, int],
        line_height: int,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ) -> Image.Image:
        """(Private) Create an L-mode text mask image."""
        img_text = Image.new("L", img_size, color=0)
        draw = ImageDraw.Draw(img_text)
        for text_idx, text_line in enumerate(text):
            draw.text(
                (pos[0], pos[1] + line_height * text_idx),
                text_line,
                font=font,
                fill=255,
            )
        return img_text

    @property
    def img(self) -> Image.Image:
        """Property: Render the text as an image, and get the pixel-based image."""
        if self.__temp_img is not None:
            return self.__temp_img
        if ("size_font" not in self.__temp_vars) or ("n_width" not in self.__temp_vars):
            self._renew_size_info()
        size_font = self.__temp_vars["size_font"]
        n_width = self.__temp_vars["n_width"]
        im_width = self.width
        im_height = self.height
        pad_size = self.pad_size
        h_start, v_start = (
            pad_size,  # width
            pad_size,  # height
        )
        # Init figure.
        img = Image.new("RGBA", (im_width, im_height), color=(0, 0, 0, 0))

        # Parse text.
        if n_width is not None:
            text_div = textwrap.wrap(self.__text, width=n_width)
        else:
            text_div = [self.__text.strip()]
        font = self._get_font(self.font, size_font)
        size_line = int(size_font * 1.5)

        # Create text mask.
        img_text = self._create_text_mask(
            text_div,
            img_size=img.size,
            pos=(h_start, v_start),
            line_height=size_line,
            font=font,
        )
        # Compose text.
        img_text = self._cast_text_style(img_text, text_color=self.color)
        img.alpha_composite(img_text, dest=(0, 0))
        self.__temp_img = img
        return img


class ImageTeX(ImageText):
    """A layer of TeX equation that can be rendered as an image.

    The image will be rendered every time when it is accessed.
    """

    __slots__ = ("template", "color", "__temp_vars", "__temp_img")

    def __init__(
        self,
        equation: str,
        template: str | TeXTemplate = "default",
        font_size: int | str | ImageFontAbsSize | ImageFontSize = ImageFontSize.h2,
        pad_size: int = 0,
        color: str | tuple[float, ...] = "#FFFFFF",
    ) -> None:
        """Initialization.

        Arguments
        ---------
        equation: `str`
            The LaTeX equation to be rendered.

            Do not add `$` or `$$` symbol to the equation.

        template: `str | TeXTemplate`
            The LaTeX template used for rendering the equation. If using `str`,
            will treat this value as the template name.

            The available templates can be found in
            `improc.variables.tex_templates`.

        font_size: `str | ImageFontSize`
            The dynamic font size of the rendered text.

        pad_size: `int`
            The size used for padding on all sides of the text.

        color: `str | tuple[float, ...]`
            The text color.
        """
        super().__init__(text="", font_size=font_size, color=color, pad_size=pad_size)
        equation = equation.strip()
        self.text: str = equation
        self.template: str | TeXTemplate = template

        self.__temp_vars: dict[str, Any] = dict()
        self.__temp_img: Image.Image | None = None

    @property
    def equation(self) -> str:
        """Property: The LaTeX equation. Equivalent to `self.text`."""
        return self.text

    @property
    def width(self) -> int:
        if "img_equation" not in self.__temp_vars:
            self._renew_size_info()
        return self.__temp_vars["img_equation"].width + 2 * self.pad_size

    @property
    def height(self) -> int:
        if "img_equation" not in self.__temp_vars:
            self._renew_size_info()
        return self.__temp_vars["img_equation"].height + 2 * self.pad_size

    @property
    def size(self) -> tuple[int, int]:
        if "img_equation" not in self.__temp_vars:
            self._renew_size_info()
        pad_size = 2 * self.pad_size
        mask: Image.Image = self.__temp_vars["img_equation"]
        return (mask.width + pad_size, mask.height + pad_size)

    def copy(self) -> Self:
        """Get a copy of this instance."""
        return self.__class__(
            equation=self.equation,
            template=self.template,
            font_size=self.font_size,
            pad_size=self.pad_size,
            color=self.color,
        )

    def _renew_size_info(self) -> None:
        """(Private) Renew the size information. This method needs to be called when
        the text or font size is changed.
        """
        resize_factor: float | None = None
        font_size = self.font_size
        if isinstance(font_size, ImageFontAbsSize):
            if font_size.font_size > 96:
                resize_factor = None
            elif font_size.font_size > 96 * 0.4:
                resize_factor = font_size.font_size / 96
            else:
                resize_factor = 0.4
        else:
            if font_size == ImageFontSize.h1:
                resize_factor = None
            elif font_size == ImageFontSize.h2:
                resize_factor = 0.8
            elif font_size == ImageFontSize.h3:
                resize_factor = 0.6
            else:
                resize_factor = 0.4
        renderer = TeXRenderer()
        img_equation = renderer.render(equation=self.text, template=self.template)
        self.__temp_vars.update(resize_factor=resize_factor, img_equation=img_equation)

    @property
    def img(self) -> Image.Image:
        """Property: Render the text as an image, and get the pixel-based image."""
        if self.__temp_img is not None:
            return self.__temp_img
        if ("resize_factor" not in self.__temp_vars) or (
            "img_equation" not in self.__temp_vars
        ):
            self._renew_size_info()
        resize_factor: float = self.__temp_vars["resize_factor"]
        _equation: Image.Image = self.__temp_vars["img_equation"]
        if resize_factor is not None:
            _equation = _equation.resize(
                size=(
                    int(resize_factor * _equation.width),
                    int(resize_factor * _equation.height),
                ),
            )
        pad_size = self.pad_size
        equation = Image.new(
            "L",
            (_equation.width + pad_size * 2, _equation.height + pad_size * 2),
            color=0,
        )
        equation.paste(_equation, (pad_size, pad_size))

        # Init figure.
        img = Image.new("RGBA", (equation.width, equation.height), color=(0, 0, 0, 0))

        # Draw the font texts.
        img_text = self._cast_text_style(equation, text_color=self.color)
        img.alpha_composite(img_text, dest=(0, 0))
        self.__temp_img = img
        return img


class ImageMultiLayer:
    """The handle of a stack of layered images.

    This class is inspired by the image editing software.

    All modifications to this class is INPLACE. If the non-inplace modification is
    required, please use copy() method.
    """

    __slots__ = ("layers", "mode", "width", "height", "fmt")

    @overload
    def __init__(
        self, width: int, height: int, fmt: str | ImageFormat = "png"
    ) -> None: ...

    @overload
    def __init__(
        self, size: tuple[int, int], fmt: str | ImageFormat = "png"
    ) -> None: ...

    @overload
    def __init__(
        self, img: ImageSingle, name: str, fmt: str | ImageFormat | None = None
    ) -> None: ...

    @overload
    def __init__(
        self, img: "ImageLayer | ImageMultiLayer", fmt: str | ImageFormat | None = None
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialization.

        Arguments (version 1)
        =====================
        width: `int`
            The width of the canvas (this multi-layered image).

        height: `int`
            The height of the canvas (this multi-layered image).

        fmt: `str | ImageFormat | None`
            The format of the image. It is used only when saving this image.

        Arguments (version 2)
        =====================
        size: `tuple[int, int]`
            The `(width, height)` of the canvas (this multi-layered image).

        fmt: `str | ImageFormat | None`
            The format of the image. It is used only when saving this image.

        Arguments (version 3)
        =====================
        img: `ImageSingle`
            The image used as the first layer of this multi-layered image. The canvas
            size will be the same as this image size.

        name: `str`
            The name of the first image layer (the layer is specified by `img`).

        fmt: `str | ImageFormat | None`
            The format of the image. It is used only when saving this image.

        Arguments (version 4)
        =====================
        img: `ImageLayer | ImageMultiLayer`
            The image used for initializing this image. If it is `ImageLayer`, will
            use this layer as the first layer. If it is `ImageMultiLayer`, will
            make a copy of the given `img`.

        fmt: `str | ImageFormat | None`
            The format of the image. It is used only when saving this image.
        """

        def from_config(
            width: int, height: int, fmt: str | ImageFormat = "png"
        ) -> tuple[tuple[ImageLayer, ...], str, int, int, ImageFormat]:
            width = int(width)
            height = int(height)
            if width < 0:
                raise TypeError(
                    "The {0} width should be greater than 0.".format(
                        self.__class__.__name__
                    )
                )
            if height < 0:
                raise TypeError(
                    "The {0} height should be greater than 0.".format(
                        self.__class__.__name__
                    )
                )
            fmt = ImageFormat.from_str(fmt)
            return tuple(), "RGBA", width, height, fmt

        def from_config_ver_size(
            size: tuple[int, int], fmt: str | ImageFormat = "png"
        ) -> tuple[tuple[ImageLayer, ...], str, int, int, ImageFormat]:
            return from_config(size[0], size[1], fmt)

        def from_img(
            img: ImageSingle, name: str, fmt: str | ImageFormat | None = None
        ) -> tuple[tuple[ImageLayer, ...], str, int, int, ImageFormat]:
            width = img.width
            height = img.height
            fmt = img.fmt if fmt is None else ImageFormat.from_str(fmt)
            layers = (ImageLayer(parent=self, img=img.copy(), name=name),)
            mode = img.img.mode
            return layers, mode, width, height, fmt

        def from_layers(
            img: ImageLayer | Self, fmt: str | ImageFormat | None = None
        ) -> tuple[tuple[ImageLayer, ...], str, int, int, ImageFormat]:
            width = img.width
            height = img.height
            if isinstance(img, ImageLayer):
                layers = (img,)
                fmt = img.fmt if fmt is None else ImageFormat.from_str(fmt)
                mode = img.img.img.mode
            else:
                layers = tuple(img_l.copy() for img_l in img.layers.values())
                fmt = img.fmt if fmt is None else ImageFormat.from_str(fmt)
                mode = img.mode
            return layers, mode, width, height, fmt

        for init_ver, validator_cls in (
            (from_config, int),
            (from_config_ver_size, tuple),
            (from_img, ImageSingle),
            (from_layers, (ImageLayer, self.__class__)),
        ):
            try:
                arguments = inspect.signature(init_ver).bind(*args, **kwargs)
                first_value = next(iter(arguments.arguments.values()))
                if not isinstance(first_value, validator_cls):
                    raise TypeError
            except TypeError:
                continue
            data = init_ver(*arguments.args, **arguments.kwargs)
            break
        else:
            raise TypeError(
                "The initialization arguments of {0} are invalid.".format(
                    self.__class__.__name__
                )
            )

        self.layers: collections.OrderedDict[str, ImageLayer] = (
            collections.OrderedDict()
        )
        for img_l in data[0]:
            if img_l.name in self.layers:
                raise KeyError(
                    "The image layer name {0} is duplicated.".format(img_l.name)
                )
            self.layers[img_l.name] = img_l
        self.mode: str = data[1]
        self.width: int = data[2]
        self.height: int = data[3]
        self.fmt: ImageFormat = data[4]

    @property
    def size(self) -> tuple[int, int]:
        """Property: The `(width, height)` of this image."""
        return (self.width, self.height)

    def add_background(
        self: Self,
        color: str | tuple[float, ...] = steam_color,
        name: str = "background",
    ) -> Self:
        """Add a background layer to this multi-layered image.

        This method is inplace.

        Arguments
        ---------
        color: `str | tuple[float, ...]`
            The color of the background to be added.

        name: `str`
            The name of the added background layer.

        Returns
        -------
        #1: `Self`
            The inplace-modified multi-layered image.
        """
        img_new = Image.new("RGBA", size=self.size, color=color)
        self.add_image(
            name=name,
            img=ImageSingle(img_new, fmt=self.fmt),
            anchor=ImageAnchor.center,
            related_to=None,
            pos_shift=None,
        )
        self.layers.move_to_end(name, last=False)
        return self

    def add_text(
        self: Self,
        text: str,
        name: str,
        font: "str | os.PathLike[str] | FontInfo | None" = None,
        font_size: int | str | ImageFontAbsSize | ImageFontSize = ImageFontSize.h2,
        color: str | tuple[float, ...] = "#FFFFFF",
        stroke_color: str | tuple[float, ...] | None = None,
        glow_color: str | tuple[float, ...] | None = None,
        shadow_color: str | tuple[float, ...] | None = None,
        anchor: str | ImageAnchor = ImageAnchor.center,
        related_to: str | None = None,
        rel_anchor: str | ImageAnchor = ImageAnchor.center,
        pos_shift: tuple[int, int] | None = None,
    ) -> Self:
        """Add a text layer to this multi-layered image.

        This method is inplace.

        Arguments
        ---------
        text: `str`
            The text to be rendered.

        name: `str`
            The name of the added text layer.

        font: `str | os.PathLike[str] | FontInfo | None`
            The path of the font, or the searched font used for rendering the text.
            If not specified, will use the default font.

        font_size: `int | str | ImageFontAbsSize | ImageFontSize`
            The dynamic font size of the rendered text. If using `int`, this size
            will be absolute.

        color: `str | tuple[float, ...]`
            The text color.

        stroke_color: `str | tuple[float, ...] | None`
            The text stroke color. If not specified, will not add a stroke to the
            text.

        glow_color: `str | tuple[float, ...] | None`
            The text glow color. If not specified, will not add a glow to the text.

        shadow_color: `str | tuple[float, ...] | None`
            The text shadow color. If not specified, will not add a shadow to the
            text.

        anchor: `str | ImageAnchor`
            The anchor of this image.

        related_to: `str | None`
            The name of another image layer. When rendering the image, will place
            this image based on the position of the image specified by `related_to`.

            If not specified, the image layer will be put related to the canvas.

        rel_anchor: `str | ImageAnchor`
            The anchor of the reference image specified by `related_to` when placing
            this image.

        pos_shift: `tuple[int, int] | None`
            The `(h_shift, v_shift)` of this image position. If not specified, will
            use `(0, 0)`.

        Returns
        -------
        #1: `Self`
            The inplace-modified multi-layered image.
        """
        img = ImageText(text, font=font, font_size=font_size, color=color)
        self.add_image(
            name=name,
            img=img,
            anchor=anchor,
            related_to=related_to,
            rel_anchor=rel_anchor,
            pos_shift=pos_shift,
        )
        layer = self.layers[name]
        if stroke_color is not None:
            layer.set_stroke(size=2, color=stroke_color)
        font_size = img.font_size
        size_font = (
            font_size.font_size
            if isinstance(font_size, ImageFontAbsSize)
            else font_size.get_line_size(len(img.text))[1]
        )
        if glow_color is not None:
            glow_size = max(2, int(0.2 * size_font))
            layer.set_glow(size=glow_size, color=glow_color)
        if shadow_color is not None:
            shadow_offset = min(4, size_font // 24)
            shadow_size = max(2, shadow_offset // 2)
            layer.set_shadow(size=shadow_size, offset=shadow_offset, color=shadow_color)
        return self

    def add_latex(
        self: Self,
        equation: str,
        name: str,
        template: str | TeXTemplate = "default",
        font_size: str | ImageFontSize = ImageFontSize.h2,
        color: str | tuple[float, ...] = "#FFFFFF",
        stroke_color: str | tuple[float, ...] | None = None,
        glow_color: str | tuple[float, ...] | None = None,
        shadow_color: str | tuple[float, ...] | None = None,
        anchor: str | ImageAnchor = ImageAnchor.center,
        related_to: str | None = None,
        rel_anchor: str | ImageAnchor = ImageAnchor.center,
        pos_shift: tuple[int, int] | None = None,
    ) -> Self:
        """Add a LaTeX equation layer to this multi-layered image.

        This method is inplace.

        Arguments
        ---------
        equation: `str`
            The LaTeX equation to be rendered.

            Do not add `$` or `$$` symbol to the equation.

        name: `str`
            The name of the added equation (text) layer.

        template: `str | TeXTemplate`
            The LaTeX template used for rendering the equation. If using `str`,
            will treat this value as the template name.

            The available templates can be found in
            `improc.variables.tex_templates`.

        font_size: `str | ImageFontSize`
            The dynamic font size of the rendered text.

        color: `str | tuple[float, ...]`
            The text color.

        stroke_color: `str | tuple[float, ...] | None`
            The text stroke color. If not specified, will not add a stroke to the
            text.

        glow_color: `str | tuple[float, ...] | None`
            The text glow color. If not specified, will not add a glow to the text.

        shadow_color: `str | tuple[float, ...] | None`
            The text shadow color. If not specified, will not add a shadow to the
            text.

        anchor: `str | ImageAnchor`
            The anchor of this image.

        related_to: `str | None`
            The name of another image layer. When rendering the image, will place
            this image based on the position of the image specified by `related_to`.

            If not specified, the image layer will be put related to the canvas.

        rel_anchor: `str | ImageAnchor`
            The anchor of the reference image specified by `related_to` when placing
            this image.

        pos_shift: `tuple[int, int] | None`
            The `(h_shift, v_shift)` of this image position. If not specified, will
            use `(0, 0)`.

        Returns
        -------
        #1: `Self`
            The inplace-modified multi-layered image.
        """
        img = ImageTeX(equation, template=template, font_size=font_size, color=color)
        self.add_image(
            name=name,
            img=img,
            anchor=anchor,
            related_to=related_to,
            rel_anchor=rel_anchor,
            pos_shift=pos_shift,
        )
        layer = self.layers[name]
        if stroke_color is not None:
            layer.set_stroke(size=2, color=stroke_color)
        if glow_color is not None:
            glow_size = 8
            layer.set_glow(size=glow_size, color=glow_color)
        if shadow_color is not None:
            shadow_offset = 4
            shadow_size = max(2, shadow_offset // 2)
            layer.set_shadow(size=shadow_size, offset=shadow_offset, color=shadow_color)
        return self

    def add_image(
        self,
        img: ImageSingle | ImageText,
        name: str,
        anchor: str | ImageAnchor = ImageAnchor.center,
        related_to: str | None = None,
        rel_anchor: str | ImageAnchor = ImageAnchor.center,
        pos_shift: tuple[int, int] | None = None,
    ) -> Self:
        """Add an image layer to this multi-layered image.

        This method is inplace.

        Arguments
        ---------
        img: `ImageSingle | ImageText`
            The image to be added.

        name: `str`
            The name of the added image layer.

        anchor: `str | ImageAnchor`
            The anchor of this image.

        related_to: `str | None`
            The name of another image layer. When rendering the image, will place
            this image based on the position of the image specified by `related_to`.

            If not specified, the image layer will be put related to the canvas.

        rel_anchor: `str | ImageAnchor`
            The anchor of the reference image specified by `related_to` when placing
            this image.

        pos_shift: `tuple[int, int] | None`
            The `(h_shift, v_shift)` of this image position. If not specified, will
            use `(0, 0)`.

        Returns
        -------
        #1: `Self`
            The inplace-modified multi-layered image.
        """
        name = str(name).strip() if name else ""
        if not name:
            raise KeyError('The argument "name" is empty.')
        if name in self.layers:
            raise KeyError(
                'The argument "name" is duplicated. An existing layer is already named by: {0}'.format(
                    name
                )
            )
        related_to = (
            related_to.strip()
            if (isinstance(related_to, str) and related_to.strip())
            else None
        )
        if (related_to is not None) and (related_to not in self.layers):
            raise KeyError(
                'The argument "related_to" does not refer to an existing image layer.'
            )
        self.layers[name] = ImageLayer(
            parent=self,
            name=name,
            img=img,
            anchor=anchor,
            related_to=related_to,
            rel_anchor=rel_anchor,
            pos_shift=pos_shift,
        )
        return self

    def __render(self) -> Image.Image:
        """(Private) Render the layer stack as a single image."""

        img_new = Image.new("RGBA", size=(self.width, self.height), color=(0, 0, 0, 0))
        pos_cache = dict()
        comp = ImageComposer()

        for _, layer in self.layers.items():
            img_new = layer.render(comp, img_new, pos_cache)

        return img_new

    def convert(self, mode: str) -> Self:
        """Convert the image mode.

        This method is inplace.

        Arguments
        ---------
        mode: `str`
            The mode of the converted image.

        Returns
        -------
        #1: `Self`
            The inplace-modified multi-layered image.
        """
        self.mode = mode
        return self

    def flatten(self) -> ImageSingle:
        """Flatten this image as a single-layer image.

        This method is non-inplace.

        Returns
        -------
        #1: `ImageSingle`
            The flattened single-layer image.
        """
        return ImageSingle(img=self.__render().convert(self.mode), fmt=self.fmt)

    def save(
        self,
        fobj: "str | os.PathLike[str] | IO[bytes]",
        quality: str | ImageQuality = ImageQuality.high,
    ) -> None:
        """Save the image as a file.

        Before saving the image, this method will run optimizations corresponding to
        the saving format.

        Arguments
        ---------
        fobj: `str | PathLike[str] | IO[bytes]`
            The file path of file-like object of the output file.

        quality: `str | ImageQuality`
            The quality of the image to be saved.
        """
        ImageSingle(img=self.__render().convert(self.mode), fmt=self.fmt).save(
            fobj, quality
        )

    def save_steam_screenshot(
        self,
        folder_path: "str | os.PathLike[str]",
        file_name: str,
        quality: str | ImageQuality = ImageQuality.high,
    ) -> None:
        """Save the image as a Steam screenshot.

        When using this method to save the image, we will create a "thumbnails"
        folder where we save the image, and save the small version
        (thumbnail image) in the "thumbnails" folder.

        Arguments
        ---------
        folder_path: `str`
            The path of the folder where we save the image.

        file_name: `str`
            The name of the saved screenshot file.

        quality: `str | ImageQuality`
            The quality of the image to be saved.
        """
        ImageSingle(
            img=self.__render().convert(self.mode), fmt=self.fmt
        ).save_steam_screenshot(folder_path, file_name, quality)
