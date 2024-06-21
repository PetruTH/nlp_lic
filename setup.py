from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        subprocess.check_call(['spacy', 'download', 'ro_core_news_sm'])

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='dexflex',
    description='Spacy plugin working based on dexonline database',
    author='Cristea Petru-Theodor',
    version='0.0.6',
    author_email='petru.theodor@outlook.com',
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['dexflex', 'dexflex.*']),
    install_requires=[
        'numpy==1.26.4',
        'requests==2.31.0',
        'mariadb',
        'feather-format',
        'zipp==3.17.0',
        'tqdm==4.66.1',
        'torch',
        'spacy==3.7.2',
        'transformers==4.36.2',
        'wordfreq'
    ],
)
