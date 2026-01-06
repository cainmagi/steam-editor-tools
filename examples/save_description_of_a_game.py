# -*- coding: UTF-8 -*-
"""
Examples: Save Game Description
===============================
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
Render a figure as a title.
"""

import os

from typing_extensions import Literal

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("save_game_description",)

HTML_TEMPLATE: str = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      margin: 1.5rem;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
<h1 id="title">{title}</h1>
<h2 id="intro">Introduction</h1>
<div><p>{intro}</p></div>
<h2 id="about">About this game</h2>
{body}
</body>
</html>
"""


def save_game_description(
    name: str,
    out_file_path: "str | os.PathLike[str]",
    lang: Literal["english", "chinese"] = "english",
) -> None:
    """Create a simple title figure.

    Arguments
    ---------
    name: `str`
        The name used for querying the game.

    out_file_path: `str | PathLike[str]`
        The path to the output file.

    lang: `str`
        The language used for searching the game.
    """
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
    with open(out_file_path, "w", encoding="utf-8") as fobj:
        fobj.write(
            HTML_TEMPLATE.format(
                title=info.name,
                lang=lang,
                intro=info.short_description,
                body=info.about_the_game,
            )
        )


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)
    save_game_description(
        "Hollow Knight",
        out_file_path=os.path.join(root_dir, "example-game-descr.html"),
        lang="english",
    )
