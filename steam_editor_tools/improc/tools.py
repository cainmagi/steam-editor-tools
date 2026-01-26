# -*- coding: UTF-8 -*-
"""
Tools
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
Extra tools for processing images.
"""

import os
import logging
import collections.abc
import inspect
import functools

from typing import Any
from typing_extensions import Literal, Protocol, overload

from PIL import Image

from .data import ImageQuality, ImageFormat
from .renderer import ImageSingle, ImageMultiLayer


__all__ = ("batch_process_images", "ImageGrids")

log = logging.getLogger("steam_editor_tools")


def batch_process_images(
    processor: collections.abc.Callable[[ImageSingle], ImageSingle],
    folder_path: "str | os.PathLike[str]",
    out_folder_path: "str | os.PathLike[str] | None" = None,
    out_file_name_prefix: str | None = None,
    verbose: bool = False,
) -> None:
    """Run batch processing for a group of images, and save the processed images as
    Steam screenshots.

    Arguments
    ---------
    processor: `(ImageSingle) -> ImageSingle`
        The processor where the input and output are loaded image and the processed
        image, respectively.

    folder_path: `str | PathLike[str]`
        The path to the folder where the input images are stored. The image files
        with `jpg`, `jpeg`, `png`, or `webp` will be loaded.

    out_folder_path: `str | PathLike[str] | None`
        The folder where the output images are saved. If not specified, will use
        `<folder_path>/out` as this value.

    out_file_name_prefix: `str | None`
        The prefix prepended to the output image file names. If not specified, will
        not add name prefix.

    verbose: `bool`
        A flag. If specified, will display the processing progress.
    """
    folder_path = str(folder_path)
    if out_folder_path is None:
        out_folder_path = os.path.join(folder_path, "out")
    else:
        out_folder_path = str(out_folder_path)
    for finfo in os.scandir(folder_path):
        if not (
            finfo.is_file()
            and os.path.splitext(finfo)[-1].strip().casefold().lstrip(".").strip()
            in ("jpg", "jpeg", "png", "webp")
        ):
            continue
        if verbose:
            log.info("Processing: {0}".format(finfo.name))
        out_file_name = os.path.splitext(finfo.name)[0].strip() + ".jpg"
        if out_file_name_prefix:
            out_file_name = "{0}-{1}".format(out_file_name_prefix, out_file_name)
        processor(ImageSingle(finfo.path)).save_steam_screenshot(
            out_folder_path, out_file_name, quality=ImageQuality.medium
        )


class ImageGrids:
    """The tool used for creating grided images.

    Its design is similar to matplotlib's subplots.
    """

    class ImageProtocol(Protocol):
        """The protocol of insertable images."""

        @property
        def width(self) -> int: ...

        @property
        def height(self) -> int: ...

        @property
        def size(self) -> tuple[int, int]: ...

        @property
        def img(self) -> Image.Image: ...

    @overload
    def __init__(
        self,
        n_cols: int,
        *,
        width: int = 1024,
        margins: tuple[int, int] = (0, 0),
        gaps: tuple[int, int] = (0, 0),
        bg_color: str | tuple[float, ...] | None = None,
        fmt: str | ImageFormat = "png",
    ) -> None: ...

    @overload
    def __init__(
        self,
        n_rows: int,
        *,
        height: int = 1024,
        margins: tuple[int, int] = (0, 0),
        gaps: tuple[int, int] = (0, 0),
        bg_color: str | tuple[float, ...] | None = None,
        fmt: str | ImageFormat = "png",
    ) -> None: ...

    @overload
    def __init__(
        self,
        n_rows: int,
        n_cols: int,
        *,
        width: int = 1024,
        height: int = 1024,
        margins: tuple[int, int] = (0, 0),
        gaps: tuple[int, int] = (0, 0),
        bg_color: str | tuple[float, ...] | None = None,
        fmt: str | ImageFormat = "png",
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialization.

        Arguments (version 1)
        =====================
        n_rows: `int`
            The number of rows in the grid.

        height: `int`
            The height of the image. This height will be uniformly divided according
            to `n_rows`.

        Arguments (version 2)
        =====================
        n_cols: `int`
            The number of rows in the grid.

        width: `int`
            The width of the image. This width will be uniformly divided according
            to `n_cols`.

        Arguments (version 3)
        =====================
        n_rows: `int`
        n_cols: `int`
            When both rows and cols are specified, this container will has a number
            limit of specified figures.

        width: `int`
        height: `int`
            The size of the image. The width and height will be uniformly divided.

        Arguments shared (kwargs only)
        ==============================
        margins: `tuple[int, int]`
            The `(horizontal_margin, vertical_margin)` padded to the image.

        gaps: `tuple[int, int]`
            The `(x_gap, y_gap)` defining the separations among images.

        bg_color: `str | tuple[float, ...] | None`
            The background color of the whole image. If this value is `None`,
            will use transparent background.

        fmt: `str | ImageFormat | None`
            The format of the image. It is used only when saving this image.
        """

        self.__row_lim: int = 0
        self.__col_lim: int = 0
        self.__width_lim: int = 0
        self.__height_lim: int = 0
        margins = kwargs.pop("margins", (0, 0))
        if not isinstance(margins, collections.abc.Sequence):
            raise TypeError(
                'The argument "margins" is not correct: {0}'.format(margins)
            )
        self.__margins: tuple[int, int] = (margins[0], margins[1])

        gaps = kwargs.pop("gaps", (0, 0))
        if not isinstance(gaps, collections.abc.Sequence):
            raise TypeError('The argument "gaps" is not correct: {0}'.format(gaps))
        self.__gaps: tuple[int, int] = (gaps[0], gaps[1])

        self.__color: str | tuple[float, ...] | None = kwargs.pop("bg_color", None)
        self.__fmt: ImageFormat = ImageFormat.from_str(kwargs.pop("fmt", "png"))
        self.__mode: Literal["col", "row", "both"] = "both"

        self.__store: dict[int, ImageGrids.ImageProtocol] = dict()

        def init_col_specified(n_cols: int, *, width: int = 1024) -> None:
            self.__col_lim = n_cols
            self.__width_lim = width
            self.__mode = "col"

        def init_row_specified(n_rows: int, *, height: int = 1024) -> None:
            self.__row_lim = n_rows
            self.__height_lim = height
            self.__mode = "row"

        def init_both_specified(
            n_rows: int, n_cols: int, *, width: int = 1024, height: int = 1024
        ) -> None:
            self.__row_lim = n_rows
            self.__col_lim = n_cols
            self.__width_lim = width
            self.__height_lim = height
            self.__mode = "both"

        def detect(func: collections.abc.Callable[..., Any]) -> bool:
            sig = inspect.signature(func)
            try:
                all_args = sig.bind(*args, **kwargs)
            except TypeError:
                return False
            else:
                func(*all_args.args, **all_args.kwargs)
                return True

        if detect(init_col_specified):
            if self.__col_lim <= 0 or self.__width_lim <= 0:
                raise TypeError(
                    "The arguments do not specify the correct size limitation."
                )
        elif detect(init_row_specified):
            if self.__row_lim <= 0 or self.__height_lim <= 0:
                raise TypeError(
                    "The arguments do not specify the correct size limitation."
                )
        elif detect(init_both_specified):
            if (
                self.__col_lim <= 0
                or self.__width_lim <= 0
                or self.__row_lim <= 0
                or self.__height_lim <= 0
            ):
                raise TypeError(
                    "The arguments do not specify the correct size limitation."
                )
        else:
            raise TypeError(
                "Unable to detect the argument signatures: (args={0}, "
                "kwargs={1})".format(args, kwargs)
            )

    def _solve_idx(self, row: int, col: int) -> int:
        """(Private) Solve the internal index from the given dictionary."""
        if self.__col_lim > 0:
            if col >= self.__col_lim:
                raise IndexError("The column index overflows.")
            return row * self.__col_lim + col
        else:
            if row >= self.__row_lim:
                raise IndexError("The row index overflows.")
            return row + col * self.__row_lim

    def _rev_solve_idx(self) -> dict[int, dict[int, int]]:
        """(Private) Solve the row-column indicies reversely.

        This method is the base of iterating all indicies.
        """
        indicies: dict[int, dict[int, int]] = dict()
        if self.__col_lim > 0:
            for idx in self.__store.keys():
                _row = idx // self.__col_lim
                _col = idx % self.__col_lim
                indicies.setdefault(_row, dict())[_col] = idx
        elif self.__row_lim > 0:
            for idx in self.__store.keys():
                _col = idx // self.__row_lim
                _row = idx % self.__row_lim
                indicies.setdefault(_row, dict())[_col] = idx
        else:
            raise IndexError("The image grid does not specify the correct axes system.")
        return indicies

    @property
    def n_rows(self) -> int:
        """Property: Get the number of rows based on the currently registered images."""
        indicies: set[int] = set()
        if self.__col_lim > 0:
            for idx in self.__store.keys():
                _row = idx // self.__col_lim
                indicies.add(_row)
        elif self.__row_lim > 0:
            for idx in self.__store.keys():
                _row = idx % self.__row_lim
                indicies.add(_row)
        else:
            raise IndexError("The image grid does not specify the correct axes system.")
        return len(indicies)

    @property
    def n_cols(self) -> int:
        """Property: Get the number of columns based on the currently registered
        images."""
        indicies: set[int] = set()
        if self.__col_lim > 0:
            for idx in self.__store.keys():
                _col = idx % self.__col_lim
                indicies.add(_col)
        elif self.__row_lim > 0:
            for idx in self.__store.keys():
                _col = idx // self.__row_lim
                indicies.add(_col)
        else:
            raise IndexError("The image grid does not specify the correct axes system.")
        return len(indicies)

    def clear(self) -> None:
        """Remove all images registered to this storage."""
        self.__store.clear()

    def append(self, img: Image.Image | ImageProtocol) -> None:
        """Add an image to this grid.

        The image added by this method will be placed after previously registered
        images.

        Arguments
        ---------
        img: `Image.Image | ImageProtocol`
            The image instance to be registered.
        """
        if isinstance(img, Image.Image):
            img = ImageSingle(img, fmt=self.__fmt)
        # Solve the last index
        idx = (max(self.__store.keys()) + 1) if self.__store else 0
        if self.__mode == "both":
            idx_lim = self.__row_lim * self.__col_lim
            if idx >= idx_lim:
                raise IndexError("The grid has been full.")
        self.__store[idx] = img

    def pop(self, row: int, col: int) -> ImageProtocol:
        """Remove the image in the storage, and return it.

        Arguments
        ---------
        row: `int`
        col: `int`
            The indicies along the row and column axes.

        Returns
        -------
        #1: `ImageProtocol`
            The image removed from the storage.

            Will raise `KeyError` if the given index does not refer to an registered
            image.
        """
        return self.__store.pop(self._solve_idx(row, col))

    def __contains__(self, idx: tuple[int, int]) -> bool:
        """Test whether the index exists in the grid.

        Arguments
        ---------
        idx: `tuple[int, int]`
            The `(row, col)` index.
        """
        return self._solve_idx(idx[0], idx[1]) in self.__store

    def __getitem__(self, idx: tuple[int, int]) -> ImageProtocol:
        """Get the image stored in this grid.

        Arguments
        ---------
        idx: `tuple[int, int]`
            The `(row, col)` index.

        Returns
        -------
        #1: `ImageProtocol`
            The image in the storage.

            Will raise `KeyError` if the given index does not refer to an registered
            image.
        """
        return self.__store[self._solve_idx(idx[0], idx[1])]

    def __setitem__(
        self, idx: tuple[int, int], val: Image.Image | ImageProtocol
    ) -> None:
        """Add the image to this grid.

        Arguments
        ---------
        idx: `tuple[int, int]`
            The `(row, col)` index.

        Returns
        -------
        #1: `ImageProtocol`
            The image in the storage.

            Will raise `KeyError` if the given index does not refer to an registered
            image.
        """
        if isinstance(val, Image.Image):
            val = ImageSingle(val, fmt=self.__fmt)
        if self.__mode == "both":
            if idx[0] >= self.__row_lim or idx[1] >= self.__col_lim:
                raise IndexError("The grid has been full.")
        self.__store[self._solve_idx(idx[0], idx[1])] = val

    def __delitem__(self, idx: tuple[int, int]) -> None:
        """Remove the image in this grid.

        Arguments
        ---------
        idx: `tuple[int, int]`
            The `(row, col)` index.
        """
        del self.__store[self._solve_idx(idx[0], idx[1])]

    def __iter__(self) -> collections.abc.Iterator[tuple[int, int]]:
        """Iterate all `(row, col)` indicies in the order of row-col."""
        indicies = self._rev_solve_idx()
        for row in sorted(indicies.keys()):
            cols = indicies[row]
            for col in sorted(cols.keys()):
                yield row, col

    def items(self) -> collections.abc.Iterator[tuple[tuple[int, int], ImageProtocol]]:
        """Iterate all indicies and corresponding images.

        Returns
        -------
        #1: `tuple[int, int]`
            The `(row, col)` index.

        #2: `Image.Image`
            The image corresponding to the index.
        """
        indicies = self._rev_solve_idx()
        for row in sorted(indicies.keys()):
            cols = indicies[row]
            for col in sorted(cols.keys()):
                yield (row, col), self.__store[cols[col]]

    def _solve_render_indicies(
        self,
    ) -> tuple[dict[int, dict[int, int]], tuple[int, ...], tuple[int, ...]]:
        """(Private) Get the indicies used for rendering the image."""
        indicies = self._rev_solve_idx()
        idx_rows: tuple[int, ...] = tuple(
            sorted(set(key for key, cols in indicies.items() if cols))
        )
        idx_cols: tuple[int, ...] = tuple(
            sorted(
                functools.reduce(
                    lambda res, val: res.union(val.keys()), indicies.values(), set()
                )
            )
        )
        if len(idx_rows) == 0 or len(idx_cols) == 0:
            raise ValueError(
                "The image grid cannot be rendered because it does not have any "
                "valid indexed image."
            )
        return indicies, idx_rows, idx_cols

    def _render_col_lim(self) -> ImageMultiLayer:
        """(Private) Render the image in the column-limited mode."""
        if self.__width_lim <= 0:
            raise ValueError(
                "The image grid does not have the width limitation, but the mode "
                '"col" has been specified.'
            )
        indicies, idx_rows, idx_cols = self._solve_render_indicies()
        _idx_rows = {val: idx for idx, val in enumerate(idx_rows)}
        _idx_cols = {val: idx for idx, val in enumerate(idx_cols)}
        width_u = max(1, round(self.__width_lim / max(1, len(idx_cols))))
        hw_ratio = 0.0
        for img in self.__store.values():
            img_width, img_height = img.size
            img_hw_ratio = img_height / img_width
            if img_hw_ratio > hw_ratio:
                hw_ratio = img_hw_ratio
        height_u = round(width_u * hw_ratio)
        if height_u <= 0:
            raise ValueError("The registered images do not have valid heights.")
        n_rows = len(idx_rows)
        n_cols = len(idx_cols)
        images = ImageMultiLayer(
            (
                width_u * n_cols
                + self.__gaps[0] * (n_cols - 1)
                + self.__margins[0] * 2,
                height_u * n_rows
                + self.__gaps[1] * (n_rows - 1)
                + self.__margins[1] * 2,
            ),
            fmt=self.__fmt,
        )
        for idx_row in idx_rows:
            cols = indicies[idx_row]
            for idx_col in cols.keys():
                img = self.__store[cols[idx_col]].img
                img_hw_ratio = img.height / img.width
                img = img.resize(
                    (width_u, round(img_hw_ratio * width_u)),
                    resample=Image.Resampling.LANCZOS,
                )
                _img = (
                    ImageMultiLayer(width_u, height_u, fmt=self.__fmt)
                    .add_image(ImageSingle(img), "img")
                    .flatten()
                )
                images.add_image(
                    _img,
                    name="r{0}c{1}".format(idx_row, idx_col),
                    anchor="top left",
                    rel_anchor="top left",
                    pos_shift=(
                        _idx_cols[idx_col] * (width_u + self.__gaps[0])
                        + self.__margins[0],
                        _idx_rows[idx_row] * (height_u + self.__gaps[1])
                        + self.__margins[1],
                    ),
                )
        if self.__color is not None:
            images.add_background(self.__color)
        return images

    def _render_row_lim(self) -> ImageMultiLayer:
        """(Private) Render the image in the row-limited mode."""
        if self.__height_lim <= 0:
            raise ValueError(
                "The image grid does not have the height limitation, but the mode "
                '"row" has been specified.'
            )
        indicies, idx_rows, idx_cols = self._solve_render_indicies()
        _idx_rows = {val: idx for idx, val in enumerate(idx_rows)}
        _idx_cols = {val: idx for idx, val in enumerate(idx_cols)}
        height_u = max(1, round(self.__height_lim / max(1, len(idx_rows))))
        wh_ratio = 0.0
        for img in self.__store.values():
            img_width, img_height = img.size
            img_wh_ratio = img_width / img_height
            if img_wh_ratio > wh_ratio:
                wh_ratio = img_wh_ratio
        width_u = round(height_u * wh_ratio)
        if width_u <= 0:
            raise ValueError("The registered images do not have valid widths.")
        n_rows = len(idx_rows)
        n_cols = len(idx_cols)
        images = ImageMultiLayer(
            (
                width_u * n_cols
                + self.__gaps[0] * (n_cols - 1)
                + self.__margins[0] * 2,
                height_u * n_rows
                + self.__gaps[1] * (n_rows - 1)
                + self.__margins[1] * 2,
            ),
            fmt=self.__fmt,
        )
        for idx_row in idx_rows:
            cols = indicies[idx_row]
            for idx_col in cols.keys():
                img = self.__store[cols[idx_col]].img
                img_wh_ratio = img.width / img.height
                img = img.resize(
                    (round(img_wh_ratio * height_u), height_u),
                    resample=Image.Resampling.LANCZOS,
                )
                _img = (
                    ImageMultiLayer(width_u, height_u, fmt=self.__fmt)
                    .add_image(ImageSingle(img), "img")
                    .flatten()
                )
                images.add_image(
                    _img,
                    name="r{0}c{1}".format(idx_row, idx_col),
                    anchor="top left",
                    rel_anchor="top left",
                    pos_shift=(
                        _idx_cols[idx_col] * (width_u + self.__gaps[0])
                        + self.__margins[0],
                        _idx_rows[idx_row] * (height_u + self.__gaps[1])
                        + self.__margins[1],
                    ),
                )
        if self.__color is not None:
            images.add_background(self.__color)
        return images

    def _render_both_lim(self) -> ImageMultiLayer:
        """(Private) Render the image in the both-limited mode."""
        if self.__height_lim <= 0 or self.__width_lim <= 0:
            raise ValueError(
                "The image grid does not have the width or height limitation, but "
                'the mode "both" has been specified.'
            )
        indicies, idx_rows, idx_cols = self._solve_render_indicies()
        width_u = max(1, round(self.__width_lim / max(1, idx_cols[-1] + 1)))
        height_u = max(1, round(self.__height_lim / max(1, idx_rows[-1] + 1)))
        if width_u <= 0 or height_u <= 0:
            raise ValueError("The registered images do not have valid widths/heights.")
        n_rows = idx_rows[-1] + 1
        n_cols = idx_cols[-1] + 1
        images = ImageMultiLayer(
            (
                width_u * n_cols
                + self.__gaps[0] * (n_cols - 1)
                + self.__margins[0] * 2,
                height_u * n_rows
                + self.__gaps[1] * (n_rows - 1)
                + self.__margins[1] * 2,
            ),
            fmt=self.__fmt,
        )
        for idx_row in idx_rows:
            cols = indicies[idx_row]
            for idx_col in cols.keys():
                img = self.__store[cols[idx_col]].img
                img_wh_ratio = img.width / img.height
                if img_wh_ratio > 0:
                    _height = width_u / img_wh_ratio
                    if _height <= height_u:
                        img.resize(
                            (width_u, round(_height)), resample=Image.Resampling.LANCZOS
                        )
                    else:
                        img.resize(
                            (round(img_wh_ratio * height_u), height_u),
                            resample=Image.Resampling.LANCZOS,
                        )
                else:
                    _width = img_wh_ratio * height_u
                    if _width <= width_u:
                        img.resize(
                            (round(_width), height_u), resample=Image.Resampling.LANCZOS
                        )
                    else:
                        img.resize(
                            (width_u, round(width_u / img_wh_ratio)),
                            resample=Image.Resampling.LANCZOS,
                        )
                _img = (
                    ImageMultiLayer(width_u, height_u, fmt=self.__fmt)
                    .add_image(ImageSingle(img), "img")
                    .flatten()
                )
                images.add_image(
                    _img,
                    name="r{0}c{1}".format(idx_row, idx_col),
                    anchor="top left",
                    rel_anchor="top left",
                    pos_shift=(
                        idx_col * (width_u + self.__gaps[0]) + self.__margins[0],
                        idx_row * (height_u + self.__gaps[1]) + self.__margins[1],
                    ),
                )
        if self.__color is not None:
            images.add_background(self.__color)
        return images

    @property
    def img(self) -> ImageMultiLayer:
        """Property: Render the multi-layer image."""
        if self.__col_lim <= 0 and self.__row_lim <= 0:
            raise ValueError(
                "The image grid cannot be rendered because it does not specify the "
                "row or column number."
            )
        if not self.__store:
            raise ValueError(
                "The image grid cannot be rendered because it does not contain any "
                "image yet."
            )
        if self.__mode == "both":
            return self._render_both_lim()
        elif self.__mode == "col":
            return self._render_col_lim()
        elif self.__mode == "row":
            return self._render_row_lim()
        else:
            raise TypeError("Unrecongnized grid mode: {0}".format(self.__mode))
