# -*- coding: UTF-8 -*-
"""
Examples: Convert a table in a BBCode to List
=============================================
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
An example to read and rewrite a BBCode.
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet

__all__ = ("convert_bbcode_table_to_list",)


def convert_bbcode_table_to_list(file_path: "str | os.PathLike[str]") -> None:
    """Read a bbcode file, load its table, and convert the table to a list.

    Arguments
    ---------
    file_path: `str | PathLike[str]`
        The path to a BBCode file to be converted.
    """
    _raw_path = os.path.splitext(file_path)[0].strip()
    _raw_dir = os.path.dirname(_raw_path)
    out_file_path = os.path.join(
        _raw_dir, "example-table2list-" + os.path.split(_raw_path)[-1] + ".bbcode"
    )
    doc = stet.DocumentParser().parse_file(file_path)
    with open(out_file_path, "w", encoding="utf-8") as fobj:
        fobj.write(stet.bbcode.renderer.BBCodeRendererListPreferred().render(doc))


if __name__ == "__main__":
    file_path = os.path.join(os.path.dirname(__file__), "convert-table.bbcode")
    convert_bbcode_table_to_list(file_path)
