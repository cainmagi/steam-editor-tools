# -*- coding: UTF-8 -*-
"""
Image Processing
================
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
The image processing package for preparing the figures when writing the Steam guides.

This package supports image editing by codes, especially for creating an image based
on stacking multiple layers of images, texts and equations.

This package is implemented solely using the lightweight Pillow package.
"""

from pkgutil import extend_path

from . import data
from . import variables
from . import latex_to_img
from . import font
from . import composer
from . import effects
from . import overlays
from . import layer
from . import renderer
from . import tools

from .data import (
    ImageFontAbsSize,
    ImageFontSize,
    ImageFormat,
    ImageQuality,
    ImageAnchor,
    TeXTemplate,
)
from .latex_to_img import TeXRenderer
from .font import FontLanguage, FontInfo, FontLocator
from .composer import ImageComposer, ImageComposerMode
from .layer import ImageEffects, ImageLayer
from .renderer import ImageSingle, ImageText, ImageTeX, ImageMultiLayer


__all__ = (
    "data",
    "variables",
    "latex_to_img",
    "font",
    "composer",
    "effects",
    "overlays",
    "layer",
    "renderer",
    "tools",
    "TeXTemplate",
    "ImageFontAbsSize",
    "ImageFontSize",
    "ImageFormat",
    "ImageQuality",
    "ImageAnchor",
    "TeXRenderer",
    "FontLanguage",
    "FontInfo",
    "FontLocator",
    "ImageComposer",
    "ImageComposerMode",
    "ImageEffects",
    "ImageLayer",
    "ImageSingle",
    "ImageText",
    "ImageTeX",
    "ImageMultiLayer",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
