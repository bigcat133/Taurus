#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='galaxy-taurus',
    version='0.2.0.4',
    description='An adaptation layer for libcloud, openstack, aliyun, ceph',
    keywords='Adapter, libCloud, openstack, aliyun',
    author='bigcat133',
    author_email='bigcat133@gmail.com',
    license='GNU Lesser General Public License',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'backports.ssl-match-hostname==3.5.0.1',
        'apache-libcloud==1.5.0',
        'python-cinderclient==1.11.0',
        'keystoneauth1==2.18.0',
        'python-novaclient==8.0.0',
        'aliyun-python-sdk-core==2.3.1',
    ],
)
