from setuptools import setup, find_packages

setup(
    name="kafka_consumer",
    version="0.1",
    packages=find_packages(include=["consumer", "consumer.*"]),
    install_requires=[],
)
