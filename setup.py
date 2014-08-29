#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of gandalf-client.
# https://github.com/rfloriano/gandalf-client

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com


from setuptools import setup, find_packages
from gandalf.version import __version__

tests_require = [
    'mock',
    'nose',
    'nose-focus',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
    'tornado',
    'cow-framework',
    'requests',
    'pycrypto==master',
    'sphinx_rtd_theme',
]

setup(
    name='gandalf-client',
    version=__version__,
    description='an incredible python package',
    long_description='''
an incredible python package
''',
    keywords='',
    author='Rafael Floriano da Silva',
    author_email='rflorianobr@gmail.com',
    url='https://github.com/rfloriano/gandalf-client',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[],
    extras_require={
        'tests': tests_require,
    },
    dependency_links=['https://github.com/dlitz/pycrypto/tarball/master#egg=pycrypto-master'],
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'gandalf-client=gandalf_client.cli:main',
        ],
    },
)
