#!/usr/bin/env python3
"""
Setup script for repo-tickets CLI application.
"""

from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A CLI ticket system for VCS repositories"

setup(
    name="repo-tickets",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A CLI ticket system that works with git, mercurial, and Jujutsu repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/repo-tickets",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Bug Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "colorama>=0.4.4",
        "tabulate>=0.9.0",
        "python-dateutil>=2.8.0",
        "rich>=13.0.0",
        "textual>=0.44.0",
    ],
    entry_points={
        "console_scripts": [
            "tickets=repo_tickets.cli:main",
        ],
    },
)