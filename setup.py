#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='warden',
    version='0.1',
    description='app for monitoring service availability',
    author='Ethan Haynes',
    install_requires=[
        'click'
    ],
    packages=find_packages(),
    scripts=['bin/warden']
)
