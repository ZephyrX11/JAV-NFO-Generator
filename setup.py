#!/usr/bin/env python3
"""
Setup script for JAV NFO Generator.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jav-nfo-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python CLI tool for scraping JAV metadata and generating .nfo files",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/python_jav_nfo_generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "jav-nfo-generator=main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="jav metadata scraper nfo generator",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/python_jav_nfo_generator/issues",
        "Source": "https://github.com/yourusername/python_jav_nfo_generator",
    },
) 