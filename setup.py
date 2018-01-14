#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import euchre


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

packages = [
    'euchre',
]

package_data = {
}

requires = [
]

classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Card Games :: Euchre',
]

setup(
    name='euchre',
    version=skeleton.__version__,
    description='game logic for playing card game euchre',
    long_description=readme,
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    author=skeleton.__author__,
    author_email='', #ToAdd
    url='', #ToADD
    license='MIT',
    classifiers=classifiers,
)