# -*- coding: UTF-8 -*-
"""
Examples: Download Screenshots
==============================
@ Steam Editor Tools

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
An example to download the screenshots from the official site, and save the optmized
ones in the output folder.
"""

import os
import shutil

from typing_extensions import Literal

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("download_screenshots",)


def download_screenshots(
    name: str,
    out_folder_path: "str | os.PathLike[str]",
    lang: Literal["english", "chinese"] = "english",
) -> None:
    """Download the screenshots

    Arguments
    ---------
    name: `str`
        The name used for querying the game.

    out_folder_path: `str | PathLike[str]`
        The path to the output folder.

    lang: `str`
        The language used for searching the game.
    """
    raw_folder_path = os.path.join(out_folder_path, "raw")
    if os.path.isdir(raw_folder_path):
        shutil.rmtree(raw_folder_path, ignore_errors=True)
    os.makedirs(os.path.join(out_folder_path, "raw"), exist_ok=True)
    if lang == "chinese":
        _lang = "schinese"
        _cc = "cn"
    else:
        _lang = "english"
        _cc = "us"
    apps = stet.query_app_by_name_simple(name, lang=_lang, cc=_cc)
    if len(apps) < 1:
        raise ValueError("Does not find the game: {0}".format(name))
    app = apps[0]
    info = stet.get_app_details(app, lang=_lang, cc=_cc)
    if info is None:
        raise ValueError("Does not get the game details: {0}".format(name))
    proc_folder_path = os.path.join(out_folder_path, "{0}".format(info.steam_appid))
    os.makedirs(proc_folder_path, exist_ok=True)
    for scr in info.screenshots:
        img = scr.get_image()
        if img is None:
            continue
        img.save(os.path.join(raw_folder_path, "scr-{0:03d}.jpg".format(scr.id)))

    def processor(img: stet.ImageSingle) -> stet.ImageSingle:
        """Before saving the image, resize it to 1920x? if it is larger than this
        size."""
        if img.width > 1920:
            img = img.resize((1920, None))
        return img

    stet.improc.tools.batch_process_images(
        processor,
        folder_path=raw_folder_path,
        out_folder_path=proc_folder_path,
        out_file_name_prefix="proc",
        verbose=True,
    )


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    download_screenshots(
        "Hollow Knight",
        out_folder_path=os.path.join(root_dir, "example-screenshots"),
        lang="english",
    )
