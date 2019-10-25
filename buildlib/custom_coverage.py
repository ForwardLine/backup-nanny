#!/usr/bin/env python
from setuptools.command.install import install
import subprocess


class CustomCoverage(install):

    def run(self):
        install.run(self)
        subprocess.call('./buildlib/coverage')
