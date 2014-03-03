#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

setup(
    name = 'meetlogindex',
    version = '0.1',
    description = 'Short description',
    long_description = 'Long description',
    keywords = 'some, keywords',
    author = 'Honza Horak',
    author_email = 'hhorak@redhat.com',
    license = 'MIT',
    packages = find_packages(),
    entry_points={'console_scripts':['meetlogindex = meetlogindex.bin:main']},
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Build Tools',
                   'Topic :: System :: Software Distribution',
                  ]
)
