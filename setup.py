# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-poker",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "llm",
        "click",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "poker-eval = poker_eval.cli:main",  
        ],
    },
    description="Texas Hold'em environment with LLM players",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rohit Krishnan",
    author_email="rohit.krishnan@gmail.com",
    url="http://www.strangeloopcanon.com",
)
