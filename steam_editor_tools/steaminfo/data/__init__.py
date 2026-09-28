# -*- coding: UTF-8 -*-
"""
Data
=======
@ Steam Editor Tools - Steam Information

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The data structures for this package.
"""

from pkgutil import extend_path

from . import appdata
from . import achievements

from .appdata import AppQuerySimple, AppInfo
from .achievements import AchievementList

__all__ = (
    "appdata",
    "achievements",
    "AppQuerySimple",
    "AchievementList",
    "AppInfo",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
