# -*- coding: UTF-8 -*-
"""
Overlays
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
The overlay effect handles. Provide the solutions of covering the a layer with
colors, gradients, or images.
"""

import abc
import collections.abc
import math
import itertools

from typing_extensions import Literal

import dataclasses

from PIL import Image
from PIL import ImageColor
from PIL import ImageChops

from .composer import ImageComposer, ImageComposerMode


__all__ = (
    "ImageOverlayAbstract",
    "ImageOverlayColor",
    "ImageOverlayGradient",
    "ImageOverlayImage",
)


def _get_color(
    color: str | tuple[float, ...], alpha: int | None = None
) -> tuple[int, ...]:
    """Get the normalized color value.

    Arguments
    ---------
    color: `str | tuple[float, ....]`
        A PIL color argument.

    alpha: `int | None`
        The alpha value in the range of 0~100.

        If not specified, will return the normalized color without reset the alpha
        value.

    Returns
    -------
    #1: `tuple[int, int, int] | tuple[int, int, int, int]`
        The normalized color. Will be an RGB color if `alpha=100`. Otherwise, will be
        an RGBA color.
    """
    _color = ImageColor.getcolor(color, "RGBA")
    if not isinstance(_color, collections.abc.Sequence):
        _color = (_color, _color, _color, 255)
    if alpha is None:
        return _color
    if alpha < 100:
        _color = (*_color[:3], max(0, min(255, round(alpha / 100 * 255))))
    else:
        _color = _color[:3]
    return _color


def _feather_mask_rect(size: tuple[int, int], depth: int) -> Image.Image:
    """Create an L-mode alpha mask for a rectangular feather mask image.

    The feather effect is calculated by L-inf norm.

    Arguments
    ---------
    size: `tuple[int, int]`
        The mask image size `(h, w)`.

    depth: `int`
        The feather depth.
        * Pixels at the edge have `alpha=0`.
        * Pixels with L-inf distance `>= depth` have `alpha=255`.

    Returns
    -------
    #1: `Image.Image`
        An L-mode image containing a rectangular feather mask (soft edge).
    """
    width, height = size
    mask = Image.new("L", size, color=255)
    px = mask.load()
    if px is None:
        raise ValueError("Cannot access the mask image pixels.")

    for y, x in itertools.product(range(height), range(width)):
        dist = min(x, y, width - 1 - x, height - 1 - y)

        if dist >= depth:
            continue
        elif dist <= 0:
            a = 0
        else:
            a = int(255 * (dist / depth))

        px[x, y] = a

    return mask


@dataclasses.dataclass
class ImageOverlayAbstract(abc.ABC):
    """The abstract image overlay.

    Most properties are not implemented here.

    It is only used for providing the common logics of different effects.
    """

    @property
    def _mode_safe(self) -> ImageComposerMode:
        """(Private) Safe implementation of the field `self.mode`.

        If the subclasses do not provide `mode`, where return `"default"`.
        """
        if "mode" in set(field.name for field in dataclasses.fields(self)):
            return getattr(self, "mode")
        else:
            return "default"

    @property
    def _pos_shift_safe(self) -> tuple[int, int]:
        """(Private) Safe implementation of the field `self.pos_shift`.

        If the subclasses do not provide `pos_shift`, where return `(0, 0)`.
        """
        if "pos_shift" in set(field.name for field in dataclasses.fields(self)):
            return getattr(self, "pos_shift")
        else:
            return (0, 0)

    @property
    def intermediate_bg_color(self) -> str | tuple[float, ...]:
        """Property: The intermediate background color. This value may be used
        when the layer content needs to be rescale."""
        return "#00000000"

    @abc.abstractmethod
    def overlay(self, shape: Image.Image) -> Image.Image | None:
        """Generate the overlay image from the given image.

        Arguments
        ---------
        shape: `Image.Image`
            An `L` type image defining the shape of the overlay. This value is
            provided when rendering the overlaying effect.

        Returns
        -------
        #1: `Image.Image | None`
            The generated overlay image. This image can be not `RGBA`, but will
            be automatically converted to `RGBA` by applying the `self.shape` as
            the alpha channel. The size can be different from the input image.
            However, in most cases, this size should be the same as `self.shape`.

            This image should be center-aligned with the input `self.shape`.

            Will return `None` if the effect should be skipped.
        """
        raise NotImplementedError

    def compose(
        self,
        comp: ImageComposer,
        image_bg: Image.Image,
        image_fg: Image.Image,
    ) -> Image.Image:
        """Compose the background and foreground images.

        This method do not need to be overriden unless the subclass needs to change
        the behavior of image blending.

        Arguments
        ---------
        comp: `ImageComposer`
            The composer that is used for merging images.

        image_bg: `Image.Image`
            The background image where the effect will be rendered. This image should
            be `RGB` or `RGBA`.

        Returns
        -------
        #1: `Image.Image`
            The composed image.
        """
        return comp.by_name(self._mode_safe)(image_bg, image_fg)

    def render(
        self,
        comp: ImageComposer,
        image_bg: Image.Image,
        shape: Image.Image,
        pos: tuple[int, int],
    ) -> Image.Image:
        """Render this overlay effect.

        Arguments
        ---------
        comp: `ImageComposer`
            The composer that is used for merging images.

        image_bg: `Image.Image`
            The background image where the overlay image will be rendered. This image
            should be `RGB` or `RGBA`.

        shape: `Image.Image`
            An `L` type image defining the shape of the overlay. This value can be
            provided by the alpha channel of an image.

        pos: `tuple[int, int]`
            The position shift of the shape. This position means the top left corner
            of the given shape.

            This value should be `(0, 0)` if the given shape has the same size of the
            background.

        Returns
        -------
        #1: `Image.Image`
            The `image_bg` with this effect image rendered on it.
        """
        image_eff = self.overlay(shape=shape)
        if image_eff is None:
            return image_bg

        # Put image_eff on shape
        _pos_shift = self._pos_shift_safe
        pos_x = _pos_shift[0] + (shape.width - image_eff.width) // 2
        pos_y = _pos_shift[1] + (shape.height - image_eff.height) // 2
        image_eff = image_eff.convert("RGBA")
        _image_eff = Image.new("RGBA", shape.size)
        _image_eff.paste(image_eff, (pos_x, pos_y))
        _image_eff = Image.alpha_composite(
            Image.new("RGBA", shape.size, color=self.intermediate_bg_color),
            _image_eff,
        )
        _image_eff.putalpha(ImageChops.multiply(_image_eff.getchannel("A"), shape))

        # Put shape on foreground
        pos_x = pos[0]
        pos_y = pos[1]
        inner_box = (
            min(image_bg.width, max(0, pos_x)),
            min(image_bg.height, max(0, pos_y)),
            min(image_bg.width, max(0, pos_x + _image_eff.width)),
            min(image_bg.height, max(pos_y + _image_eff.height, 0)),
        )
        if inner_box[2] - inner_box[0] <= 0 or inner_box[3] - inner_box[1] <= 0:
            return image_bg
        outer_pos = (min(0, pos_x), min(0, pos_y))
        _image_bg = image_bg.crop(inner_box)
        _image_fg = Image.new("RGBA", _image_bg.size)
        _image_fg.paste(_image_eff, outer_pos)

        # Blend background.
        res = self.compose(comp, image_bg=_image_bg, image_fg=_image_fg)
        image_bg = image_bg.copy()
        image_bg.paste(res, (inner_box[0], inner_box[1]))
        return image_bg


@dataclasses.dataclass
class ImageOverlayColor(ImageOverlayAbstract):
    """An overlay layer with a pure color."""

    color: str | tuple[float, ...]
    """The RGB/RGBA color of the overlaying layer."""

    pos_shift: tuple[int, int] = (0, 0)
    """The shift of the overlaying content. By default, the content will be center-
    aligned with the giving shape. The overlaying content that is outside the
    shape mask will be cut off."""

    mode: ImageComposerMode = "default"
    """The blender mode of the overlaying effect."""

    @property
    def intermediate_bg_color(self) -> str | tuple[float, ...]:
        return self.color

    def overlay(self, shape: Image.Image) -> Image.Image | None:
        return Image.new(mode="RGBA", size=shape.size, color=_get_color(self.color))


@dataclasses.dataclass
class ImageOverlayGradient(ImageOverlayAbstract):
    """An overlay layer with a linear gradient."""

    color_a: str | tuple[float, ...]
    """The starting RGB/RGBA color of the overlaying layer."""

    color_b: str | tuple[float, ...]
    """The ending RGB/RGBA color of the overlaying layer."""

    size: tuple[int | None, int | None] | None = None
    """The size of the gradient. If not specified, will use the layer size."""

    direction: Literal[
        "left_to_right",
        "top_to_bottom",
        "rect_center_to_outside",
        "radius_center_to_outside",
    ] = "left_to_right"
    """The gradient direction. The value means the direction from `color_a` to
    `color_b`."""

    pos_shift: tuple[int, int] = (0, 0)
    """The shift of the overlaying content. By default, the content will be center-
    aligned with the giving shape. The overlaying content that is outside the
    shape mask will be cut off."""

    mode: ImageComposerMode = "default"
    """The blender mode of the overlaying effect."""

    @property
    def intermediate_bg_color(self) -> str | tuple[float, ...]:
        return self.color_b

    def overlay(self, shape: Image.Image) -> Image.Image | None:
        color_a = _get_color(self.color_a)
        color_b = _get_color(self.color_b)
        if self.direction == "left_to_right":
            grad_shape = Image.linear_gradient("L").transpose(Image.Transpose.ROTATE_90)
        elif self.direction == "top_to_bottom":
            grad_shape = Image.linear_gradient("L")
        elif self.direction == "rect_center_to_outside":
            _grad = Image.linear_gradient("L").transpose(Image.Transpose.ROTATE_180)
            grad_shape = Image.new("L", (_grad.width, _grad.height * 2), 0)
            grad_shape.paste(_grad, (0, 0))
            grad_shape.paste(
                _grad.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, _grad.height)
            )
            _pre_size = max(_grad.width, _grad.height * 2)
            grad_shape = grad_shape.resize((_pre_size, _pre_size))
            grad_shape = ImageChops.lighter(
                grad_shape, grad_shape.transpose(Image.Transpose.ROTATE_90)
            )
        elif self.direction == "radius_center_to_outside":
            _grad = Image.radial_gradient("L")
            cap_val = 255 / math.sqrt(2)
            table = tuple(
                255 - min(255, (255 / cap_val) * max(0, cap_val - val))
                for val in range(256)
            )
            grad_shape = _grad.point(table, "L")
        else:
            grad_shape = Image.linear_gradient("L").transpose(Image.Transpose.ROTATE_90)
        if self.size is None:
            _size = shape.size
        else:
            _size = (
                shape.size[0] if self.size[0] is None else self.size[0],
                shape.size[1] if self.size[1] is None else self.size[1],
            )
        grad_shape = grad_shape.resize(_size)
        return Image.composite(
            Image.new("RGBA", size=_size, color=color_b),
            Image.new("RGBA", size=_size, color=color_a),
            grad_shape,
        )


@dataclasses.dataclass
class ImageOverlayImage(ImageOverlayAbstract):
    """An overlay layer with a linear gradient."""

    image: Image.Image
    """The image filled as the overlaying layer."""

    size: tuple[int | None, int | None] | None = None
    """The size of the image. If not specified, will use the layer size.

    If at least one of the size is not specified, will attempt to resize the
    image while preserving the ratio.
    """

    feather_depth: int = 0
    """Whether to apply feathering edge mask to the image. If this value
    is 0, will use the image as it is."""

    pos_shift: tuple[int, int] = (0, 0)
    """The shift of the overlaying content. By default, the content will be center-
    aligned with the giving shape. The overlaying content that is outside the
    shape mask will be cut off."""

    mode: ImageComposerMode = "default"
    """The blender mode of the overlaying effect."""

    def overlay(self, shape: Image.Image) -> Image.Image | None:
        img_width, img_height = self.image.size
        ratio = img_height / img_width
        width, height = (None, None) if self.size is None else self.size
        if width is None:
            if height is None:
                width = min(shape.width, max(1, round(shape.height / ratio)))
                height = max(1, round(width * ratio))
            else:
                width = max(1, round(height / ratio))
        elif height is None:
            height = max(1, round(width * ratio))
        image = self.image.resize((width, height)).convert("RGBA")
        if self.feather_depth > 0:
            mask = _feather_mask_rect(image.size, depth=self.feather_depth)
            image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
        return image
