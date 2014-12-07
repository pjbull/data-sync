#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='data-sync-s3',
    version='0.0.1',
    description='Data Sync S3',
    author='Peter Bull',
    author_email='pjbull@gmail.com',
    url='http://www.drivendata.org/',
    license='MIT',
    packages=find_packages(),

    entry_points={
    'console_scripts': [
        'data-sync-s3=data_sync:main',
    ]},

    zip_safe=True,
)