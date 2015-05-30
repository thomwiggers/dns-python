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

setup(
    name='OneBot',
    version='0.1.0',
    description='Python reincarnation of OneBot',
    long_description=readme + '\n\n' + history,
    author='Thom Wiggers',
    author_email='Thom@ThomWiggers.nl',
    url='https://github.com/thomwiggers/OneBot',
    packages=[
        'OneBot',
    ],
    package_dir={'OneBot':
                 'OneBot'},
    include_package_data=True,
    install_requires=[
        'irc3'
    ],
    license="BSD",
    zip_safe=False,
    keywords='OneBot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public Licence v3 or later (GPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
