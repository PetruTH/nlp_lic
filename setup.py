from setuptools import setup, find_packages

setup(
    name='dexflex',
    description='Spacy plugin working based on dexonline database',
    author='Cristea Petru-Theodor',
    version='0.0.1',
    author_email='petru.theodor@outlook.com',
    packages=find_packages(include=['dexflex', 'dexflex.*']),
    install_requires=[
        'numpy==1.26.4',
        'requests==2.31.0',
        'mariadb',
        'zipp==3.17.0',
        'tqdm==4.66.1',
        'torch',
        'spacy==3.7.2',
        'transformers==4.36.2'
    ],
)
