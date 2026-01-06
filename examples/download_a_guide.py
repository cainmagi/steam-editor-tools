# -*- coding: UTF-8 -*-
"""
Examples: Download a Steam Guide
================================
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
An example to download a Steam guide and parse it as BBCode text.
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("download_a_guide",)


def download_a_guide(url: str | int, out_file_path: "str | os.PathLike[str]") -> None:
    """Convert a markdown file to a bbcode file. The BBcode file will be saved in
    the same folder.

    Arguments
    ---------
    url: `str | int`
        The full Steam guide URL or its numeric ID. If an ID is given, the full
        URL will be

        `https://steamcommunity.com/sharedfiles/filedetails/?id=<url>`

    out_file_path: `str | PathLike[str]`
        The path to the output file.
    """
    doc = stet.GuideParser().parse(url)
    with open(out_file_path, "w", encoding="utf-8") as fobj:
        fobj.write(stet.BBCodeRenderer().render(doc))


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "example-guide.bbcode")
    download_a_guide(1258079393, file_path)
