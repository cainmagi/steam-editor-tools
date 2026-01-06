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

from .data import ImageQuality
from .renderer import ImageSingle


__all__ = ("batch_process_images",)

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
