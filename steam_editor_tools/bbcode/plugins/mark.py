# -*- coding: UTF-8 -*-
"""
Marker
======
@ Steam Editor Tools - Renderer Plugins

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The plugin rendering `==...==` as highlight `<mark>,,,</mark>`.
"""

import re

from typing import Any

from markdown_it.main import MarkdownIt
from markdown_it.token import Token
from markdown_it.renderer import RendererHTML


__all__ = ("mark_plugin",)

MARK_RE = re.compile(r"==(.+?)==")


def mark_plugin(md: MarkdownIt) -> None:
    """Simple plugin: replace `==text==` with `<mark>text</mark>` using regex."""

    def render_text(
        self: RendererHTML,
        tokens: list[Token],
        idx: int,
        options: dict[str, Any],
        env: dict[str, Any],
    ) -> str:
        content = tokens[idx].content
        return MARK_RE.sub(r"<mark>\1</mark>", content)

    md.add_render_rule("text", render_text)
