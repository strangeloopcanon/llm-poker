# setup.py

from setuptools import setup, find_packages

setup(
    name="poker-eval",
    version="0.1.1",
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
    author="Rohit Krishnan",
    author_email="rohit.krishnan@gmail.com",
    url="http://www.strangeloopcanon.com",
)
