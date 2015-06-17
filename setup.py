#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requires = []

if sys.version_info < (3, 4, 0):
    requires += [
            'enum34'
    ]

setup(
    name='dns',
    version='0.1.0',
    description='Python DNS server / client',
    long_description=readme + '\n\n' + history,
    author='Thom Wiggers and Luuk Scholten',
    author_email='Thom@ThomWiggers.nl and info@luukscholten.com',
    url='https://github.com/thomwiggers/dns-python',
    packages=[
        'dns',
    ],
    package_dir={'dns':
                 'dns'},
    include_package_data=True,
    install_requires=requires,
    license="BSD",
    zip_safe=False,
    keywords='dns',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public Licence v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
