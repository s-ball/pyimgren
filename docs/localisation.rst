Localisation
============

Internationalization
--------------------

:mod:`pyimgren` is a fully internationalized package. The French translations
are provided for the source files and
the documentation.

If you use it as a module, and want to use that feature, you just have to
call the :func:`~pyimgren.renamer.nls_init` function::

    import pyimgren
    ...
    pyimgren.nls_init()          # enable i18n on the pyimgren package

If the ``LANG`` environment variable is present, it is used to define the
locale that will be used by :program:`pyimgren`. Else the default locale is used.

Localisation of the code
------------------------

You should use the `GNU gettext tools`_
to generate the POT files for :file:`cmdline.py` and :file:`pyimgren.py`. The fully
translated PO files are expected to be in the locale folder. For a language
``ll`` (resp. ``ll_CC``) they should be named :file:`pyimgren-ll.po` and
:file:`cmdline-ll.po` (resp. :file:`pyimgren-ll_CC.po` and :file:`cmdline-ll_CC.po`)

That way they will be automatically compiled at build time to the corresponding
MO file and will be used at run time.

Localisation of the documentation
---------------------------------

You will need to install `sphinx-intl`_::

    pip install spinx-intl

Alternatively, the package is automatically installed along with the
``pyimgren`` package it you ask for the ``docs`` options at install time::

    pip install pyimgren[docs]

Once installed, you can generate the POT files in the ``_build/gettext``
folder with::

    make gettext

and prepare (or update) the PO files for the ``ll`` locale with::

    sphinx-intl update -p _build/gettext -l ll

The PO files will end in the ``docs/locale/ll/LC_MESSAGES`` folder.

You will have to edit them to add all the translated strings.
You will then generate the
translated documentation on a Unix-like system with (assuming a sphinx
>= 1.3)::

    make -e SPHINXOPTS="-D language='ll'" html

and on Windows with::

    set SPHINXOPTS=-D language=ll
    .\make.bat html

Have everything on ReadTheDocs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I maintain a documentation project for ``pyimgren`` on
`Read the Docs <https://about.readthedocs.com/>`_. So the English
documentation is directly accessible at `<https://pyimgren.readthedocs.io/>`_

I also maintain (manually) a companion project for the French documentation.

If you have a translation that you would like to be there, you should
contact me through an issue on GitHub, or directly by mail.

..  _GNU gettext tools: https://www.gnu.org/software/gettext/
.. _sphinx-intl: https://pypi.org/project/sphinx-intl/