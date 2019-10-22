#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

def get_cmdclass(needs_install):
    if needs_install:
        return {}
    return {
        'coverage': CustomCoverage,
    }


install_requires = read('requirements.txt').split()

needs_install = not os.path.isdir('build')

if not needs_install:
    from buildlib.custom_coverage import CustomCoverage

package_ignore = ['tests']

setup(
    name="BackupNanny",
    version="0.0.2",
    author="forwardline",
    author_email="",
    cmdclass=get_cmdclass(needs_install),
    description=('BackupNanny allows for backup/cleanup automation across AWS accounts and regions'),
    url="https://github.com/ForwardLine/backup-nanny",
    include_package_data=True,
    install_requires=install_requires,
    test_suite="nose.collector",
    tests_require=install_requires,
    long_description=read('README.md'),
    packages=find_packages(exclude=package_ignore),
    py_modules = ['deploy_nanny', 'buildlib'],
    entry_points='''
        [console_scripts]
        deploy_nanny=deploy_nanny:cli
    '''
)
