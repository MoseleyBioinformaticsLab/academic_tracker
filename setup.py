#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages


def find_version():
    with open('stalker/__init__.py', 'r') as fd:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                            fd.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


REQUIRES = [
    "pymed"
]


setup(
    name='stalker',
    version=find_version(),
    author='Christian Powell',
    author_email='christian.david.powell@gamil.com',
    description='Find papers PIs have yet to report.',
    license='BSD',
    packages=find_packages(),
    platforms='any',
    install_requires=REQUIRES,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
