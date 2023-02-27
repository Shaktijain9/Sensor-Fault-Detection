from setuptools import find_packages, setup
from typing import List


def get_requirements() -> List[str]:
    pass


setup(
    name='sensor',
    version="0.0.1",
    author='Shakti Jain',
    author_email="shaktijain9806@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)
