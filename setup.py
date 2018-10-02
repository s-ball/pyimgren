from setuptools import setup, find_packages

from io import open

with open('README.md') as fd:
    long_description = fd.read()

setup(
    name="pyimgren",
    version = "0.1.0",
    description = "Rename image files according to exif tags",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = find_packages(exclude = ["tests", "docs"]),
    install_requires = ["piexif"],
    author="s-ball",
    author_email = 's-ball@laposte.net',
    url = "https://github.com/s-ball/pyimgren",
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires=">=3",
##    entry_points = {
##        'console_scripts': [
##            'pyimgren=pyimgren:main',
##            ],
##        },
    )
