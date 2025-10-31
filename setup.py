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
    version="1.0.2",
    author="Julio Ona",
    author_email="thinmanj@gmail.com",
    description="Enterprise-grade, VCS-agnostic ticket management system optimized for agentic development workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thinmanj/repo-tickets",
    project_urls={
        "Documentation": "https://github.com/thinmanj/repo-tickets#readme",
        "Source": "https://github.com/thinmanj/repo-tickets",
        "Issues": "https://github.com/thinmanj/repo-tickets/issues",
        "Changelog": "https://github.com/thinmanj/repo-tickets/releases",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Version Control",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Software Development :: Version Control :: Mercurial",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Typing :: Typed",
    ],
    keywords="tickets issue-tracker project-management git mercurial jujutsu vcs cli workflow agents ai automation devops agile epic backlog requirements bdd gherkin",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "colorama>=0.4.4",
        "tabulate>=0.9.0",
        "python-dateutil>=2.8.0",
        "rich>=13.0.0",
        "textual>=0.44.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tickets=repo_tickets.cli:main",
        ],
    },
)
