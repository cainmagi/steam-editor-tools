# -*- coding: UTF-8 -*-
"""
LaTeX to Image
==============
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
The extension supporting the conversion from LaTeX equations to pixel-based images.

Note that this package requires the installtion of a released version of LaTeX.

We recommend TeXLive, see
https://www.tug.org/texlive/
"""

import os
import subprocess

from PIL import Image

from .data import TeXTemplate
from .variables import steam_color, tex_templates as templates
from ..utils import NamedTempFolder


class TeXRenderer:
    """The LaTeX renderer.

    Render the LaTeX equation to pixel image. The backend is implemented by calling the
    `latex` command. Therefore, using this renderer requires the installation of a
    LaTeX released version.
    """

    __slots__ = ("path_temp", "verbose")

    def __init__(
        self, path_temp: "str | os.PathLike[str] | None" = None, verbose: bool = False
    ) -> None:
        """Initialzation.

        Arguments
        ---------
        path_temp: `str | PathLike[str] | None`
            The path to the folder storing the temporary files. If not specified, will
            create a folder in the temp path,

        verbose: `bool`
            Whether to show the running details of LaTeX.
        """
        self.path_temp = path_temp
        self.verbose = bool(verbose)

    @staticmethod
    def get_template(template: str | TeXTemplate = "default") -> TeXTemplate:
        """Get the LaTeX rendering template by specifying the template name."""
        if isinstance(template, TeXTemplate):
            return template
        if template in ("default", "chinese", "multilines", "multilines_chinese"):
            return templates[template]
        else:
            return templates["default"]

    def render(
        self, equation: str, template: str | TeXTemplate = "default"
    ) -> Image.Image:
        """Render the equation into a pixel-based image.

        Arguments
        ---------
        equation: `str`
            The LaTeX equation. This equation is treated as a block equation.

            Do not need to specify `$` or `$$` symbol.

        template: `str | TeXTemplate`
            The LaTeX template used for rendering the equation. If using `str`, this
            value will be treated as the template name. Users can provide
            self-implemented template by instantiate `TeXTemplate`.

            Check `improc.variables.tex_templates` to view the currently supported
            templates.
        """
        template = self.get_template(template)
        with NamedTempFolder(self.path_temp) as path:
            name_tex = "equation"
            path_tex = os.path.join(path, name_tex)
            # Write LaTeX file
            with open(path_tex + ".tex", "w", encoding="utf-8") as f:
                f.write(template.render(equation))

            # Compile LaTeX → DVI
            subprocess.run(
                ["latex", "-interaction=nonstopmode", name_tex + ".tex"],
                cwd=path,  # current folder
                check=True,
                stdout=None if self.verbose else subprocess.DEVNULL,
            )

            # Convert DVI → PNG with DPI and tight bounding box
            subprocess.run(
                [
                    "dvipng",
                    "-D",
                    "600",  # DPI (resolution)
                    "-T",
                    "tight",  # Trim margins
                    "-bg",
                    "Transparent",  # Optional: transparent background
                    "-o",
                    name_tex + ".png",  # Output file
                    name_tex + ".dvi",
                ],
                cwd=path,  # current folder
                check=True,
                stdout=None if self.verbose else subprocess.DEVNULL,
            )

            with Image.open(path_tex + ".png", "r") as fobj:
                alpha = fobj.convert("RGBA").getchannel("A")

            return alpha

    def render_png(
        self,
        out_file: "str | os.PathLike[str]",
        equation: str,
        template: str | TeXTemplate = "default",
        bg_color: str | tuple[float, ...] = steam_color,
        fg_color: str | tuple[float, ...] = "#ffffff",
        out_width: int = 3000,
    ) -> None:
        """Render the equation as a PNG file.

        This method is recommended for previewing the rendered equations.

        Arguments
        ---------
        out_file: `str | PathLike[str]`
            The path to the output file.

        equation: `str`
            The LaTeX equation. This equation is treated as a block equation.

            Do not need to specify `$` or `$$` symbol.

        template: `str | TeXTemplate`
            The LaTeX template used for rendering the equation. If using `str`, this
            value will be treated as the template name. Users can provide
            self-implemented template by instantiate `TeXTemplate`.

            Check `improc.variables.tex_templates` to view the currently supported
            templates.

        bg_color: `str | tuple[float, ...]`
            The background color of the rendered image.

        fg_color: `str | tuple[float, ...]`
            The foreground (text) color.

        out_width: `int`
            The width of the output image. If the rendered equation is not long
            enough, will place the equation in the center of the image.

            This option ensures that every output file to have the same image width.
        """
        alpha = self.render(equation=equation, template=template)
        out_h = alpha.height + 32 * 2
        out_w = max(out_width, alpha.width)

        # Full-size foreground/background (configured to output width)
        fg_full = Image.new("RGB", (out_w, out_h), fg_color)
        bg_full = Image.new("RGB", (out_w, out_h), bg_color)

        # Build a full-size alpha mask, with the original alpha centered horizontally
        mask_full = Image.new("L", (out_w, out_h), 0)
        offset_x = (out_w - alpha.width) // 2
        offset_y = (out_h - alpha.height) // 2
        mask_full.paste(alpha, (offset_x, offset_y))

        # Composite foreground over background using the centered alpha mask
        composite = Image.composite(fg_full, bg_full, mask_full)

        # Save as opaque, optimized PNG (no alpha channel)
        composite.quantize(colors=16, method=Image.Quantize.FASTOCTREE).save(
            str(out_file),
            format="PNG",
            optimize=True,  # run optimizer
            compress_level=9,  # highest deflate compression
            bits=4,  # explicitly configure 4-bit depth
        )
