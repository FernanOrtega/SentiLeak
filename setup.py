import os

from setuptools import setup, find_packages

VERSION = "0.1-beta.2"
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def licence():
    with open("LICENSE") as f:
        return f.read()


def readme():
    with open(os.path.join(THIS_DIR, "README.md"), encoding="utf-8") as f:
        return f.read()


with open(os.path.join(THIS_DIR, "requirements.txt")) as f:
    requirements = f.read().splitlines()

setup(
    name="SentiLeak",
    version=VERSION,
    install_requires=requirements,
    author="FernanOrtega",
    author_email="f.ortega.gallego@gmail.com",
    description="A lexicon-based sentiment analysis for Spanish.",
    long_description_content_type='text/markdown',
    long_description=readme(),
    packages=find_packages(exclude=["test"]),
    licence=licence(),
    url="https://fernanortega.es/",
)
