#!/usr/bin/env python2

from distutils.core import setup

setup(name='installkernel',
      version='1.0',
      description='program to install kernel',
      author='(cdep) illabout',
      author_email='cdep.illabout@gmail.com',
      #url='http://www.python.org/sigs/distutils-sig/',
      scripts=['src/installkernel'],
      data_files=[('etc/bash_completion.d', ['datafiles/bash_completion.d/installkernel'])], 
     )

