#!/usr/bin/env python3
"""
Setup script for JAV NFO Generator
"""

from setuptools import setup, find_packages
import os

# Get the directory containing this file
here = os.path.abspath(os.path.dirname(__file__))

def read_file(filename):
    """Read file contents."""
    with open(filename, "r", encoding="utf-8") as fh:
        return fh.read()

def read_requirements(filename):
    """Read requirements from file."""
    requirements = []
    with open(filename, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements

# Read files
long_description = read_file("README.md")
requirements = read_requirements("requirements.txt")

setup(
    name="jav-nfo-generator",
    version="1.0.0",
    author="JAV NFO Generator Team",
    author_email="contact@javnfo.com",
    description="A powerful CLI tool for scraping JAV metadata and generating .nfo files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZephyrX11/JAV-NFO-Generator",
    project_urls={
        "Bug Reports": "https://github.com/ZephyrX11/JAV-NFO-Generator/issues",
        "Source": "https://github.com/ZephyrX11/JAV-NFO-Generator",
        "Documentation": "https://github.com/ZephyrX11/JAV-NFO-Generator#readme",
    },
    packages=find_packages(),
    py_modules=["main"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jav-nfo=main:cli",
            "javnfo=main:cli",
            "javnfo-generator=main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="jav nfo metadata scraper cli video media",
    platforms=["any"],
) 