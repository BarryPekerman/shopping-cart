from setuptools import setup, find_packages

setup(
    name="backend_api",
    version="0.1",
    packages=find_packages(include=["app", "app.*"]),
)
