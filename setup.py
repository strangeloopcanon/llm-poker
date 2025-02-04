# setup.py

from setuptools import setup, find_packages

setup(
    name="poker_eval",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "llm",    # for calling LLM models
        "click",  # for the CLI
    ],
    entry_points={
        "console_scripts": [
            "poker-eval = poker_eval.cli:main",
        ],
    },
    description="Minimal environment for multi-LLM Texas Hold'em with reliability checks.",
    author="Rohit Krishnan",
    author_email="rohit.krishnan@gmail.com",
    url="http://www.strangeloopcanon.com",
)
