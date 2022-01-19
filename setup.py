#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    os.system('python3 setup.py sdist')
    os.system('twine upload dist/*')
    sys.exit()


def readme():
    with open('README.rst') as readme_file:
        return readme_file.read()


def find_version():
    with open('academic_tracker/__init__.py', 'r') as fd:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            fd.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


REQUIRES = [
    "docopt >= 0.6.2",
    "pymed >= 0.8.9",
    "jsonschema >= 3.0.1",
    "habanero >= 1.0.0",
    "orcid >= 1.0.3",
    "scholarly >= 1.4.5",
    "pdfplumber >= 0.5.28",
    "beautifulsoup4 >= 4.9.3",
    "fuzzywuzzy >= 0.18.0",
    "docx >= 0.2.4",
    "pandas >= 0.24.2"
]


setup(
    name='academic_tracker',
    version=find_version(),
    author='Travis Thompson',
    author_email='ptth222@gmail.com',
    description='Find publications on PubMed for given authors.',
    keywords='PubMed publications citations',
    license='BSD',
    url='https://github.com/MoseleyBioinformaticsLab/academic_tracker',
    packages=find_packages(),
    platforms=['any'],
    long_description=readme(),
    install_requires=REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Linux',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={"console_scripts": ["academic_tracker = academic_tracker.__main__:main"]},
)