# -*- coding: UTF-8 -*-
"""
Composer
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
Extensive `ImageChops` of `pillow`. Compared to the original version, this version
extends the image blending operators to the `RGBA` images.
"""

import collections.abc

from typing_extensions import Literal

from PIL import Image
from PIL import ImageChops


__all__ = ("ImageComposerMode", "ImageComposer")

ImageComposerMode = Literal[
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
]
"""The name of a composer mode. Pass it to ImageCompoer.by_name to fetch the binary
operator."""


class ImageComposer:
    """The image mixing operators extended to the alpha-channel (RGBA) domain.

    This composer extends the scope of `ImageChops`, which only works with non-
    transparent images (such as `L` and `RGB`). Using this extended version,
    users can stack either `RGB` or `RGBA` images, where the stacking algorithm
    will take the alpha channel into consideration.
    """

    ImageOpPrototype = collections.abc.Callable[[Image.Image, Image.Image], Image.Image]
    """The prototype of the available image operators."""

    def __init__(self) -> None:
        """Initialization."""
        self._ops_by_name: dict[ImageComposerMode, ImageComposer.ImageOpPrototype] = {
            "default": self.alpha_composite,
            "add": self.add,
            "add_modulo": self.add_modulo,
            "screen": self.screen,
            "lighter": self.lighter,
            "subtract": self.subtract,
            "subtract_modulo": self.subtract_modulo,
            "multiply": self.multiply,
            "darker": self.darker,
            "difference": self.difference,
            "soft_light": self.soft_light,
            "hard_light": self.hard_light,
        }

    def by_name(self, mode: ImageComposerMode) -> ImageOpPrototype:
        """Fetch the composer method by the mode name.

        Arguments
        ---------
        mode: `ImageComposerMode`
            The name of the composer binary operator.

        Returns
        -------
        #1: `(Image.Image, Image.Image) -> Image.Image`
            The selected composer operator.
        """
        if mode not in self._ops_by_name:
            raise TypeError("Unrecognized mode: {0}".format(mode))
        return self._ops_by_name[mode]

    @staticmethod
    def _has_alpha_channel(image: Image.Image) -> bool:
        """(Private) Check whether an image has alpha channel or not.

        Copied from `Image.Image.has_transparency_data()` for preserving
        the compatibility.
        """
        if (
            image.mode in ("LA", "La", "PA", "RGBA", "RGBa")
            or "transparency" in image.info
        ):
            return True
        if image.mode == "P":
            assert image.palette is not None
            return image.palette.mode.endswith("A")
        return False

    @classmethod
    def _run_image_op(
        cls, op: ImageOpPrototype, image_bg: Image.Image, image_fg: Image.Image
    ):
        """(Private) Run an `ImageChops` operator for `RGBA` images.

        Note that the `image_bg` and `image_fg` value in this method can have any
        mode. However, when `op` is run by this method, the input image is always
        presumed to be converted to `RGB` mode.
        """
        alpha_bg = (
            image_bg.getchannel("A") if cls._has_alpha_channel(image_bg) else None
        )
        _image_bg = image_bg.convert("RGB")
        if cls._has_alpha_channel(image_fg):
            alpha_fg = image_fg.getchannel("A")
            res = op(_image_bg, image_fg.convert("RGB"))
            res = Image.composite(res, _image_bg, alpha_fg)
        else:
            res = op(_image_bg, image_fg.convert("RGB"))
        if alpha_bg is not None:
            res = res.convert("RGBA")
            res.putalpha(alpha_bg)
        else:
            res = res.convert(image_bg.mode)
        return res

    def alpha_composite(
        self, image_bg: Image.Image, image_fg: Image.Image
    ) -> Image.Image:
        """Equivalent to `Image.alpha_composite`.

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        res = Image.alpha_composite(
            image_bg.convert("RGBA"), image_fg.convert("RGBA")
        ).convert(image_bg.mode)
        return res

    def add(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.add`.

        Adds two images by:

        ``` python
        out = clip(image1 + image2, (0, 255))
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(ImageChops.add, image_bg=image_bg, image_fg=image_fg)

    def add_modulo(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.add_modulo`.

        Add two images, without clipping the result.

        ``` python
        out = ((image1 + image2) % MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.add_modulo, image_bg=image_bg, image_fg=image_fg
        )

    def darker(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.darker`.

        Compares the two images, pixel by pixel, and returns a new image containing
        the darker values.

        ``` python
        out = min(image1, image2)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.darker, image_bg=image_bg, image_fg=image_fg
        )

    def difference(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.difference`.

        Returns the absolute value of the pixel-by-pixel difference between the two
        images.

        ``` python
        out = abs(image1 - image2)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.difference, image_bg=image_bg, image_fg=image_fg
        )

    def lighter(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.lighter`.

        Compares the two images, pixel by pixel, and returns a new image containing
        the lighter values.

        ``` python
        out = max(image1, image2)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.lighter, image_bg=image_bg, image_fg=image_fg
        )

    def _logical_op(self, op: ImageOpPrototype, threshold: int) -> ImageOpPrototype:
        """(Private) A wrapper of the logical operator.

        Ensure the input image to be converted to "1" mode before calling the
        operator.
        """

        def run(_image_bg: Image.Image, _image_fg: Image.Image) -> Image.Image:
            return op(
                self.threshold(_image_bg, threshold).convert("1"),
                self.threshold(_image_fg, threshold).convert("1"),
            )

        return run

    def logical_and(
        self, image_bg: Image.Image, image_fg: Image.Image, threshold: int = 128
    ) -> Image.Image:
        """Equivalent to `ImageChops.logical_and`.

        Both of the images will be converted to mode "1". If you would like to
        perform a logical AND on an image with a mode other than "1", try
        `self.multiply` instead, using a black-and-white mask as the second image.

        ``` python
        out = ((image1 and image2) % MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        threshold: `int`
            The threshold used for converting `image_bg` and `image_fg` to binary
            images.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """

        return self._run_image_op(
            self._logical_op(ImageChops.logical_and, threshold),
            image_bg=image_bg,
            image_fg=image_fg,
        )

    def logical_or(
        self, image_bg: Image.Image, image_fg: Image.Image, threshold: int = 128
    ) -> Image.Image:
        """Equivalent to `ImageChops.logical_or`.

        Logical OR between two images.

        Both of the images will be converted to mode "1".

        ``` python
        out = ((image1 or image2) % MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        threshold: `int`
            The threshold used for converting `image_bg` and `image_fg` to binary
            images.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            self._logical_op(ImageChops.logical_or, threshold),
            image_bg=image_bg,
            image_fg=image_fg,
        )

    def logical_xor(
        self, image_bg: Image.Image, image_fg: Image.Image, threshold: int = 128
    ) -> Image.Image:
        """Equivalent to `ImageChops.logical_xor`.

        Logical XOR between two images.

        Both of the images will be converted to mode "1".

        ``` python
        out = ((bool(image1) != bool(image2)) % MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        threshold: `int`
            The threshold used for converting `image_bg` and `image_fg` to binary
            images.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            self._logical_op(ImageChops.logical_xor, threshold),
            image_bg=image_bg,
            image_fg=image_fg,
        )

    def multiply(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.multiply`.

        Superimposes two images on top of each other.

        If you multiply an image with a solid black image, the result is black. If
        you multiply with a solid white image, the image is unaffected.

        ``` python
        out = image1 * image2 / MAX
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.multiply, image_bg=image_bg, image_fg=image_fg
        )

    def soft_light(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.soft_light`.

        Superimposes two images on top of each other using the Soft Light algorithm.

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.soft_light, image_bg=image_bg, image_fg=image_fg
        )

    def hard_light(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.hard_light`.

        Superimposes two images on top of each other using the Hard Light algorithm.

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.hard_light, image_bg=image_bg, image_fg=image_fg
        )

    def overlay(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.overlay`.

        Superimposes two images on top of each other using the Overlay algorithm.

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.overlay, image_bg=image_bg, image_fg=image_fg
        )

    def screen(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.screen`.

        Superimposes two inverted images on top of each other.

        ``` python
        out = MAX - ((MAX - image1) * (MAX - image2) / MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.screen, image_bg=image_bg, image_fg=image_fg
        )

    def subtract(self, image_bg: Image.Image, image_fg: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.subtract`.

        Subtracts two images.

        ``` python
        out = clip(image1 - image2, (0, 255))
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.subtract, image_bg=image_bg, image_fg=image_fg
        )

    def subtract_modulo(
        self, image_bg: Image.Image, image_fg: Image.Image
    ) -> Image.Image:
        """Equivalent to `ImageChops.subtract_modulo`.

        Subtract two images, without clipping the result.

        ``` python
        out = ((image1 - image2) % MAX)
        ```

        Arguments
        ---------
        image_bg: `Image`
            The background image.

        image_fg: `Image`
            The foreground image that will lay over `image_bg`.

        Returns
        -------
        #1: `Image`
            The mixed image. This returned image has the same mode of `image_bg`.
        """
        return self._run_image_op(
            ImageChops.subtract_modulo, image_bg=image_bg, image_fg=image_fg
        )

    def invert(self, image: Image.Image) -> Image.Image:
        """Equivalent to `ImageChops.invert`.

        Invert an image (channel).

        ``` python
        out = MAX - image
        ```

        Note that this operator will be applied to each channel except the alpha
        channel if the alpha channel exists.

        Arguments
        ---------
        image: `Image`
            The image to be inverted.

        Returns
        -------
        #1: `Image`
            The image with the inverted colors.
        """
        mode_img = image.mode
        is_gray = mode_img in ("LA", "La", "L", "1")
        alpha_img = image.getchannel("A") if self._has_alpha_channel(image) else None
        if is_gray:
            image = ImageChops.invert(image.convert("L"))
            if alpha_img is not None and mode_img in ("LA", "La"):
                image = image.convert("LA")
                image.putalpha(alpha_img)
        else:
            image = ImageChops.invert(image.convert("RGB"))
            if alpha_img is not None:
                image = image.convert("RGBA")
                image.putalpha(alpha_img)
        image = image.convert(mode_img)
        return image

    def invert_luminance(self, image: Image.Image) -> Image.Image:
        """Modified `ImageChops.invert`, where we only invert the luminance of the
        image, while preserve the color of the image.

        If the input image has the transparency channel, it will be preserved.

        Arguments
        ---------
        image: `Image`
            The image to be inverted.

        Returns
        -------
        #1: `Image`
            The image with the inverted colors.
        """
        mode_img = image.mode
        if mode_img in ("La", "LA", "L", "1"):
            return self.invert(image)
        alpha_img = image.getchannel("A") if self._has_alpha_channel(image) else None
        image = image.convert("YCbCr")
        l_img = image.getchannel("Y")
        l_img = ImageChops.invert(l_img)
        image = Image.merge(
            "YCbCr", (l_img, image.getchannel("Cb"), image.getchannel("Cr"))
        )
        if alpha_img is not None:
            image = image.convert("RGBA")
            image.putalpha(alpha_img)
        image = image.convert(mode_img)
        return image

    def threshold(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """Given a threshold, use this threshold to convert the image
        into a binary image.

        If the image have multiple channels, will perform the conversion
        with respect to the luminance channel.

        Arguments
        ---------
        image: `Image`
            The image to be inverted.

        threshold: `int`
            The threshold used for dividing the image.

        Returns
        -------
        #1: `Image`
            The image mask in the mode "L" or "LA". Note that we do not perform
            the mode "1" conversion because the alpha channel needs to be preserved
            if it exists.
        """
        if image.mode == "1":
            return image
        alpha_img = image.getchannel("A") if self._has_alpha_channel(image) else None
        image = image.convert("L")
        table = tuple(255 if i >= threshold else 0 for i in range(256))
        image = image.point(table)
        if alpha_img is not None:
            if image.mode in ("LA", "La"):
                image = image.convert("LA")
                image.putalpha(alpha_img)
            else:
                image = image.convert("RGBA")
                image.putalpha(alpha_img)
        return image
