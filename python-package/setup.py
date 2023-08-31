from pathlib import Path

from setuptools import setup

README_FILE_PATH = Path("README.md")

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

# Note the package should always be installed via `pip install` rather than
# directly calling setup.py. When installed that way, the values of
# pyproject.toml are passed in here
setup(
    packages=["opchatserver"],
    package_dir={"": "src"},
    long_description=README_FILE_PATH.read_text(),
    setup_requires=requirements,
)
