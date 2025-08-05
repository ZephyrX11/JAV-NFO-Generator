#!/usr/bin/env python3
"""
Setup script for JAV NFO Generator
"""

from setuptools import setup, find_packages
import os

# Get the directory containing this file
here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jav-nfo-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI tool for scraping JAV metadata and generating .nfo files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python_jav_nfo_generator",
    packages=find_packages(),
    py_modules=["main"],  # Include main.py as a module
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jav-nfo=main:cli",
            "javnfo=main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 