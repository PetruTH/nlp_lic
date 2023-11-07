from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

setup(
    name='dexonlineplugin',
    description='Spacy plugin working based on dexonline database',
    author='Cristea Petru-Theodor',
    version='0.0.1',
    author_email='petru.theodor@outlook.com',
    packages=find_packages(),
    install_requires=[
        'spacy'
    ],
    scripts=["download_jsons_data.py"]
)
