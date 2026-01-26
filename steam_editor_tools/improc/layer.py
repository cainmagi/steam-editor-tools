# -*- coding: UTF-8 -*-
"""
Layer
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
Definition of the wrapped image layer.
"""

import collections
import collections.abc
import dataclasses

from typing_extensions import Literal, Protocol, Self, TypedDict

from PIL import Image
from PIL import ImageChops

from . import effects as _effects
from . import overlays as _overlays
from .composer import ImageComposer, ImageComposerMode
from .data import ImageAnchor, ImageFormat


__all__ = (
    "ImageLayerContentProtocol",
    "ImageLayerContainerProtocol",
    "ImageEffects",
    "ImageLayer",
)


class ImageLayerContentProtocol(Protocol):
    """The protocol of the image layer content."""

    @property
    def width(self) -> int:
        """Property: The width of the image."""
        ...

    @property
    def height(self) -> int:
        """Property: The width of the image."""
        ...

    @property
    def size(self) -> tuple[int, int]:
        """Property: The `(width, height)` tuple of the image."""
        ...

    @property
    def img(self) -> Image.Image:
        """Property: The accessible pixel-based image maintained by this instance."""
        ...

    def copy(self) -> Self:
        """Create a copy of this instance."""
        ...


class ImageLayerContainerProtocol(Protocol):
    """The protocol of the container that manages several `ImageLayer`s.

    The implementationof this protocol should be `renderer.ImageMultiLayer`.
    """

    @property
    def width(self) -> int:
        """Property: The width of the canvas."""
        ...

    @property
    def height(self) -> int:
        """Property: The width of the canvas."""
        ...

    @property
    def size(self) -> tuple[int, int]:
        """Property: The `(width, height)` tuple of the canvas."""
        ...

    @property
    def layers(self) -> "collections.OrderedDict[str, ImageLayer]":
        """Property: The internal storage of the layers managed by this
        container."""
        ...


@dataclasses.dataclass
class ImageEffects:
    """The image effects of a layer.

    The stack of the effects are ordered as:
    ```
    (bottom) -> (top)
    shadow -> glow -> stroke -> (bg replica) -> self -> overlays -> bevel
    ```
    """

    alpha: int = 100
    """The alpha value of the whole layer. This value will take effect for all
    applied effects."""

    alpha_content: int = 100
    """The alpha value of the image. This value will only take effects on the image
    but will not take effects on the applied effects."""

    blend: ImageComposerMode = "default"
    """The mode used for blending this image into the canvas."""

    stroke: _effects.ImageEffectStroke | None = None
    """The "stroke" effect of the layer. It works only when the image is RGBA."""

    glow: _effects.ImageEffectGlow | None = None
    """The "glowing" effect of the layer. It works only when the image is RGBA."""

    shadow: _effects.ImageEffectShadow | None = None
    """The "shadow/shade" effect of the layer. It works only when the image is RGBA."""

    bevel: _effects.ImageEffectBevel | None = None
    """The "bevel" effect of the layer. It works only when the image is RGBA."""

    overlays: list[_overlays.ImageOverlayAbstract] = dataclasses.field(
        default_factory=list
    )
    """The "overlaying" effect of the layer. It contains a series of overlaying
    operations. The top layers will be ordered later in this list."""


class ImageLayer:
    """A layer of image. It is typically used as a member of MultiLayerImage stack.

    All instance operations of this class are non-inplace.
    """

    __slots__ = (
        "parent",
        "name",
        "img",
        "anchor",
        "related_to",
        "rel_anchor",
        "pos_shift",
        "effects",
    )

    class _LayerPos(TypedDict):
        """(Private) Real position of an image layer."""

        pos: tuple[int, int]
        size: tuple[int, int]

    def __init__(
        self,
        parent: ImageLayerContainerProtocol,
        name: str,
        img: ImageLayerContentProtocol,
        anchor: str | ImageAnchor = ImageAnchor.center,
        related_to: str | None = None,
        rel_anchor: str | ImageAnchor = ImageAnchor.center,
        pos_shift: tuple[int, int] | None = None,
        effects: ImageEffects | None = None,
    ) -> None:
        """Initialization.

        In most cases, we do not instantiate this class explicitly. This
        instance shold be created by the methods like `ImageMultiLayer.add_image`.

        Arguments
        ---------
        parent: `ImageLayerContainerProtocol`
            The canvas, i.e. the container that manages several image layers.

            This layer is registered as a member of this container.

        name: `str`
            The name of this layer.

        img: `ImageLayerContentProtocol`
            The image instance maintained by this layer.

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

        effects: `ImageEffects | None`:
            The effects configured during the initialization. If not specified, will
            use an empty `ImageEffects` to configure this layer.
        """
        self.parent = parent
        """The canvas, i.e. the container that manages several image layers.

        This layer is registered as a member of this container."""

        name = str(name).strip()
        if not name:
            raise KeyError("The image layer name should not be empty.")
        self.name = name
        """The name of this layer."""

        self.img: ImageLayerContentProtocol = img
        """The image instance maintained by this layer."""

        self.anchor: ImageAnchor = ImageAnchor.from_str(anchor)
        """The anchor of this image."""

        self.related_to = (
            related_to.strip()
            if (isinstance(related_to, str) and related_to.strip())
            else None
        )
        """The name of another image layer. When rendering the image, will place
        this image based on the position of the image specified by `related_to`.
        """

        self.rel_anchor: ImageAnchor = ImageAnchor.from_str(rel_anchor)
        """The anchor of the reference image specified by `related_to` when placing
        this image."""

        self.pos_shift = pos_shift if pos_shift is not None else (0, 0)
        """The `(h_shift, v_shift)` of this image position."""

        self.effects = effects if isinstance(effects, ImageEffects) else ImageEffects()
        """The effects configured during the initialization."""

    @property
    def width(self) -> int:
        """Property: The width of the image."""
        return self.img.width

    @property
    def height(self) -> int:
        """Property: The height of the image."""
        return self.img.height

    @property
    def size(self) -> tuple[int, int]:
        """Property: The `(width, height)` of the image."""
        return self.img.size

    @property
    def fmt(self) -> ImageFormat:
        """Property: Attempt to get the image format from the content. If failed,
        return `ImageFormat.png`."""
        fmt = getattr(self.img, "fmt", None)
        if fmt is None or (not isinstance(fmt, ImageFormat)):
            return ImageFormat.png
        return fmt

    @property
    def related(self) -> "ImageLayer | ImageLayerContainerProtocol":
        """The instance of the `ImageLayer` that is specified by `self.related_to`.

        If `self.related_to` is None, return `self.parent` (canvas).
        """
        return (
            self.parent.layers[self.related_to]
            if self.related_to is not None
            else self.parent
        )

    @property
    def alpha(self) -> Image.Image | None:
        """Property: Get the alpha channel of this layer. It is equivalent to
        ```
        self.img.img.getchannel("A")
        ```
        The returned image is in the L mode.

        If the image does not contain the alpha channel, will return `None`.
        """
        img = self.img.img
        if not ImageComposer._has_alpha_channel(img):
            return None
        return img.getchannel("A")

    def copy(self) -> Self:
        """Get a copy of this instance."""
        return self.__class__(
            parent=self.parent,
            img=self.img.copy(),
            name=self.name,
            anchor=self.anchor,
            related_to=self.related_to,
            rel_anchor=self.rel_anchor,
            pos_shift=self.pos_shift,
        )

    def del_shadow(self) -> None:
        """Delete the shadow effect of this layer."""
        self.effects.shadow = None

    def set_shadow(
        self,
        mode: ImageComposerMode = "multiply",
        size: int = 4,
        offset: int = 8,
        color: str | tuple[float, ...] = "#000000",
    ) -> None:
        """Set the shadow effect of this layer.

        Arguments
        ---------
        mode: `ImageComposerMode`
            The blending mode of the shadow.

        size: `int`
            The size of the shadow. This size can be viewed as "brush size" when
            creating the shadow.

        offset: `int`
            The offset of the shadow. It represents the distance between the shadow
            and the image.

        color: `str | tuple[float, ...]`
            The RGB/RGBA color of the shadow.
        """
        self.effects.shadow = _effects.ImageEffectShadow(
            mode=mode, size=size, offset=offset, color=color
        )

    def del_glow(self) -> None:
        """Delete the glowing effect of this layer."""
        self.effects.glow = None

    def set_glow(
        self,
        mode: ImageComposerMode = "screen",
        size: int = 8,
        color: str | tuple[float, ...] = "#FFFFFF",
    ) -> None:
        """Set the glowing effect of this layer.

        Arguments
        ---------
        mode: `ImageComposerMode`
            The blending mode of the glowing light.

        size: `int`
            The size of the glowing light. This size can be viewed as "brush size"
            when creating the glowing light.

        color: `str | tuple[float, ...]`
            The RGB/RGBA color of the glowing light.
        """
        self.effects.glow = _effects.ImageEffectGlow(mode=mode, size=size, color=color)

    def del_stroke(self) -> None:
        """Delete the glowing effect of this layer."""
        self.effects.stroke = None

    def set_stroke(
        self,
        mode: ImageComposerMode = "default",
        size: int = 2,
        color: str | tuple[float, ...] = "#000000",
    ) -> None:
        """Set the glowing effect of this layer.

        Arguments
        ---------
        mode: `ImageComposerMode`
            The blending mode of the stroke.

        size: `int`
            The size of the stroke. This size can be viewed as stroke width.

        color: `str | tuple[float, ...]`
            The RGB/RGBA color of the stroke.
        """
        self.effects.stroke = _effects.ImageEffectStroke(
            mode=mode, size=size, color=color
        )

    def del_bevel(self) -> None:
        """Delete the bevel effect of this layer."""
        self.effects.bevel = None

    def set_bevel(
        self,
        mode: Literal["default", "screen", "lighter", "add"] = "default",
        algorithm: Literal["euclidean", "gaussian"] = "euclidean",
        threshold: int = 128,
        max_distance: int = 3,
        smooth: float = 1.0,
        opacity: int = 75,
    ) -> None:
        """Set the glowing effect of this layer.

        Arguments
        ---------
        mode: `"default" | "screen" | "lighter" | "add"`
            The blending mode of the bevel effect. This value is the blending mode
            of the highlight. The mode of the bevel shadow will be automatically
            chosen based on this value.

        algorithm: `"euclidean" | "gaussian"`
            The algorithm used for solving the chisel distance. The "eudlidean" mode
            is strict, while the "gaussian" mode is a fast approximation.

        threshold: `int`
            A threshold in the range of 0~255. This value is used for determining the
            edge of the bevel effect.

        max_distance: `int`
            The maximal distance when solving the depth of the bevel effect. When
            using "euclidean" algorithm, this value is strictly the same as the
            bevel depth.

        smooth: `float`
            The size of the smoothing filter. The configuration `smooth=0` is
            equivalent to "Chisel Hard" effect.

        opacity: `int`
            The opacity of the effect. It is in the range of 0~100.
        """
        self.effects.bevel = _effects.ImageEffectBevel(
            mode=mode,
            algorithm=algorithm,
            threshold=threshold,
            max_distance=max_distance,
            smooth=smooth,
            opacity=opacity,
        )

    def delete_overlays(self) -> None:
        """Delete all overlay effects. This method is equivalent to
        ``` python
        self.effects.overlays.clear()
        ```
        """
        self.effects.overlays.clear()

    def add_overlay_color(
        self,
        color: str | tuple[float, ...],
        mode: ImageComposerMode = "default",
        pos_shift: tuple[int, int] = (0, 0),
    ) -> None:
        """Add a pure-color overlaying layer to the current layer.

        Arguments
        ---------
        color: `str | tuple[float, ...]`
            The RGB/RGBA color of the overlaying layer.

        mode: `ImageComposerMode`
            The blending mode of the overlaying effect.

        pos_shift: `tuple[int, int]`
            The shift of the overlaying content. By default, the content will be
            center-aligned with the giving shape. The overlaying content that is
            outside the shape mask will be cut off.
        """
        self.effects.overlays.append(
            _overlays.ImageOverlayColor(mode=mode, color=color, pos_shift=pos_shift)
        )

    def add_overlay_gradient(
        self,
        color_a: str | tuple[float, ...],
        color_b: str | tuple[float, ...],
        mode: ImageComposerMode = "default",
        size: tuple[int | None, int | None] | None = None,
        direction: Literal[
            "left_to_right",
            "top_to_bottom",
            "rect_center_to_outside",
            "radius_center_to_outside",
        ] = "left_to_right",
        pos_shift: tuple[int, int] = (0, 0),
    ) -> None:
        """Add a linear-gradient overlaying layer to the current layer.

        Arguments
        ---------
        color_a: `str | tuple[float, ...]`
            The starting RGB/RGBA color of the overlaying layer.

        color_b: `str | tuple[float, ...]`
            The ending RGB/RGBA color of the overlaying layer.

        mode: `ImageComposerMode`
            The blending mode of the overlaying effect.

        size: `tuple[int | None, int | None] | None`
            The size of the gradient. If not specified, will use the layer size.

        direction: selected from
            - `"left_to_right"`
            - `"top_to_bottom"`
            - `"rect_center_to_outside"`
            - `"radius_center_to_outside"`

            The gradient direction. The value means the direction from `color_a` to
            `color_b`.

        pos_shift: `tuple[int, int]`
            The shift of the overlaying content. By default, the content will be
            center-aligned with the giving shape. The overlaying content that is
            outside the shape mask will be cut off.
        """
        self.effects.overlays.append(
            _overlays.ImageOverlayGradient(
                mode=mode,
                color_a=color_a,
                color_b=color_b,
                size=size,
                direction=direction,
                pos_shift=pos_shift,
            )
        )

    def add_overlay_image(
        self,
        image: Image.Image,
        mode: ImageComposerMode = "default",
        size: tuple[int | None, int | None] | None = None,
        feather_depth: int = 0,
        pos_shift: tuple[int, int] = (0, 0),
    ) -> None:
        """Add an image-based overlaying layer to the current layer.

        Arguments
        ---------
        image: `Image.Image`
            The image filled as the overlaying layer.

        mode: `ImageComposerMode`
            The blending mode of the overlaying effect.

        size: `tuple[int | None, int | None] | None`
            The size of the image. If not specified, will use the layer size.

            If at least one of the size is not specified, will attempt to resize the
            image while preserving the ratio.

        feather_depth: `int`
            Whether to apply feathering edge mask to the image. If this value
            is 0, will use the image as it is.

        pos_shift: `tuple[int, int]`
            The shift of the overlaying content. By default, the content will be
            center-aligned with the giving shape. The overlaying content that is
            outside the shape mask will be cut off.
        """
        self.effects.overlays.append(
            _overlays.ImageOverlayImage(
                mode=mode,
                image=image,
                size=size,
                feather_depth=feather_depth,
                pos_shift=pos_shift,
            )
        )

    def get_pos_abs(
        self, cache: collections.abc.MutableMapping[str, _LayerPos] | None = None
    ) -> _LayerPos:
        """Get the absolute position of this layer.

        Arguments
        ---------
        cache: `dict[str, _LayerPos] | None`
            The cache used for accelerating the position locating. Typically, this
            value is maintained in the container when rendering all layers.

            If not specified, will not benefit from acceleration.

        Returns
        -------
        #1: `{pos: tuple[int, int], size: tuple[int, int]}`
            The position of the top left corner (anchor), and the `(width, height)`
            of this layer.
        """
        name = self.name
        if cache is not None and name in cache:
            return cache[name]
        rel_to = self.related_to
        anchor = self.anchor.value
        rel_anchor = self.rel_anchor.value
        if rel_to is None:  # Related to container
            boundary_l = 0
            boundary_r = self.parent.width
            boundary_t = 0
            boundary_b = self.parent.height
        else:
            rel_lp = self.parent.layers[rel_to].get_pos_abs(cache)
            boundary_l = rel_lp["pos"][0]
            boundary_r = boundary_l + rel_lp["size"][0]
            boundary_t = rel_lp["pos"][1]
            boundary_b = boundary_t + rel_lp["size"][1]
        # Solve horizontal position.
        if "left" in rel_anchor:
            _pos_rel_l = boundary_l
        elif "right" in rel_anchor:
            _pos_rel_l = boundary_r
        else:
            _pos_rel_l = (boundary_l + boundary_r) // 2
        if "left" in anchor:
            _pos_l = _pos_rel_l
        elif "right" in anchor:
            _pos_l = _pos_rel_l - self.width
        else:
            _pos_l = _pos_rel_l - (self.width // 2)
        # Solve vertical position.
        if "top" in rel_anchor:
            _pos_rel_t = boundary_t
        elif "bottom" in rel_anchor:
            _pos_rel_t = boundary_b
        else:
            _pos_rel_t = (boundary_t + boundary_b) // 2
        if "top" in anchor:
            _pos_t = _pos_rel_t
        elif "bottom" in anchor:
            _pos_t = _pos_rel_t - self.height
        else:
            _pos_t = _pos_rel_t - (self.height // 2)
        _pos = self._LayerPos(
            pos=(_pos_l + self.pos_shift[0], _pos_t + self.pos_shift[1]),
            size=(self.width, self.height),
        )
        if cache is not None:
            cache[name] = _pos
        return _pos

    def render(
        self,
        comp: ImageComposer,
        image_bg: Image.Image,
        cache: collections.abc.MutableMapping[str, _LayerPos] | None = None,
    ) -> Image.Image:
        """Render this layer.

        Arguments
        ---------
        comp: `ImageComposer`
            The composer that is used for merging images.

        image_bg: `Image.Image`
            The background image where this layer will be rendered on.
            This image should be `RGB` or `RGBA`.

        cache: `dict[str, _LayerPos] | None`
            The cache used for accelerating the position locating. Typically, this
            value is maintained in the container when rendering all layers.

            If not specified, will not benefit from acceleration.

        Returns
        -------
        #1: `Image.Image`
            The `image_bg` with this layer rendered on it.
        """
        img = self.img.img
        pos = self.get_pos_abs(cache)
        alpha = self.alpha
        # Early stop if the overall alpha value is 0.
        val_alpha = min(100, max(0, self.effects.alpha))
        if val_alpha == 0:
            return image_bg
        # Three styling layers under the current layer.
        # Will not render the following three layers if the current layer does
        # not have an alpha channel.
        img_cur = image_bg
        for effect in (self.effects.shadow, self.effects.glow, self.effects.stroke):
            if effect is None:
                continue
            img_cur = effect.render(
                comp, image_bg=img_cur, image_fg=img, pos=pos["pos"]
            )
        # Add the "bg replica layer"
        _alpha = Image.new("L", size=image_bg.size, color=0)
        _alpha.paste(
            alpha if alpha is not None else Image.new("L", img.size, color=255),
            pos["pos"],
        )
        img_cur = ImageChops.composite(image_bg, img_cur, _alpha)
        # Add self
        val_alpha_content = min(100, max(0, self.effects.alpha_content))
        if val_alpha_content == 100:
            _img = Image.new("RGBA", size=image_bg.size, color="#00000000")
            _img.paste(img, pos["pos"])
            img_cur = comp.by_name(self.effects.blend)(img_cur, _img)
        elif val_alpha_content > 0:
            _alpha_val = min(255, max(0, round(val_alpha_content / 100 * 255)))
            if alpha is not None:
                table = tuple(
                    min(255, max(0, round(val * (val_alpha_content / 100))))
                    for val in range(256)
                )
                _alpha = alpha.point(table)
            else:
                _alpha = Image.new("L", img.size, color=_alpha_val)
            _img = img.convert("RGBA")
            _img.putalpha(_alpha)
            img_cur = comp.by_name(self.effects.blend)(img_cur, _img)
        # Add overlays
        _alpha = alpha if alpha is not None else Image.new("L", img.size, color=255)
        for effect in self.effects.overlays:
            img_cur = effect.render(
                comp, image_bg=img_cur, shape=_alpha, pos=pos["pos"]
            )
        # Add bevel
        effect = self.effects.bevel
        if effect is not None:
            img_cur = effect.render(
                comp, image_bg=img_cur, image_fg=img, pos=pos["pos"]
            )
        # Merge overall alpha
        if val_alpha == 100:
            return img_cur
        return Image.blend(image_bg, img_cur, val_alpha / 100)
