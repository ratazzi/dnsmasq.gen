#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='dnsmasq.gen',
    version='0.1.0',
    author='ratazzi',
    author_email='ratazzi.potts@gmail.com',
    url='http://github.com/ratazzi/dnsmasq.gen',
    packages=find_packages(),
    description='dnsmasq.conf generator',
    entry_points={
        'console_scripts': [
            'dnsmasq.gen=dnsmasqgen.gen:main',
        ],
    },
    install_requires=[
        'dnspython',
        'pyyaml',
    ],
    include_package_data=True,
    license='BSD License',
)
