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
    with open('src/academic_tracker/__init__.py', 'r') as fd:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            fd.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


REQUIRES = [
    "docopt >= 0.6.2",
    "pymed >= 0.8.9",
    "jsonschema >= 4.4.0",
    "habanero >= 1.0.0",
    "orcid >= 1.0.3",
    "scholarly >= 1.4.5",
    "beautifulsoup4 >= 4.9.3",
    "fuzzywuzzy >= 0.18.0",
    "python-docx >= 0.8.11",
    "pandas >= 0.24.2",
    "openpyxl >= 2.6.2",
    "requests >= 2.21.0",
    "deepdiff >= 5.7.0"
]


setup(
    name='academic_tracker',
    version=find_version(),
    author='Travis Thompson',
    author_email='ptth222@gmail.com',
    description='Find publications on PubMed, Crossref, ORCID, and Google Scholar for given authors or references.',
    keywords='PubMed publications citations Crossref ORCID Google Scholar',
    license='BSD',
    url='https://github.com/MoseleyBioinformaticsLab/academic_tracker',
    packages=find_packages("src", exclude=['doc', 'docs', 'vignettes']),
    package_dir={'': 'src'},
    platforms=['any'],
    long_description=readme(),
    long_description_content_type="text/x-rst",
    install_requires=REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={"console_scripts": ["academic_tracker = academic_tracker.__main__:main"]},
)