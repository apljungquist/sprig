# pylint: disable=missing-docstring
import codecs
import os
import re

import setuptools


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as f:
        return f.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="sprig",
    version=find_version("src", "sprig", "__init__.py"),
    author="AP Ljungquist",
    author_email="ap@ljungquist.eu",
    description="A home to code that would otherwise be homeless",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/apljungquist/sprig",
    license="MIT",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
