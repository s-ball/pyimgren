# MIT License
# Copyright (c) 2018 s-ball

from .pyimgren import Renamer
from .version import __version__

__all__ = ["Renamer", "__version__", "__name__"]

import gettext
import locale
import os.path

loc = locale.getlocale()[0]
if loc is None: loc = locale.getdefaultlocale()[0]

_ = gettext.translation("pyimgren",
                        os.path.join(os.path.dirname(__file__), "locale"),
                        loc,
                        fallback=True).gettext
