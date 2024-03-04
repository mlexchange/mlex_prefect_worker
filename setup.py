from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="MLExWorker",
    version="0.2",
    python_requires=">=3.10",
    packages=find_packages(include=["flows", "flows.*"]),
    install_requires=required,
)
