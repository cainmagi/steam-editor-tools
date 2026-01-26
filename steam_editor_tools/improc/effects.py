# -*- coding: UTF-8 -*-
"""
Effects
=======
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
The effect handles. For each layer, each kind of effect is configured for no more
than once.
"""

import abc
import collections.abc
import math
import itertools

from typing import cast
from typing_extensions import Literal

from pydantic import BaseModel, Field

from PIL import Image
from PIL import ImageColor
from PIL import ImageFilter
from PIL import ImageChops

from .composer import ImageComposer, ImageComposerMode


__all__ = (
    "ImageEffectAbstract",
    "ImageEffectGlow",
    "ImageEffectStroke",
    "ImageEffectBevel",
)


def _cast_dilation(
    img_shape: Image.Image,
    color: str | tuple[float, ...],
    dil_size: int = 2,
    filter_size: int = 2,
):
    """(Private) Cast the dilation style to the given shape.

    This method accept the L-mode `img_shape` and return the styled `img`.
    """
    clr = ImageColor.getcolor(color, "RGBA")
    if isinstance(clr, int):
        clr = (clr, clr, clr, 255)
    if dil_size > 0:
        img_shape = img_shape.filter(ImageFilter.MaxFilter(dil_size * 2 + 1)).filter(
            ImageFilter.SMOOTH
        )
    img_shape = Image.composite(
        Image.new("RGBA", img_shape.size, color=clr),
        Image.new("RGBA", img_shape.size, color=(*clr[:3], 0)),
        img_shape,
    )
    if filter_size > 0:
        img_shape = img_shape.filter(ImageFilter.GaussianBlur(radius=filter_size))
    return img_shape


def _solve_quantile(
    img: Image.Image, low_q: float = 0.05, high_q: float = 0.95
) -> tuple[float, float]:
    """(Private) Solve the quantile value of a Pillow L-mode image using:

    * low_q quantile -> 0
    * high_q quantile -> 255

    The quantiles are solved by dividing the image into <128 and >128
    segements.
    """

    if img.mode != "L":
        img = img.convert("L")

    img_hist = img.histogram()

    sorted_px_lo = list(itertools.accumulate(img_hist[:128]))
    sorted_px_hi = list(itertools.accumulate(img_hist[128:]))
    n_lo = max(1, sorted_px_lo[-1])
    n_hi = max(1, sorted_px_hi[-1])
    idx_lo = len(
        tuple(itertools.takewhile(lambda val: val < (n_lo * low_q), sorted_px_lo))
    )
    idx_hi = len(
        tuple(itertools.takewhile(lambda val: val < (n_hi * high_q), sorted_px_hi))
    )
    lo = (
        (idx_lo - 1 + max(0, min(1, (n_lo * low_q) - sorted_px_lo[idx_lo - 1])))
        if idx_lo > 0
        else 0.0
    )
    hi = (
        (128 + idx_hi - 1 + max(0, min(1, (n_hi * high_q) - sorted_px_hi[idx_hi - 1])))
        if idx_hi > 0
        else 255.0
    )
    return lo, hi


def _normalize_threshold(
    img: Image.Image, lo_val: float = 5, hi_val: float = 245
) -> Image.Image:
    """(Private) Normalize a Pillow L-mode image using thresholding:

    * value < lo_val -> 0
    * value > hi_val -> 255

    Everything outside the range is clipped.
    """
    lo = lo_val
    hi = hi_val

    if hi <= lo:
        return img.copy()

    lut = []
    for v in range(128):
        if v <= lo:
            lut.append(0)
        else:
            norm = (v - lo) / float(128 - lo)
            lut.append(int(round(norm * 128)))
    for v in range(128, 256):
        if v >= hi:
            lut.append(255)
        else:
            norm = (v - 128) / float(hi - 128)
            lut.append(int(round(128 + norm * 127)))

    return img.point(lut)


class ImageEffectAbstract(BaseModel, abc.ABC):
    """The abstract image effect.

    Most properties are not implemented here.

    It is only used for providing the common logics of different effects.
    """

    @property
    def _mode_safe(self) -> ImageComposerMode:
        """(Private) Safe implementation of the field `self.mode`.

        If the subclasses do not provide `mode`, where return `"default"`.
        """
        if "mode" in self.__class__.model_fields:
            return getattr(self, "mode")
        else:
            return "default"

    @abc.abstractmethod
    def effect(self, image_fg: Image.Image) -> Image.Image | None:
        """Generate the effect image from the given image.

        Arguments
        ---------
        image_fg: `Image.Image`
            The image used for genereating this effect.

        Returns
        -------
        #1: `Image.Image | None`
            The generated effect image. This image should be `RGBA`, and the size
            can be different from the input image.

            This image should be center-aligned with the input `image_fg`.

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

        image_fg: `Image.Image`
            The image used for genereating this effect.

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
        image_fg: Image.Image,
        pos: tuple[int, int],
    ) -> Image.Image:
        """Render this effect.

        Arguments
        ---------
        comp: `ImageComposer`
            The composer that is used for merging images.

        image_bg: `Image.Image`
            The background image where the effect will be rendered. This image should
            be `RGB` or `RGBA`.

        image_fg: `Image.Image`
            The image used for genereating this effect.

        pos: `tuple[int, int]`
            The `(x, y)` position where the `image_fg` is placed on the `image_bg`.
            This position is the top-left corner of `image_fg`.

        Returns
        -------
        #1: `Image.Image`
            The `image_bg` with this effect image rendered on it.
        """
        image_eff = self.effect(image_fg)
        if image_eff is None:
            return image_bg
        pos_x = pos[0] - (image_eff.width - image_fg.width) // 2
        pos_y = pos[1] - (image_eff.height - image_fg.height) // 2
        # All boxes are LTRB.
        inner_box = (
            min(image_bg.width, max(0, pos_x)),
            min(image_bg.height, max(0, pos_y)),
            min(image_bg.width, max(0, pos_x + image_eff.width)),
            min(image_bg.height, max(pos_y + image_eff.height, 0)),
        )
        if inner_box[2] - inner_box[0] <= 0 or inner_box[3] - inner_box[1] <= 0:
            return image_bg
        outer_pos = (min(0, pos_x), min(0, pos_y))
        _image_bg = image_bg.crop(inner_box)
        _image_fg = Image.new("RGBA", _image_bg.size)
        _image_fg.paste(image_eff, outer_pos)
        res = self.compose(comp, image_bg=_image_bg, image_fg=_image_fg)
        image_bg = image_bg.copy()
        image_bg.paste(res, (inner_box[0], inner_box[1]))
        return image_bg


class ImageEffectGlow(ImageEffectAbstract):
    """The image effect: Glow

    Add the glowing effect to the alpha channel of the given image.
    """

    mode: ImageComposerMode = "screen"
    """The blending mode of the glowing effect."""

    type: Literal["glow"] = "glow"
    """The type code of this effect. It should not be modified."""

    size: int = Field(ge=0, default=8)
    """The size of the glowing light."""

    color: str | tuple[float, ...] = "#FFFFFF"
    """The RGB/RGBA color of the glowing light."""

    def effect(self, image_fg: Image.Image) -> Image.Image | None:
        if self.size <= 0:
            return None
        color = ImageColor.getcolor(self.color, "RGBA")
        if isinstance(color, int):
            color = (color, color, color, 255)
        glow_size = max(2, self.size)
        pad_size = glow_size * 3
        res = Image.new(
            mode="L",
            size=(image_fg.width + 2 * pad_size, image_fg.height + 2 * pad_size),
            color=0,
        )
        res.paste(image_fg.convert("RGBA").getchannel("A"), box=(pad_size, pad_size))
        img_glow = _cast_dilation(
            res,
            color=self.color,
            dil_size=glow_size,
            filter_size=glow_size,
        )
        return img_glow


class ImageEffectShadow(ImageEffectAbstract):
    """The image effect: Shadow

    Add the shadow effect to the alpha channel of the given image.
    """

    mode: ImageComposerMode = "multiply"
    """The blending mode of the shadow."""

    type: Literal["shadow"] = "shadow"
    """The type code of this effect. It should not be modified."""

    size: int = Field(ge=0, default=4)
    """The size of the shadow. This size can be viewed as "brush size" when
    creating the shadow.
    """

    offset: int = Field(ge=0, default=8)
    """The offset of the shadow. It represents the distance between the shadow and
    the image."""

    color: str | tuple[float, ...] = "#000000"
    """The RGB/RGBA color of the shadow."""

    def effect(self, image_fg: Image.Image) -> Image.Image | None:
        if self.size <= 0:
            return None
        color = ImageColor.getcolor(self.color, "RGBA")
        if isinstance(color, int):
            color = (color, color, color, 255)
        shadow_offset = max(4, self.offset)
        shadow_size = max(2, self.size)
        pad_size = shadow_offset * 2 + shadow_size * 3
        res = Image.new(
            mode="L",
            size=(image_fg.width + 2 * pad_size, image_fg.height + 2 * pad_size),
            color=0,
        )
        res.paste(
            image_fg.convert("RGBA").getchannel("A"),
            box=(pad_size + shadow_offset, pad_size + shadow_offset),
        )
        img_shadow = _cast_dilation(
            res,
            color=self.color,
            dil_size=shadow_size // 2,
            filter_size=shadow_size,
        )
        return img_shadow


class ImageEffectStroke(ImageEffectAbstract):
    """The image effect: Stroke

    Add the stroke effect to the alpha channel of the given image.
    """

    mode: ImageComposerMode = "default"
    """The blending mode of the stroke."""

    type: Literal["stroke"] = "stroke"
    """The type code of this effect. It should not be modified."""

    size: int = Field(ge=0, default=2)
    """The size of the stroke."""

    color: str | tuple[float, ...] = "#000000"
    """The RGB/RGBA color of the stroke."""

    def effect(self, image_fg: Image.Image) -> Image.Image | None:
        if self.size <= 0:
            return None
        color = ImageColor.getcolor(self.color, "RGBA")
        if isinstance(color, int):
            color = (color, color, color, 255)
        stroke_size = max(2, self.size)
        pad_size = stroke_size * 2
        res = Image.new(
            mode="L",
            size=(image_fg.width + 2 * pad_size, image_fg.height + 2 * pad_size),
            color=0,
        )
        res.paste(image_fg.convert("RGBA").getchannel("A"), box=(pad_size, pad_size))
        img_stroke = _cast_dilation(
            res, color=self.color, dil_size=stroke_size, filter_size=0
        )
        return img_stroke


class ImageEffectBevel(ImageEffectAbstract):
    """The image effect: Bevel

    Add the bevel effect to the alpha channel of the given image.

    The "bevel" effect here is a replica of the "Chisel Hard" effect.

    The algorithm is inspired by the following C++ implementation:
    https://dsp.stackexchange.com/a/533

    Different from the above OpenCV version, this effect is purely implemented by
    Pillow. In other words, we implement the following algorithm from scratch:
    1. Determine the binarized version of the alpha channel.
    2. Given a specific `max_distance` value, for each pixel inside the alpha
       shape, calculate the Euclidean distance between the pixel and the nearest
       edge pixel. The "nearest" means that the distance is the minimal value.
    3. Run a 3x3 "bevel" filter on the solved distance map.
    4. Run any post-processing (such as smoothing) if necessary.
    5. Split the grayscale bevel layer into the highlight and shadow layers, merge
       them into the original image, respectively.

    In this class, the "mode" is only referring to the mode of the highlight.
    The mode of the shadow is automatically chosen with respect to the highlight
    mode.

    The default algorithm used for solving the distance is based on
    Squared Euclidean Distance Transform (Felzenszwalb & Huttenlocher Algorithm)

    See
    https://cs.brown.edu/people/pfelzens/papers/seg-ijcv.pdf

    The distance is strictly Euclidean. We provide an approximated version of this
    distance. Use "gaussian" algorithm to enable it. This approximation is faster
    but does not work well on sharp edges.
    """

    mode: Literal["default", "screen", "lighter", "add"] = "default"
    """The blending mode of the bevel effect. This value is the blending mode
    of the highlight. The mode of the bevel shadow will be automatically
    chosen based on this value."""

    type: Literal["bevel"] = "bevel"
    """The type code of this effect. It should not be modified."""

    algorithm: Literal["euclidean", "gaussian"] = "euclidean"
    """The algorithm used for solving the chisel distance. The "eudlidean" mode is
    strict, while the "gaussian" mode is a fast approximation."""

    threshold: int = Field(ge=0, le=255, default=128)
    """A threshold in the range of 0~255. This value is used for determining the
    edge of the bevel effect."""

    max_distance: int = Field(ge=0, default=3)
    """The maximal distance when solving the depth of the bevel effect. When
    using "euclidean" algorithm, this value is strictly the same as the
    bevel depth."""

    smooth: float = Field(ge=0.0, default=1.0)
    """The size of the smoothing filter. The configuration `smooth=0` is
    equivalent to "Chisel Hard" effect."""

    opacity: int = Field(ge=0, le=100, default=75)
    """The opacity of the effect. It is in the range of 0~100."""

    @classmethod
    def _sedt_1d_list(cls, f: collections.abc.Sequence[float]) -> list[float]:
        """(Private) 1D Squared Euclidean Distance Transform
        (Felzenszwalb & Huttenlocher Algorithm)

        Arguments
        ---------
        f: `Sequence[float]`
            The `D(x, y)` list (0 for edge pixels, +inf for uncomputed
            distances, and others for the D(x, y) values specified by
            the last pass).

        Returns
        -------
        #1: `list[float]`
            The best squared distances.
        """
        n = len(f)
        d = [0.0] * n

        v = [0] * n  # locations of parabolas
        z = [0.0] * (n + 1)  # boundaries
        k = 0

        _neg_inf = float("-inf")
        _pos_inf = float("+inf")

        v[0] = 0
        z[0] = _neg_inf
        z[1] = _pos_inf

        for q in range(1, n):
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            while s <= z[k]:
                k -= 1
                s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2.0 * q - 2.0 * v[k])
            k += 1
            v[k] = q
            z[k] = s
            z[k + 1] = _pos_inf

        k = 0
        for q in range(n):
            while z[k + 1] < q:
                k += 1
            dq = q - v[k]
            d[q] = dq * dq + f[v[k]]

        return d

    @classmethod
    def _sedt_2d_list(
        cls, f2d: collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> list[list[float]]:
        """(Private) 2D Squared Euclidean Distance Transform
        (Felzenszwalb & Huttenlocher Algorithm)

        Arguments
        ---------
        f: `Sequence[Sequence[float]]`
            The edge mask list (2D list of floats (h x w), 0 for edge pixels,
            +inf for others).

        Returns
        -------
        #1: `list[list[float]]`
            The 2D list of best squared distances.
        """
        h = len(f2d)
        w = len(f2d[0]) if h > 0 else 0

        # Vertical pass
        tmp = [[0.0] * w for _ in range(h)]
        for x in range(w):
            col = [f2d[y][x] for y in range(h)]
            dcol = cls._sedt_1d_list(col)
            for y in range(h):
                tmp[y][x] = dcol[y]

        # Horizontal pass
        dist2 = [[0.0] * w for _ in range(h)]
        for y in range(h):
            row = tmp[y]
            drow = cls._sedt_1d_list(row)
            for x in range(w):
                dist2[y][x] = drow[x]

        return dist2

    def _solve_exact_euclidean_distmap(self, alpha: Image.Image) -> Image.Image:
        """(Private) Solve the exact Euclidean distance gradient map by
        Felzenszwalb & Huttenlocher Algorithm.

        Arguments
        ---------
        alpha: `Image.Image`
            L-mode image (alpha channel)

        Returns
        -------
        #1: `Image.Image`
            L-mode gradient image:
            - 255 at alpha outer edge
            - 255 outside alpha
            - 0 at distance >= `self.max_distance`
        """

        threshold = self.threshold
        max_distance = self.max_distance

        alpha = alpha.convert("L")
        w, h = alpha.size
        a_px = alpha.load()
        if a_px is None:
            raise ValueError("Cannot load the pixel view of the alpha channel.")

        # 1. Binarize alpha
        mask = [
            [1 if cast(float, a_px[x, y]) >= threshold else 0 for x in range(w)]
            for y in range(h)
        ]

        # 2. Detect outer edge: inside pixel with at least one neighbor outside
        edge = [[False] * w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                if mask[y][x] == 0:
                    continue
                is_edge = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if dx == 0 and dy == 0:
                            continue
                        if nx < 0 or nx >= w or ny < 0 or ny >= h:
                            is_edge = True
                        else:
                            if mask[ny][nx] == 0:
                                is_edge = True
                        if is_edge:
                            break
                    if is_edge:
                        break
                edge[y][x] = is_edge

        # 3. Build initial f(y,x): 0 for edge, +inf for others
        INF = 1e12
        f2d = [[0.0] * w for _ in range(h)]
        any_edge = False
        for y in range(h):
            for x in range(w):
                if edge[y][x]:
                    f2d[y][x] = 0.0
                    any_edge = True
                else:
                    f2d[y][x] = INF

        if not any_edge:
            return Image.new("L", (w, h), 0)

        # 4. Exact squared Euclidean distance transform
        dist2 = self._sedt_2d_list(f2d)

        # 5. Convert to true distance and normalize to 0..255
        grad_img = Image.new("L", (w, h), 0)
        g_px = grad_img.load()
        if g_px is None:
            raise ValueError("Cannot load the pixel view of grad_img.")

        for y in range(h):
            for x in range(w):
                if mask[y][x] == 0:
                    g_px[x, y] = 255
                    continue

                d2 = dist2[y][x]
                if d2 >= INF / 2:
                    g_px[x, y] = 0
                    continue

                d = math.sqrt(d2)
                if d >= max_distance:
                    val = 0
                else:
                    val = int(255 * (1.0 - d / max_distance))
                g_px[x, y] = max(0, min(255, val))

        return grad_img

    def _solve_approx_gaussian_distmap(self, alpha: Image.Image) -> Image.Image:
        """(Private) Solve the approximated distance gradient map by running a
        Gaussian filter.

        Arguments
        ---------
        alpha: `Image.Image`
            L-mode image (alpha channel)

        Returns
        -------
        #1: `Image.Image`
            L-mode gradient image:
            - 255 at alpha outer edge
            - 255 outside alpha
            - 0 at distance >= `self.max_distance`
        """
        threshold = self.threshold
        max_distance = self.max_distance

        table = tuple((0 if val >= threshold else 255) for val in range(256))
        bin_mask = alpha.point(table, mode="L")
        max_filter_size = max_distance // 2
        max_filter_size = max_filter_size + (1 if max_filter_size % 2 == 0 else 0)
        _bin_mask = bin_mask.filter(ImageFilter.MaxFilter(max_filter_size)).filter(
            ImageFilter.GaussianBlur(max_distance / 2)
        )
        bin_mask = ImageChops.lighter(bin_mask, _bin_mask)
        vmin, vmax = bin_mask.getextrema()
        if isinstance(vmin, collections.abc.Sequence):
            vmin = float(vmin[0])
        if isinstance(vmax, collections.abc.Sequence):
            vmax = float(vmax[0])

        def clip(val: float) -> float:
            return max(0, val - 0.1) / 0.9

        table = tuple((255 * clip(val / (vmax - vmin))) for val in range(256))
        bin_mask = bin_mask.point(table)
        return bin_mask

    def _distmap_to_bevel(
        self, gradient: Image.Image, alpha: Image.Image
    ) -> Image.Image:
        """Convert a distance map to the bevel layer.

        Arguments
        ---------
        gradient: `Image.Image`
            The distance gradient map provided by the algorithm.

        alpha: `Image.Image`
            The alpha channel of the gradient image area.

        Returns
        -------
        #1: `Image.Image`
            The bevel effect layer solved from `gradient`.
        """

        max_distance = self.max_distance

        k_value = (-3, -2, -1, 0, 0, -2, 1, 0, -3)
        k_avg = sum(k_value) / len(k_value)
        k_value = tuple((val - k_avg) for val in k_value)

        def get_scale(dist):
            """A guessed gradient scale. This scale is estimated for preventing
            the binary solution. The final scale is provided by the normalization.
            """
            if dist > 10:
                dist = 10 / dist
            elif dist > 5:
                dist = 5 / dist
            else:
                dist = 1
            return dist

        k_filter = ImageFilter.Kernel(
            (3, 3), k_value, scale=min(1, get_scale(max_distance)), offset=128
        )
        _gradient = Image.new("L", (gradient.width + 2, gradient.height + 2), "#FFFFFF")
        _gradient.paste(gradient, (1, 1))
        _gradient = _gradient.filter(k_filter)
        _gradient = _gradient.crop((1, 1, 1 + gradient.width, 1 + gradient.height))
        lo, hi = _solve_quantile(_gradient)
        if self.smooth >= 1e-3:
            _gradient = _gradient.filter(ImageFilter.GaussianBlur(self.smooth)).filter(
                ImageFilter.MedianFilter(3)
            )
            _gradient = ImageChops.composite(
                _gradient, Image.new("L", size=_gradient.size, color=128), alpha
            )
        _gradient = _normalize_threshold(_gradient, lo, hi)
        return _gradient

    def effect(self, image_fg: Image.Image) -> Image.Image | None:
        if self.max_distance <= 0 or self.opacity <= 0:
            return None
        if self.threshold == 0 or self.threshold == 255:
            return None
        alpha = image_fg.convert("RGBA").getchannel("A")
        if self.algorithm == "gaussian":
            gradient = self._solve_approx_gaussian_distmap(alpha)
        else:
            gradient = self._solve_exact_euclidean_distmap(alpha)
        bevel = self._distmap_to_bevel(gradient, alpha).convert("RGBA")
        bevel.putalpha(alpha)
        return bevel

    def compose(
        self, comp: ImageComposer, image_bg: Image.Image, image_fg: Image.Image
    ) -> Image.Image:
        mode = self.mode

        mode_bg = image_bg.mode
        alpha_fg = image_fg.getchannel("A")
        alpha_bg = (
            image_bg.getchannel("A")
            if ImageComposer._has_alpha_channel(image_bg)
            else None
        )
        image_bg = image_bg.convert("RGB")
        image_fg = image_fg.convert("L")

        opacity = self.opacity
        factor = opacity / 100 * 255 / 127
        if mode in ("add", "default"):
            table = tuple(
                round(factor * (255 - min(255, val + 128))) for val in range(256)
            )
            img_low = image_fg.point(table, mode="L")
        else:
            table = tuple(
                round(255 - factor * (255 - min(255, val + 128))) for val in range(256)
            )
            img_low = image_fg.point(table, mode="L")
        table = tuple(round(factor * max(0, val - 128)) for val in range(256))
        img_high = image_fg.point(table, mode="L")

        if mode == "default" and alpha_bg is not None:
            image_bg = image_bg.convert("RGBA")
            image_bg.putalpha(alpha_bg)
            _img_layer = Image.new("RGBA", size=image_bg.size, color="black")
            _img_layer.putalpha(ImageChops.multiply(img_low, alpha_fg))
            image_bg.alpha_composite(_img_layer)
            _img_layer = Image.new("RGBA", size=image_bg.size, color="white")
            _img_layer.putalpha(ImageChops.multiply(img_high, alpha_fg))
            image_bg.alpha_composite(_img_layer)
            return image_bg.convert(mode_bg)

        if mode == "add":
            _image_bg = ImageChops.add(
                ImageChops.subtract(image_bg, img_low.convert("RGB")),
                img_high.convert("RGB"),
            )
        elif mode == "screen":
            _image_bg = ImageChops.screen(
                ImageChops.multiply(image_bg, img_low.convert("RGB")),
                img_high.convert("RGB"),
            )
        elif mode == "lighter":
            _image_bg = ImageChops.lighter(
                ImageChops.darker(image_bg, img_low.convert("RGB")),
                img_high.convert("RGB"),
            )
        else:
            _image_bg = Image.composite(
                Image.new("RGB", size=image_bg.size, color="black"), image_bg, img_low
            )
            _image_bg = Image.composite(
                Image.new("RGB", size=image_bg.size, color="white"), _image_bg, img_high
            )

        image_bg = Image.composite(_image_bg, image_bg, alpha_fg)

        if alpha_bg is not None:
            image_bg = image_bg.convert("RGBA")
            image_bg.putalpha(alpha_bg)
        image_bg.convert(mode_bg)

        return image_bg
