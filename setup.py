from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

setup(
    name='nlp_lic',
    description='Spacy plugin working based on dexonline database',
    author='Cristea Petru-Theodor',
    version='0.0.1',
    author_email='petru.theodor@outlook.com',
    packages=['dexonlineplugin'],
    install_requires=[
        'spacy',
        'requests',
        'tqdm'
    ]
)