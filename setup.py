#!/usr/bin/env python

from distutils.core import setup


setup(name='Bacalhau',
      version = '1.0',
      author = 'Miguel Vieira',
      author_email = 'jose.m.vieira@kcl.ac.uk',
      url = 'https://github.com/kcl-ddh/bacalhau',
      packages = ['bacalhau', 'bacalhau.corpus', 'bacalhau.document'],
      scripts = ['scripts/bacalhau'],
      )
