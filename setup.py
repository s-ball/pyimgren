from setuptools import setup, find_packages
from pkg_resources import parse_version
import os.path
import re
import sys

from io import open

NAME = "pyimgren"

# Base version (removes any pre, post, a, b or rc element)
try:
    BASE = get_distribution(NAME).base_version
except:
    BASE = "0.0.0"

# In long description, replace "master" in the build status badges
#  with the current version we are building
with open("README.md") as fd:
    long_description = next(fd).replace("master", BASE)
    long_description += next(fd).replace("latest", BASE)
    long_description += "".join(fd)

setup(
    name=NAME,
    description = "Rename image files according to exif tags",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(exclude = ["tests", "docs"]),
    setup_requires = ["setuptools_scm", "mo_installer"],
    use_scm_version = { "write_to": os.path.join(NAME, 'version.py') },
    install_requires = ["piexif", "i18nparse"],
    tests_require = ["pyfakefs"],
    author="s-ball",
    author_email = "s-ball@laposte.net",
    url = "https://github.com/s-ball/pyimgren",
    license = "MIT License",
    project_urls = {
        "Documentation":
            "https://pyimgren.readthedocs.io/en/{}/".format(BASE),
        "Changelog":
            "https://github.com/s-ball/pyimgren/blob/master/CHANGES.txt"
        },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        ],
    python_requires=">=3",
    test_suite = "tests",
    entry_points = {
        "console_scripts": [
            "pyimgren=pyimgren.__main__:main",
            ],
        },
    package_data = { "": ["locale/*/*/*.mo"]},
    )
