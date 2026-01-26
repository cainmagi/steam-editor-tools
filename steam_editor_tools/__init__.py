# -*- coding: UTF-8 -*-
"""
Steam Editor Tools
======

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
This package offers editor tools helping users write Steam guides and reviews.

This package support Steam information queries, image editing tools, and BBCode
text processing tools. Users can write their documents with Markdown, use this
package to process the images in the document, and convert the document to the
Steam BBCode format.
"""

from pkgutil import extend_path

from . import version
from . import utils
from . import bbcode
from . import improc
from . import steaminfo

from .version import __version__
from .bbcode import (
    DocumentParser,
    GuideParser,
    BBCodeRenderer,
    BBCodeConfig,
    AlertTitleConfigs,
)
from .improc import (
    FontLanguage,
    FontLocator,
    ImageFontAbsSize,
    ImageFontSize,
    ImageFormat,
    ImageQuality,
    ImageAnchor,
    ImageComposer,
    ImageComposerMode,
    ImageSingle,
    ImageText,
    ImageTeX,
    ImageMultiLayer,
)
from .steaminfo import query_app_by_name_simple, get_app_details

__all__ = (
    "version",
    "utils",
    "bbcode",
    "improc",
    "steaminfo",
    "__version__",
    "DocumentParser",
    "GuideParser",
    "BBCodeRenderer",
    "BBCodeConfig",
    "AlertTitleConfigs",
    "FontLanguage",
    "FontLocator",
    "ImageFontAbsSize",
    "ImageFontSize",
    "ImageFormat",
    "ImageQuality",
    "ImageAnchor",
    "ImageComposer",
    "ImageComposerMode",
    "ImageSingle",
    "ImageText",
    "ImageTeX",
    "ImageMultiLayer",
    "query_app_by_name_simple",
    "get_app_details",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
