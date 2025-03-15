# MIT License
# Copyright (c) 2018-current s-ball

from .renamer import Renamer
from .version import version as __version__


__all__ = ["Renamer"]

import gettext
import locale
import os.path

def nls_init(reset=False):
    if reset:
        renamer._ = lambda x: x
    else:
        loc = locale.getlocale()[0]
        if loc is None:
            loc = locale.setlocale(locale.LC_ALL, '')[0]

        renamer._ = gettext.translation("pyimgren",
                                         os.path.join(os.path.dirname(__file__),
                                                      "locale"),
                                         loc,
                                         fallback=True).gettext
