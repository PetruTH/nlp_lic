from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

setup(
    name='dexonline',
    description='Spacy plugin working based on dexonline database',
    author='Cristea Petru-Theodor',
    version='0.0.1',
    author_email='petru.theodor@outlook.com',
    packages=['dexonlineplugin'],
    install_requires=[
        'spacy==3.7.2',
        'requests==2.31.0',
        'tqdm==4.66.1'
    ]
)