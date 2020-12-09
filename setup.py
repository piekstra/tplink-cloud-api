"""setup.py: setuptools control."""

from setuptools import setup, find_packages

__version__ = '1.0.2'

with open('README.md', 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='tplink-cloud-api',
    author='Dev Piekstra',
    author_email='piekstra.dev@gmail.com',
    packages=find_packages(),
    version=__version__,
    description='Python library for communicating with the TP-Link Cloud API to manage TP-Link Kasa Smart Home devices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'requests', 
        'pyyaml'
    ],
    url='https://github.com/piekstra/tplink-cloud-api',
    python_requires='>=3.6',
    zip_safe=False,
    license='GPL-3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)