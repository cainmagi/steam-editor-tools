# -*- coding: UTF-8 -*-
"""
Examples: Render LaTeX equations
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
Note that running this example requires the intallation of LaTeX. See

https://www.tug.org/texlive/
"""

import os

if __name__ == "__main__":
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import steam_editor_tools as stet


__all__ = ("render_latex_simple", "render_latex_styled")


def render_latex_simple(equation: str, out_file_path: "str | os.PathLike[str]") -> None:
    """Render the LaTeX equation with simple presets.

    Arguments
    ---------
    equation: `str`
        The equation to be rendered.

    out_file_path: `str | PathLike[str]`
        The path to the output file.
    """
    stet.improc.TeXRenderer().render_png(
        out_file=out_file_path,
        template="multilines",
        equation=equation,
        out_width=2700,
    )


def render_latex_styled(equation: str, out_file_path: "str | os.PathLike[str]") -> None:
    """Render the LaTeX equation with stroke and shadow.

    Arguments
    ---------
    equation: `str`
        The equation to be rendered.

    out_file_path: `str | PathLike[str]`
        The path to the output file.
    """
    stet.ImageMultiLayer((2700, 500), fmt="png").add_latex(
        equation=equation,
        name="eq1",
        template="multilines",
        font_size="h1",
        color="#ffffff",
        stroke_color="#000000",
        shadow_color="#000000",
    ).add_background().convert("RGB").save(out_file_path)


if __name__ == "__main__":
    root_dir = os.path.dirname(__file__)

    equation = (
        R"\left\{\begin{aligned}"
        R"\nabla \times \mathbf{E} &= - \mu \frac{\partial \mathbf{H}}{\partial t}, \\"
        R"\nabla \times \mathbf{H} &= \varepsilon "
        R"\frac{\partial \mathbf{E}}{\partial t} + \sigma \mathbf{E} + \mathbf{J}."
        R"\end{aligned}\right."
    )

    render_latex_simple(
        equation,
        out_file_path=os.path.join(root_dir, "example-eq-simple.png"),
    )

    render_latex_styled(
        equation,
        out_file_path=os.path.join(root_dir, "example-eq-styled.png"),
    )
