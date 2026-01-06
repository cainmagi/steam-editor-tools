# -*- coding: UTF-8 -*-
"""
Examples: Markdown to BBCode
============================
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
An example to convert a Markdown file to Steam BBCode.
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("markdown_to_bbcode",)


def markdown_to_bbcode(file_path: "str | os.PathLike[str]") -> None:
    """Convert a markdown file to a bbcode file. The BBcode file will be saved in
    the same folder.

    Arguments
    ---------
    file_path: `str | PathLike[str]`
        The path to a markdown file or an HTML file to be converted.
    """
    out_file_path = os.path.splitext(file_path)[0].strip() + ".bbcode"
    doc = stet.DocumentParser().parse_file(file_path)
    with open(out_file_path, "w", encoding="utf-8") as fobj:
        fobj.write(stet.BBCodeRenderer().render(doc))


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "markdown.md")
    markdown_to_bbcode(file_path)
