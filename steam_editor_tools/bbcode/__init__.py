# -*- coding: UTF-8 -*-
"""
BBCode
======
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
The BBCode parsing package in Steam Editor Tools.

This package supports the conversion and serialization from the other document formats
to Steam BBCode texts.

This package may also supports other BBCode formats if users customize `BBCodeConfig`
by themselves.
"""

from pkgutil import extend_path

from . import nodes
from . import plugins
from . import parser
from . import guide
from . import renderer

from .parser import DocumentParser
from .guide import GuideParser
from .renderer import BBCodeRenderer, BBCodeConfig, AlertTitleConfigs


__all__ = (
    "nodes",
    "plugins",
    "parser",
    "renderer",
    "guide",
    "DocumentParser",
    "GuideParser",
    "BBCodeRenderer",
    "BBCodeConfig",
    "AlertTitleConfigs",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
