from setuptools import setup, find_packages
from pkg_resources import parse_version
import os.path
import re
import sys

from io import open

NAME = "pyimgren"
with open(os.path.join(os.path.dirname(__file__), NAME,
                       "version.py")) as fd:
    ver_line = next(fd)
    m = re.match(r'\s*__version__\s*=\s*["\"]([^"\"]+)["\"]', ver_line)
    VERSION = m.group(1)

# Base version (removes any pre, post, a, b or rc element)
BASE = parse_version(VERSION).base_version

# In long description, replace "master" in the build status badges
#  with the current version we are building
with open("README.md") as fd:
    long_description = next(fd).replace("master", BASE)
    long_description += next(fd).replace("latest", BASE)
    long_description += "".join(fd)

sys.path.append(os.path.join(os.path.dirname(__file__), "tools_i18n"))
import msgfmt
from setuptools.command.build_py import build_py as _build

class Builder(_build):
    def run(self):
        self.__mo_files = []
        po = re.compile(r"(.*)_(.*).po")
        for file in os.listdir("locale"):
            m = po.match(file)
            if m:
                path = os.path.join(self.build_lib, NAME, "locale",
                                 m.group(2), "LC_MESSAGES")
                os.makedirs(path, exist_ok=True)
                mofile = os.path.join(path, m.group(1) + ".mo")
                msgfmt.make(os.path.join("src", file), mofile)
                self.__mo_files.append(mofile)
        _build.run(self)
    def get_outputs(self):
        return _build.get_outputs(self) + self.__mo_files

setup(
    name=NAME,
    version = VERSION,
    description = "Rename image files according to exif tags",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(exclude = ["tests", "docs"]),
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
    cmdclass = {"build_py": Builder},
    )
