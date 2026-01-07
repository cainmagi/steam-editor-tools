# -*- coding: UTF-8 -*-
"""
Variables
=========
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
The global variables of this package.
"""

from typing_extensions import Literal

from .data import Templates, TeXTemplate


__all__ = (
    "steam_color",
    "steam_color_secondary",
    "steam_color_dimmed",
    "steam_color_light",
    "steam_color_light",
    "tex_templates",
)

steam_color: Literal["#1b2838"] = "#1b2838"
"""The primary steam color. It is the color of the page background."""

steam_color_secondary: Literal["#2e4863"] = "#2e4863"
"""The secondary steam color. It is the color of the card background."""

steam_color_dimmed: Literal["#445874"] = "#445874"
"""The secondary steam color. It is the color of alert box background."""

steam_color_light: Literal["#66C0F4"] = "#66C0F4"
"""The light steam color. It is the color of the colored text."""

tex_templates = Templates(
    default=TeXTemplate(
        prep=R"""
\documentclass[preview,border=5pt]{standalone}
\usepackage{amsmath, amssymb}
\begin{document}
\begin{equation*}
\begin{aligned}
""",
        end=R"""
\end{aligned}
\end{equation*}
\end{document}
""",
    ),
    chinese=TeXTemplate(
        prep=R"""
\documentclass[preview,border=5pt]{standalone}
\usepackage{amsmath, amssymb}
\usepackage{CJKutf8}
\begin{document}
\begin{CJK}{UTF8}{gbsn}
\begin{equation*}
\begin{aligned}
""",
        end=R"""
\end{aligned}
\end{equation*}
\end{CJK}
\end{document}
""",
    ),
    multilines=TeXTemplate(
        prep=R"""
\documentclass[preview,border=5pt]{standalone}
\usepackage{amsmath, amssymb}
\begin{document}
\begin{equation*}
""",
        end=R"""
\end{equation*}
\end{document}
""",
    ),
    multilines_chinese=TeXTemplate(
        prep=R"""
\documentclass[preview,border=5pt]{standalone}
\usepackage{amsmath, amssymb}
\usepackage{CJKutf8}
\begin{document}
\begin{CJK}{UTF8}{gbsn}
\begin{equation*}
""",
        end=R"""
\end{equation*}
\end{CJK}
\end{document}
""",
    ),
)
"""The built-in LaTeX templates."""
