from setuptools import setup, find_packages
import os.path
import re

from io import open

NAME = "pyimgren"
with open(os.path.join(os.path.dirname(__file__), NAME,
                       "version.py")) as fd:
    ver_line = next(fd)
    m = re.match(r"\s*__version__\s*=\s*['\"]([^'\"]+)['\"]", ver_line)
    VERSION = m.group(1)

# In long description, replace "master" in the build status badges
#  with the current version we are building
with open('README.md') as fd:
    long_description = next(fd).replace('master', VERSION)
    long_description += ''.join(fd)

setup(
    name=NAME,
    version = VERSION,
    description = "Rename image files according to exif tags",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(exclude = ["tests", "docs"]),
    install_requires = ["piexif"],
    tests_require = ['pyfakefs'],
    author="s-ball",
    author_email = 's-ball@laposte.net',
    url = "https://github.com/s-ball/pyimgren",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires=">=3",
    test_suite = "tests",
    entry_points = {
        'console_scripts': [
            'pyimgren=pyimgren.__main__:main',
            ],
        },
    )
