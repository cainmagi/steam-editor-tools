# -*- coding: UTF-8 -*-
"""
Renderer
========
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
Render the AST (Document/Node) into BBCode.

Users may customzie the BBCode styles by instantiating their own `BBCodeConfig`.
"""

from pkgutil import extend_path

from . import configs
from . import base
from . import variants

from .configs import AlertTitleConfigs, BBCodeConfig
from .base import BBCodeRenderer
from .variants import BBCodeRendererTablePreferred, BBCodeRendererListPreferred

__all__ = (
    "configs",
    "base",
    "variants",
    "AlertTitleConfigs",
    "BBCodeRenderer",
    "BBCodeConfig",
    "BBCodeRendererTablePreferred",
    "BBCodeRendererListPreferred",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
