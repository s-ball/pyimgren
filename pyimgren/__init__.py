# MIT License
# Copyright (c) 2018 s-ball

from .pyimgren import Renamer
from .version import __version__
# import .pyimgren

__all__ = ["Renamer", "__version__", "__name__"]

import gettext
import locale
import os.path

def nls_init(reset=False):
    if reset:
        pyimgren._ = lambda x: x
    else:
        loc = locale.getlocale()[0]
        if loc is None: loc = locale.getdefaultlocale()[0]

        pyimgren._ = gettext.translation("pyimgren",
                                os.path.join(os.path.dirname(__file__),
                                             "locale"),
                                loc,
                                fallback=True).gettext
