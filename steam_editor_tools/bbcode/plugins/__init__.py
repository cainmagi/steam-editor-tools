# -*- coding: UTF-8 -*-
"""
Renderer Plugins
================
@ Steam Editor Tools - BBCode

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The plugins for improving the markdown-it. Allow special rendering for extensive
Markdown-to-BBCode styles.
"""

from pkgutil import extend_path

from . import mark
from . import alert


__all__ = ("mark", "alert")

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
