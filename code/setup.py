#!/usr/bin/env python3
"""Helix-TTD Python Toolkit.

Constitutional AI governance utilities

License: Apache-2.0
"""

from setuptools import setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="helix-ttd",
    version="1.0.0",
    author="Stephen Hope",
    author_email="sbhope@gmail.com",
    description="Constitutional AI governance utilities for the Helix-TTD Federation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/helixprojectai-code/helix-ttd-kimi-cli",
    py_modules=[
        "helix_cli",
        "naming_convention",
        "drift_telemetry",
        "constitutional_compliance",
        "receipts_manager",
        "looksee_audit",
        "rpi_tracker",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "helix=helix_cli:main",
        ],
    },
)
