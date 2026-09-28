# -*- coding: UTF-8 -*-
"""
Examples: Render achievements as BBCode
=======================================
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
An example to download all achievements and save them as files.
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet

__all__ = ("convert_bbcode_achievements",)


def convert_bbcode_achievements(folder_path: str, app_id: int) -> None:
    """Read a bbcode file from achievements parsed from the game page.

    Arguments
    ---------
    folder_path: `str | os.PathLike[str]`
        The path to the folder where the output files are saved.

    app_id: `int`
        The ID of the app (game). The achievements will be fetched from it.
    """
    folder_path = folder_path.strip()
    out_folder_path = os.path.join(folder_path, "example-ach-{0}".format(app_id))

    achievements = stet.get_achievement_list(app_id)
    achievements.save_icons(out_folder_path)
    doc = stet.DocumentParser().parse_achievements(achievements)
    with open(
        os.path.join(out_folder_path, "achievements.bbcode"), "w", encoding="utf-8"
    ) as fobj:
        fobj.write(stet.bbcode.renderer.BBCodeRenderer().render(doc))


if __name__ == "__main__":
    convert_bbcode_achievements(folder_path=os.path.dirname(__file__), app_id=510420)
