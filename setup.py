import codecs
import os
import re

import setuptools


readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_path, 'r') as fp:
    long_description = fp.read()

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name="sprig",
    version=find_version("src", "sprig", "__init__.py"),
    author="AP Ljungquist",
    author_email="ap@ljungquist.eu",
    description="A home to code that would otherwise be homeless",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apljungquist/sprig",
    license="MIT",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
